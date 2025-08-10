import time
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command
from Lucky_Bulls.models import MonitorControl

# Setup logger
logger = logging.getLogger("monitor_worker")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("monitor_worker.log")
console = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
console.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console)

class Command(BaseCommand):
    help = 'Runs alerts and copy trading monitors based on toggle states.'

    def handle(self, *args, **options):
        logger.info("🔁 Monitor Worker Started.")

        while True:
            try:
                self.run_if_enabled("alerts", "send_alerts", "🔔 Alerts Monitor Running...")
                self.run_if_enabled("copy_trading", "monitor_orders", "📈 Copy Trading Monitor Running...")
            except Exception as e:
                logger.exception(f"❌ Unexpected error in monitor loop: {e}")

            time.sleep(60)  # wait before checking again

    def run_if_enabled(self, monitor_type, command_name, log_message):
        is_active = self.get_monitor_status(monitor_type)
        if is_active:
            logger.info(log_message)
            try:
                call_command(command_name)
            except Exception as e:
                logger.error(f"🚨 Failed running {command_name}: {e}")
        else:
            logger.info(f"⏸️ {monitor_type.replace('_', ' ').title()} Monitor Disabled")

    def get_monitor_status(self, monitor_type):
        control, _ = MonitorControl.objects.get_or_create(monitor_type=monitor_type, defaults={'is_active': False})
        return control.is_active
