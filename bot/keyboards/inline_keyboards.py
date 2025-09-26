from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from backend.vpn.models import Tariff
from bot.utils.db import get_support_link

from .callbacks import (
    BroadcastAdminCallback,
    ConnectCallback,
    MenuCallback,
    NotificationCallback,
    PaymentCallback,
    TariffCallback,
)


async def get_main_menu_kb(user_id: int, bot_username: str):
    support_link = await get_support_link()
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🕶 Подписка", callback_data=MenuCallback(action="subscription").pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❗️Подключить", callback_data=MenuCallback(action="connect").pack()
        )
    )
    builder.row(InlineKeyboardButton(text="🚁 Поддержка", url=support_link))
    builder.row(
        InlineKeyboardButton(
            text="⚡️ Заработать", callback_data=MenuCallback(action="earn").pack()
        )
    )
    return builder.as_markup()


def get_tariffs_kb(tariffs: list[Tariff]):
    builder = InlineKeyboardBuilder()
    buttons = []
    for tariff in tariffs:
        buttons.append(
            InlineKeyboardButton(
                text=f"{tariff.duration_days} дней {int(tariff.price)}₽",
                callback_data=TariffCallback(id=tariff.id).pack(),
            )
        )
    builder.row(*buttons, width=2)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад", callback_data=MenuCallback(action="main_menu").pack()
        )
    )
    return builder.as_markup()


def get_payment_kb(confirmation_url: str, payment_id_provider: str, tariff_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Оплатить", url=confirmation_url)
    builder.button(
        text="💳 Подтвердить",
        callback_data=PaymentCallback(
            payment_id=payment_id_provider, tariff_id=tariff_id
        ).pack(),
    )
    builder.button(
        text="⬅️ Назад", callback_data=MenuCallback(action="subscription").pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def get_connection_options_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="iPhone", callback_data="connect:iphone")
    builder.button(text="MacOS", callback_data="connect:macos")
    builder.button(text="Android", callback_data="connect:android")
    builder.button(text="Windows", callback_data="connect:windows")
    builder.button(
        text="⬅️ Назад", callback_data=MenuCallback(action="main_menu").pack()
    )
    builder.adjust(2)
    return builder.as_markup()


def get_dismiss_kb(text: str = "Отлично"):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=text, callback_data=NotificationCallback(action="dismiss").pack()
    )
    return builder.as_markup()


def get_subscription_reminder_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Подписка", callback_data=MenuCallback(action="subscription").pack()
    )
    builder.button(
        text="Отклонить", callback_data=NotificationCallback(action="dismiss").pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def get_earn_kb(referral_link: str):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📲 Отправить",
            url=referral_link,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuCallback(action="main_menu").pack(),
        )
    )
    return builder.as_markup()


def get_device_selection_kb():
    builder = InlineKeyboardBuilder()
    devices = {
        "iPhone": "iphone",
        "MacOS": "macos",
        "Android": "android",
        "Windows": "windows",
    }

    buttons = [
        InlineKeyboardButton(
            text=name,
            callback_data=ConnectCallback(device=code, action="select").pack(),
        )
        for name, code in devices.items()
    ]
    builder.row(*buttons, width=2)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад", callback_data=MenuCallback(action="main_menu").pack()
        )
    )
    return builder.as_markup()


def get_connection_details_kb(
    device: str, vless_link: str, show_key: bool, show_instruction: bool
):
    builder = InlineKeyboardBuilder()

    app_links = {
        "iphone": "https://apps.apple.com/ru/app/streisand/id6450534064",
        "macos": "https://apps.apple.com/ru/app/streisand/id6450534064",
        "android": "https://play.google.com/store/apps/details?id=com.v2raytun.android",
        "windows": "https://storage.v2raytun.com/v2RayTun_Setup.exe",
    }

    if show_instruction:
        builder.button(
            text="Скрыть",
            callback_data=ConnectCallback(
                device=device,
                action="toggle_instruction",
                show_key=int(show_key),
                show_instruction=0,
            ).pack(),
        )
    else:
        builder.button(
            text="Инструкция",
            callback_data=ConnectCallback(
                device=device,
                action="toggle_instruction",
                show_key=int(show_key),
                show_instruction=1,
            ).pack(),
        )

    builder.button(text="Приложение", url=app_links.get(device, "#"))

    if show_key:
        builder.button(
            text="Скрыть",
            callback_data=ConnectCallback(
                device=device, action="toggle_key", show_key=0
            ).pack(),
        )
    else:
        builder.button(
            text="Подключить",
            callback_data=ConnectCallback(
                device=device, action="toggle_key", show_key=1
            ).pack(),
        )

    builder.button(text="⬅️ Назад", callback_data=MenuCallback(action="connect").pack())

    builder.adjust(1, 2, 1)
    return builder.as_markup()


def get_go_to_subscription_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🕶 Подписка", callback_data=MenuCallback(action="subscription").pack()
    )
    builder.button(text="⬅️ Назад", callback_data=MenuCallback(action="connect").pack())
    builder.adjust(1)
    return builder.as_markup()


def get_broadcast_approval_kb(broadcast_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Отправить всем",
        callback_data=BroadcastAdminCallback(
            action="approve", broadcast_id=broadcast_id
        ).pack(),
    )
    builder.button(
        text="❌ Отклонить",
        callback_data=BroadcastAdminCallback(
            action="decline", broadcast_id=broadcast_id
        ).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()
