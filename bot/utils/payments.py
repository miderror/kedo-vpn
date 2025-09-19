import os
import uuid
from typing import Optional, Tuple

from yookassa import Configuration, Payment

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


async def create_yookassa_payment(
    amount: float, description: str, return_url: str
) -> Optional[Tuple[str, str]]:
    try:
        idempotence_key = str(uuid.uuid4())
        receipt = {
            "items": [
                {
                    "description": description,
                    "quantity": 1,
                    "amount": {"value": str(amount), "currency": "RUB"},
                    "vat_code": 1,
                    "payment_mode": "full_payment",
                    "payment_subject": "commodity",
                }
            ],
            "email": "example@example.com",
            "tax_system": 1,
        }

        payment = Payment.create(
            {
                "amount": {"value": str(amount), "currency": "RUB"},
                "confirmation": {"type": "redirect", "return_url": return_url},
                "capture": True,
                "description": description,
                "receipt": receipt,
            },
            idempotence_key,
        )
        return payment.confirmation.confirmation_url, payment.id
    except Exception as e:
        print(f"Ошибка создания платежа в ЮKassa: {e}")
        return None


async def check_yookassa_payment(payment_id: str) -> bool:
    try:
        payment = Payment.find_one(payment_id)
        return payment.status == "succeeded"
    except Exception as e:
        print(f"Ошибка проверки платежа {payment_id} в ЮKassa: {e}")
        return False
