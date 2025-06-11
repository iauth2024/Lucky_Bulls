from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from django.http import HttpRequest

class IPRestrictedBackend(ModelBackend):
    def authenticate(self, request: HttpRequest, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user:
            user_ip = request.META.get('REMOTE_ADDR', '')
            # Iterate through all TradingAccounts related to the user
            trading_accounts = getattr(user, 'tradingaccounts', None)
            if trading_accounts:
                for account in trading_accounts.all():
                    if account.restrict_login:
                        allowed_ips = account.allowed_ips or []
                        if user_ip not in allowed_ips and not getattr(settings, 'ALLOW_LOGIN_FROM_ANYWHERE', False):
                            return None
        return user
