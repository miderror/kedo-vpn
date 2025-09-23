from aiogram.filters.callback_data import CallbackData


class MenuCallback(CallbackData, prefix="menu"):
    action: str


class TariffCallback(CallbackData, prefix="tariff"):
    id: int


class PaymentCallback(CallbackData, prefix="payment"):
    payment_id: str
    tariff_id: int


class NotificationCallback(CallbackData, prefix="notify"):
    action: str


class ConnectCallback(CallbackData, prefix="connect"):
    device: str
    action: str
    show_key: int = 0
    show_instruction: int = 0


class BroadcastAdminCallback(CallbackData, prefix="bcast_admin"):
    action: str
    broadcast_id: int
