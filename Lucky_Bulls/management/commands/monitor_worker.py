from django.core.management.base import BaseCommand
from your_app.models import MonitorControl
import time

class Command(BaseCommand):
    help = 'Background worker for handling alerts and copy trading based on toggles.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🔁 Monitor Worker Started..."))

        while True:
            try:
                self.run_alerts_if_enabled()
                self.run_copy_trading_if_enabled()

                # Wait for 1 minute before next check
                time.sleep(60)

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Error: {e}"))
                time.sleep(10)  # Retry after 10s

    def is_enabled(self, monitor_type):
        try:
            toggle = MonitorControl.objects.get(monitor_type=monitor_type)
            return toggle.is_active
        except MonitorControl.DoesNotExist:
            return False

    def run_alerts_if_enabled(self):
        if self.is_enabled("alerts"):
            self.stdout.write("🔔 Alerts Monitor Running...")
            # Add your alert logic here
        else:
            self.stdout.write("🔕 Alerts Monitor Disabled")

    def run_copy_trading_if_enabled(self):
        if self.is_enabled("copy_trading"):
            self.stdout.write("📈 Copy Trading Monitor Running...")
            # Add your copy trading logic here
        else:
            self.stdout.write("📉 Copy Trading Monitor Disabled")
