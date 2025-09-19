from celery import shared_task

from backend.vpn.models import Subscription
from backend.vpn.services import VpnService


@shared_task
def ensure_vpn_client_active_task(subscription_id: int):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        service = VpnService()
        success = service.ensure_client_is_active(subscription)
        if success:
            subscription.is_vpn_client_active = True
            subscription.save(update_fields=["is_vpn_client_active"])
    except Subscription.DoesNotExist:
        pass


@shared_task
def deactivate_vpn_client_task(subscription_id: int):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        service = VpnService()
        service.disable_client(subscription=subscription)
    except Subscription.DoesNotExist:
        pass
