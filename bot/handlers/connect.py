from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from django.conf import settings
from django.utils import timezone

from backend.vpn.models import Subscription
from bot.keyboards.callbacks import ConnectCallback, MenuCallback
from bot.keyboards.inline_keyboards import (
    get_connection_details_kb,
    get_device_selection_kb,
    get_go_to_subscription_kb,
)
from bot.utils.db import (
    activate_trial_subscription,
    get_bot_texts,
)

router = Router()


def get_vless_link(subscription: Subscription) -> str:
    params = settings.VLESS_LINK_PARAMS
    user_id = subscription.user.telegram_id
    uuid = subscription.vless_uuid

    return (
        f"vless://{uuid}@{params['host']}:{params['port']}?type=tcp&encryption=none&security=reality"
        f"&pbk={params['pbk']}&fp=chrome&sni={params['sni']}&sid={params['sid']}"
        f"&spx=%2F#KEDOVPN-{user_id}"
    )


@router.callback_query(MenuCallback.filter(F.action == "connect"))
async def select_device_handler(callback: CallbackQuery):
    texts = await get_bot_texts()
    text = texts.connect_select_device
    await callback.message.edit_text(text, reply_markup=get_device_selection_kb())
    await callback.answer()


async def show_connection_details(
    callback: CallbackQuery,
    subscription: Subscription,
    device: str,
    show_key: bool,
    show_instruction: bool,
):
    vless_link = get_vless_link(subscription)
    texts = await get_bot_texts()

    device_instructions = {
        "android": texts.connect_instruction_android,
        "iphone": texts.connect_instruction_iphone,
        "macos": texts.connect_instruction_macos,
        "windows": texts.connect_instruction_windows,
    }

    if show_instruction:
        text = device_instructions.get(device, "Инструкция не найдена.")
    else:
        text = texts.connect_base_instruction

    if show_key:
        text = text.replace(
            "✅Подключить", f"✅Подключить\n\n<code>{vless_link}</code>"
        )

    keyboard = get_connection_details_kb(device, vless_link, show_key, show_instruction)
    await callback.message.edit_text(
        text, reply_markup=keyboard, parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(ConnectCallback.filter())
async def connection_actions_handler(
    callback: CallbackQuery, callback_data: ConnectCallback, subscription: Subscription
):
    if subscription.trial_activated and subscription.end_date <= timezone.now():
        texts = await get_bot_texts()
        await callback.message.edit_text(
            texts.connect_need_subscription,
            reply_markup=get_go_to_subscription_kb(),
        )
        await callback.answer()
        return

    if not subscription.trial_activated and callback_data.action == "select":
        await activate_trial_subscription(subscription.id)

    show_key_flag = bool(callback_data.show_key)
    show_instruction_flag = bool(callback_data.show_instruction)

    if callback_data.action == "toggle_key":
        show_instruction_flag = False

    if callback_data.action == "toggle_instruction":
        show_key_flag = False

    await show_connection_details(
        callback=callback,
        subscription=subscription,
        device=callback_data.device,
        show_key=show_key_flag,
        show_instruction=show_instruction_flag,
    )
