from django.contrib import admin
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.utils import timezone

from backend.payments.models import Payment
from backend.users.models import User
from backend.vpn.models import Subscription

from .models import ProjectStats


@admin.register(ProjectStats)
class ProjectStatsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        total_users = User.objects.count()

        total_referrals = User.objects.filter(referred_by__isnull=False).count()

        total_revenue = (
            Payment.objects.filter(status=Payment.Status.SUCCEEDED).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        active_subscription_user_ids = Subscription.objects.filter(
            end_date__gt=timezone.now()
        ).values_list("user_id", flat=True)

        paid_subscription_users = (
            User.objects.filter(
                telegram_id__in=active_subscription_user_ids,
                payments__status=Payment.Status.SUCCEEDED,
            )
            .distinct()
            .count()
        )

        ref_subscription_users = (
            User.objects.filter(telegram_id__in=active_subscription_user_ids)
            .exclude(payments__status=Payment.Status.SUCCEEDED)
            .count()
        )

        total_active_subscriptions = len(active_subscription_user_ids)

        no_subscription_users = total_users - total_active_subscriptions

        context = {
            **self.admin_site.each_context(request),
            "company_name": "KEDO VPN",
            "total_users": total_users,
            "total_referrals": total_referrals,
            "paid_subscription_users": paid_subscription_users,
            "ref_subscription_users": ref_subscription_users,
            "no_subscription_users": no_subscription_users,
            "total_revenue": f"{int(total_revenue)} ₽",
        }

        request.current_app = self.admin_site.name
        return TemplateResponse(request, "admin/project_stats_dashboard.html", context)
