import logging

from django.conf import settings
from py3xui import Api, Client

from backend.vpn.models import Subscription

logger = logging.getLogger(__name__)


class VpnService:
    def __init__(self):
        xui_cfg = settings.XUI_SETTINGS
        try:
            self.api = Api(
                host=xui_cfg["url"],
                username=xui_cfg["username"],
                password=xui_cfg["password"],
            )
            self.api.login()
        except Exception as e:
            logger.error(f"[VpnService] Failed to connect to 3x-ui: {e}")
            self.api = None

    def create_client(self, subscription: Subscription) -> bool:
        if not self.api:
            logger.error("[VpnService] API is not initialized")
            return False

        try:
            email = str(subscription.user.telegram_id)
            client_uuid = str(subscription.vless_uuid)
            inbound_id = settings.XUI_SETTINGS["inbound_id"]

            new_client = Client(id=client_uuid, email=email, enable=True)
            self.api.client.add(inbound_id, [new_client])

            logger.info(f"Created new VPN client for user {email}")
            return True
        except Exception as e:
            logger.error(
                f"[VpnService] Failed to create client for user {subscription.user.telegram_id}: {e}"
            )
            return False

    def disable_client(self, subscription: Subscription) -> bool:
        if not self.api:
            logger.error("[VpnService] API is not initialized")
            return False

        try:
            email = str(subscription.user.telegram_id)
            client_uuid = str(subscription.vless_uuid)

            client_to_update = self.api.client.get_by_email(email)
            client_to_update.id = client_uuid
            client_to_update.enable = False

            self.api.client.update(client_uuid, client_to_update)

            logger.info(f"Disabled VPN client for user {email}")
            return True
        except Exception as e:
            logger.error(
                f"[VpnService] Failed to disable client for user {subscription.user.telegram_id}: {e}"
            )
            return False

    def ensure_client_is_active(self, subscription: Subscription) -> bool:
        if not self.api:
            logger.error("[VpnService] API is not initialized")
            return False

        try:
            email = str(subscription.user.telegram_id)
            client_uuid = str(subscription.vless_uuid)

            client_to_update = self.api.client.get_by_email(email)
            if not client_to_update:
                logger.info(
                    f"VPN client for user {email} not found. Creating a new one."
                )
                return self.create_client(subscription)

            client_to_update.id = client_uuid
            client_to_update.enable = True

            self.api.client.update(client_uuid, client_to_update)

            logger.info(f"Re-enabled existing VPN client for user {email}")
            return True
        except Exception as e:
            logger.error(
                f"[VpnService] Failed to ensure client is active for user {email}: {e}"
            )
            return False
