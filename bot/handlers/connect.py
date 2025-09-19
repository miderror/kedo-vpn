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
)

router = Router()

DEVICE_INSTRUCTIONS = {
    "android": "➡️ Здравствуйте, Вы находитесь в разделе Подключить, тем самым активировали VPN данного устройства, этот раздел поможет Вам подключить VPN к Android. Для начала нажмите кнопку Приложение, которое Вас перенаправит на страницу прокси-клиента. Скачайте и установите приложение v2RayTun.\n\n➡️ Далее нажмите кнопку Подключить и скопируйте одним нажатием конфигурацию, которую необходимо добавить в v2RayTun. Дайте разрешение на получение уведомлений. Теперь справа вверху приложения нажмите на плюс и выберите: Импорт из буфера обмена и ваша конфигурация добавится в прокси-клиент и теперь VPN к работе готов.\n\n➡️ Так же хотел напомнить о реферальной программе. Если Вам понравится Kedo VPN, свободно делитесь приложением через кнопку Поделиться в Главном меню и получайте по 50 бонусных дней за каждого пользователя бесплатно.",
    "iphone": "➡️ Здравствуйте, Вы находитесь в разделе Подключить, тем самым активировали VPN данного устройства, этот раздел поможет Вам подключить VPN к iPhone. Для начала нажмите кнопку Приложение, которое Вас перенаправит на страницу прокси-клиента. Скачайте и установите приложение Streisand.\n\n➡️ Далее нажмите кнопку Подключить и скопируйте одним нажатием конфигурацию, которую необходимо добавить в Streisand. Теперь справа вверху Streisand нажмите на плюс и выберите: Добавить из буфера, дайте разрешение на вставку и ваша конфигурация добавится в прокси-клиент и теперь VPN к работе готов.\n\n➡️ Так же хотел напомнить о реферальной программе. Если Вам понравится Kedo VPN, свободно делитесь приложением через кнопку Поделиться в Главном меню и получайте по 50 бонусных дней за каждого пользователя бесплатно.",
    "macos": "➡️ Здравствуйте, Вы находитесь в разделе Подключить, тем самым активировали VPN данного устройства, этот раздел поможет Вам подключить VPN к MacOS. Для начала нажмите кнопку Приложение, которое Вас перенаправит на страницу прокси-клиента. Скачайте и установите приложение Streisand.\n\n➡️ Далее нажмите кнопку Подключить и скопируйте одним нажатием конфигурацию, которую необходимо добавить в Streisand. Запустите Streisand, нажмите на плюс в правом верхнем углу и выбираем: Добавить из буфера обмена и нажимаем Подключить и теперь VPN к работе готов.\n\n➡️ Так же хотел напомнить о реферальной программе. Если Вам понравится Kedo VPN, свободно делитесь приложением через кнопку Поделиться в Главном меню и получайте по 50 бонусных дней за каждого пользователя бесплатно.",
    "windows": "➡️ Здравствуйте, Вы находитесь в разделе Подключить, тем самым активировали VPN данного устройства, этот раздел поможет Вам подключить VPN к Windows. Для начала нажмите кнопку Приложение, которое скачает Вам прокси-клиент в папку «Загрузки». Установите приложение v2RayTun.\n\n➡️ Далее нажмите кнопку Подключить и скопируйте одним нажатием конфигурацию, которую необходимо добавить в v2RayTun. Запустите v2RayTun, нажмите на плюс в правом верхнем углу и выбираем: Импорт из буфера обмена и нажимаем Подключить и теперь VPN к работе готов.\n\n➡️ Так же хотел напомнить о реферальной программе. Если Вам понравится Kedo VPN, свободно делитесь приложением через кнопку Поделиться в Главном меню и получайте по 50 бонусных дней за каждого пользователя бесплатно.",
}


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
    text = "Выберите ваше устройство"
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

    if show_instruction:
        text = DEVICE_INSTRUCTIONS.get(device, "Инструкция не найдена.")
    else:
        text = (
            "➡️ VPN активирован! Осталось 3 шага:\n\n"
            "1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n"
            "2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>\n\n"
            "3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>"
        )

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
        await callback.message.edit_text(
            "Для активации выбранного Вами устройства необходима подписка",
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
