from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from bot.utils.payments import check_yookassa_payment, create_yookassa_payment

from backend.users.models import User
from bot.keyboards.callbacks import MenuCallback, PaymentCallback, TariffCallback
from bot.keyboards.inline_keyboards import get_payment_kb, get_tariffs_kb
from bot.utils.db import (
    create_payment_record,
    get_active_tariffs,
    get_pending_payment,
    get_tariff_by_id,
    process_successful_payment,
)

router = Router()


@router.callback_query(MenuCallback.filter(F.action == "subscription"))
async def subscription_handler(callback: CallbackQuery):
    tariffs = await get_active_tariffs()

    if not tariffs:
        await callback.answer(
            "На данный момент нет доступных тарифов.", show_alert=True
        )
        return

    text = "Выберите профиль оплаты"
    keyboard = get_tariffs_kb(tariffs)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(TariffCallback.filter())
async def select_tariff_handler(
    callback: CallbackQuery, callback_data: TariffCallback, user: User, bot: Bot
):
    tariff = await get_tariff_by_id(callback_data.id)
    if not tariff:
        await callback.answer("Тариф не найден.", show_alert=True)
        return

    bot_info = await bot.get_me()
    return_url = f"https://t.me/{bot_info.username}"
    description = f"Оплата подписки на {tariff.duration_days} дней"

    payment_info = await create_yookassa_payment(
        amount=tariff.price, description=description, return_url=return_url
    )

    if not payment_info:
        await callback.answer(
            "Не удалось создать ссылку на оплату. Попробуйте позже.", show_alert=True
        )
        return

    confirmation_url, payment_id_provider = payment_info

    await create_payment_record(user, tariff, payment_id_provider)

    text = f"Оплата {tariff.duration_days} дней составит {int(tariff.price)} рублей!\n\nПосле оплаты нажмите Подтвердить!"
    keyboard = get_payment_kb(confirmation_url, payment_id_provider, tariff.id)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(PaymentCallback.filter())
async def check_payment_handler(
    callback: CallbackQuery, callback_data: PaymentCallback
):
    await callback.answer("Проверяем оплату...")

    payment_id_provider = callback_data.payment_id

    is_successful = await check_yookassa_payment(payment_id_provider)

    if not is_successful:
        return

    payment = await get_pending_payment(payment_id_provider)
    if not payment:
        await callback.message.answer("Эта оплата уже была зачислена.")
        return

    await process_successful_payment(payment)

    await subscription_handler(callback)

    await callback.message.answer(
        f"✅ Оплата прошла успешно! Ваша подписка продлена на {payment.tariff.duration_days} дней."
    )
