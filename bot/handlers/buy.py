from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from lib.tron.router import SunSwapRouter
from lib.tron.client import get_tron_client
from db.models.user import get_or_create_user
from db.models.trade import create_trade
from workers.queue import enqueue_trade
import logging

logger = logging.getLogger(__name__)
router = Router()

class BuyState(StatesGroup):
    awaiting_token = State()
    awaiting_amount = State()
    awaiting_slippage = State()
    awaiting_confirmation = State()

@router.message(F.text.startswith("/buy"))
async def cmd_buy(message: Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) >= 2:
        await state.update_data(token=parts[1])
        if len(parts) >= 3:
            await state.update_data(amount=parts[2])
            if len(parts) >= 4:
                await state.update_data(slippage=parts[3])
                await confirm_trade(message, state)
                return
            else:
                await message.answer("📉 Enter max slippage (%):")
                await state.set_state(BuyState.awaiting_slippage)
        else:
            await message.answer("💰 Enter amount in TRX:")
            await state.set_state(BuyState.awaiting_amount)
    else:
        await message.answer("🪙 Enter token contract address:")
        await state.set_state(BuyState.awaiting_token)

@router.message(BuyState.awaiting_token)
async def process_token(message: Message, state: FSMContext):
    await state.update_data(token=message.text.strip())
    await message.answer("💰 Enter amount in TRX:")
    await state.set_state(BuyState.awaiting_amount)

@router.message(BuyState.awaiting_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
        await state.update_data(amount=amount)
        await message.answer("📉 Enter max slippage (%):")
        await state.set_state(BuyState.awaiting_slippage)
    except:
        await message.answer("❌ Invalid number. Try again:")

@router.message(BuyState.awaiting_slippage)
async def process_slippage(message: Message, state: FSMContext):
    try:
        slippage = float(message.text)
        if not (0 < slippage <= 50):
            raise ValueError
        await state.update_data(slippage=slippage)
        await confirm_trade(message, state)
    except:
        await message.answer("❌ Slippage must be 0.1–50. Try again:")

async def confirm_trade(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    amount = data["amount"]
    slippage = data["slippage"]

    # Get quote
    tron = get_tron_client()
    router = SunSwapRouter(tron)
    try:
        amounts = await router.get_amounts_out(
            int(amount * 1_000_000), [router.WTRX_ADDRESS, token]
        )
        est_out = amounts[-1]
        min_out = int(est_out * (1 - slippage / 100))

        await state.update_data(
            est_out=est_out,
            min_out=min_out,
            deadline_sec=1200,
        )

        await message.answer(
            f"📌 Quote for {amount} TRX → {token}:\n"
            f"→ Estimated output: {est_out / 1e6:,.2f} tokens\n"
            f"→ Min output (with {slippage}% slippage): {min_out / 1e6:,.2f}\n\n"
            f"✅ Confirm? (Yes/No)"
        )
        await state.set_state(BuyState.awaiting_confirmation)
    except Exception as e:
        logger.exception("Quote failed")
        await message.answer(f"❌ Quote error: {e}")
        await state.clear()

@router.message(BuyState.awaiting_confirmation)
async def process_confirmation(message: Message, state: FSMContext):
    if message.text.lower() not in ["yes", "y"]:
        await message.answer("❌ Trade cancelled.")
        await state.clear()
        return

    data = await state.get_data()
    user = await get_or_create_user(message.from_user.id)

    # Create trade record (pending)
    trade = await create_trade(
        user_id=user.telegram_id,
        token_address=data["token"],
        direction="BUY",
        amount_in=data["amount"],
        min_out_tokens=data["min_out"],
        status="pending",
    )

    # Enqueue
    job_id = await enqueue_trade(trade.id)
    await message.answer(
        f"🚀 Trade enqueued (Job ID: `{job_id}`).\n"
        "Worker will execute shortly…"
    )
    await state.clear()
