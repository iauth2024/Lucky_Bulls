import time
import logging
import sys
import io
from django.core.management.base import BaseCommand
from Lucky_Bulls.models import TradingAccount, MonitorControl, OrderMapping
from dhanhq import dhanhq
from django.db import transaction
from datetime import datetime, time as dt_time
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("monitor_orders.log", encoding='utf-8'),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Monitor orders and copy them with a multiplier from master to child accounts"

    def add_arguments(self, parser):
        parser.add_argument("--poll-interval", type=int, default=5,
                          help="Polling interval in seconds when market is open")
        parser.add_argument("--off-interval", type=int, default=3600,
                          help="Sleep interval in seconds when market is closed (1 hour)")
        parser.add_argument("--max-retries", type=int, default=3,
                          help="Maximum retries for failed API calls")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry_count = 0
        # Load processed orders from OrderMapping to persist across restarts
        self.processed_orders = set(
            OrderMapping.objects.values_list('master_order_id', flat=True)
        )
        self.order_mapping = {}
        
        # Fix Windows console encoding
        if sys.stdout.encoding != 'UTF-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    def is_market_open(self):
        """Check if market is open (9:15 AM to 3:30 PM, Monday to Friday)"""
        now = datetime.now()
        weekday = now.weekday()  # 0-4 = Monday-Friday
        current_time = now.time()
        
        market_open = dt_time(9, 15)
        market_close = dt_time(15, 30)
        
        return weekday < 5 and market_open <= current_time <= market_close

    def is_monitor_active(self):
        """Check if monitoring is enabled in database"""
        try:
            control = MonitorControl.objects.get(id=1)
            return control.is_active
        except MonitorControl.DoesNotExist:
            MonitorControl.objects.create(id=1, is_active=True)
            return True

    def get_dhan_client(self, account):
        """Initialize and return DhanHQ client with proper error handling"""
        try:
            return dhanhq(account.client_id, account.token)
        except Exception as e:
            logger.error("Failed to initialize Dhan client for %s: %s", account.name, str(e))
            return None

    def validate_order(self, order_details):
        """Validate order details before processing"""
        required_fields = ['securityId', 'exchangeSegment', 'transactionType',
                         'quantity', 'orderType', 'productType']
        
        for field in required_fields:
            if field not in order_details:
                logger.error("Missing required field in order: %s", field)
                return False
        
        try:
            if int(order_details['quantity']) <= 0:
                logger.error("Invalid quantity: %s", order_details['quantity'])
                return False
        except (ValueError, TypeError):
            logger.error("Quantity must be a positive integer: %s", order_details['quantity'])
            return False
            
        return True

    def get_holdings_data(self, dhan_client):
        """Get holdings data with proper field name handling"""
        try:
            holdings_response = dhan_client.get_holdings()
            if not isinstance(holdings_response, dict) or holdings_response.get('status') != 'success':
                logger.warning("Failed to get holdings: %s", holdings_response)
                return {}

            holdings_data = holdings_response.get('data', [])
            holdings = {}
            
            for h in holdings_data:
                symbol = h.get('tradingSymbol') or h.get('securityId') or h.get('symbol') or h.get('Symbol')
                quantity = h.get('quantity') or h.get('netQty') or h.get('totalQty') or h.get('Total Quantity')
                
                if symbol and quantity is not None:
                    holdings[symbol] = quantity
                    
            return holdings
            
        except Exception as e:
            logger.error("Error getting holdings data: %s", str(e))
            return {}

    def copy_order_to_child(self, master_order, child_account, multiplier=1):
        """Copy order to child account with multiplier applied"""
        if child_account.is_master:
            logger.warning("Attempted to copy order to master account %s, skipping", child_account.name)
            return None
        
        try:
            child_dhan = self.get_dhan_client(child_account)
            if not child_dhan:
                return None

            child_order = master_order.copy()
            # Convert multiplier to Decimal for consistent type handling
            multiplier = Decimal(str(multiplier)) if not isinstance(multiplier, Decimal) else multiplier
            
            child_order['quantity'] = int(Decimal(str(child_order['quantity'])) * multiplier)
            
            if not self.validate_order(child_order):
                return None

            order_params = {
                "security_id": child_order['securityId'],
                "exchange_segment": child_order['exchangeSegment'],
                "transaction_type": child_order['transactionType'],
                "quantity": child_order['quantity'],
                "order_type": child_order['orderType'],
                "product_type": child_order['productType'],
                "price": child_order.get('price', 0),
                "trigger_price": child_order.get('triggerPrice', 0),
                "validity": child_order.get('validity', 'DAY'),
                "after_market_order": not self.is_market_open()
            }

            response = child_dhan.place_order(**order_params)
            if response.get('status') == 'success':
                logger.info("Order copied to %s (Qty: %s)", child_account.name, child_order['quantity'])
                return response['data']['orderId']
            else:
                logger.error("Failed to copy order to %s: %s", 
                           child_account.name, response.get('remarks', 'Unknown error'))
                return None

        except Exception as e:
            logger.error("Error copying order to %s: %s", child_account.name, str(e))
            return None

    def process_master_orders(self, master_dhan, master_account, child_accounts):
        """Fetch and process orders from master account"""
        try:
            orders_response = master_dhan.get_order_list()
            if not isinstance(orders_response, dict) or orders_response.get('status') != 'success':
                logger.warning("Failed to fetch orders: %s", orders_response.get('remarks', 'Unknown error'))
                return

            logger.info("Fetched %s orders from master account", len(orders_response.get('data', [])))
            master_holdings = self.get_holdings_data(master_dhan)

            for order in orders_response.get('data', []):
                try:
                    if not all(key in order for key in ['orderId', 'securityId', 'transactionType', 'quantity']):
                        logger.warning("Skipping order with missing required fields: %s", order)
                        continue

                    order_id = order['orderId']
                    if order_id in self.processed_orders:
                        logger.info("Skipping already processed order: %s", order_id)
                        continue
                        
                    if order.get('orderStatus') != 'PENDING':
                        logger.info("Skipping non-pending order %s with status %s", 
                                  order_id, order.get('orderStatus'))
                        continue

                    logger.info("Processing new order: %s", order_id)
                    if order['transactionType'] == 'SELL':
                        symbol = order.get('tradingSymbol') or order.get('securityId')
                        if symbol not in master_holdings:
                            logger.info("Skipping sell order - No holding for %s", symbol)
                            continue

                    for child in child_accounts:
                        if child.id == master_account.id:
                            logger.warning("Skipping master account %s as child", child.name)
                            continue
                        if OrderMapping.objects.filter(
                            master_order_id=order_id,
                            child_client_id=child.client_id
                        ).exists():
                            logger.info("Order %s already copied to child %s", order_id, child.name)
                            continue

                        if order['transactionType'] == 'SELL':
                            child_holdings = self.get_holdings_data(self.get_dhan_client(child))
                            symbol = order.get('tradingSymbol') or order.get('securityId')
                            if symbol not in child_holdings:
                                logger.info("Skipping sell order for %s - No holding", child.name)
                                continue

                        logger.debug("Attempting to copy order %s to child %s with multiplier %s (type: %s)", 
                                    order_id, child.name, child.multiplier, type(child.multiplier))
                        
                        copied_order_id = self.copy_order_to_child(
                            order, 
                            child, 
                            multiplier=child.multiplier
                        )
                        
                        if copied_order_id:
                            # Mark as processed to prevent reprocessing, even if OrderMapping fails
                            self.processed_orders.add(order_id)
                            logger.info("Marked order %s as processed after copy to %s", order_id, child.name)
                            
                            try:
                                # Convert multiplier to Decimal for OrderMapping
                                multiplier = Decimal(str(child.multiplier))
                                OrderMapping.objects.create(
                                    master_order_id=order_id,
                                    child_client_id=child.client_id,
                                    child_order_id=copied_order_id,
                                    multiplier=multiplier,
                                    original_quantity=int(order['quantity']),
                                    remaining_quantity=int(Decimal(str(order['quantity'])) * multiplier)
                                )
                                logger.info("Successfully created OrderMapping for order %s to child %s", 
                                           order_id, child.name)
                            except Exception as e:
                                logger.error("Failed to create OrderMapping for order %s to child %s: %s", 
                                            order_id, child.name, str(e))
                                continue

                except Exception as e:
                    logger.error("Error processing order %s: %s", order.get('orderId', 'unknown'), str(e))

        except Exception as e:
            logger.error("Error processing master orders: %s", str(e))

    def handle(self, *args, **options):
        self.poll_interval = options['poll_interval']
        self.off_interval = options['off_interval']
        self.max_retries = options['max_retries']
        
        logger.info("Starting order monitor (Poll: %ss, Off: %ss)", self.poll_interval, self.off_interval)

        while True:
            try:
                if not self.is_monitor_active():
                    logger.info("Monitoring paused. Sleeping for %ss", self.off_interval)
                    time.sleep(self.off_interval)
                    continue

                if not self.is_market_open():
                    logger.info("Market closed. Sleeping for %ss", self.poll_interval)
                    time.sleep(self.poll_interval)
                    continue

                with transaction.atomic():
                    master_account = TradingAccount.objects.select_for_update().filter(
                        is_master=True
                    ).first()
                    
                    if not master_account:
                        logger.error("No master account found")
                        time.sleep(self.poll_interval)
                        continue

                    child_accounts = list(TradingAccount.objects.filter(
                        is_child=True, 
                        parent_account=master_account
                    ).exclude(id=master_account.id))
                    logger.info("Master account: %s, Child accounts: %s", 
                               master_account.name if master_account else "None", 
                               [child.name for child in child_accounts])

                    master_dhan = self.get_dhan_client(master_account)
                    if not master_dhan:
                        time.sleep(self.poll_interval)
                        continue

                    self.process_master_orders(master_dhan, master_account, child_accounts)
                    self.retry_count = 0

            except Exception as e:
                self.retry_count += 1
                logger.error("Critical error (Retry %s/%s): %s", 
                           self.retry_count, self.max_retries, str(e))
                
                if self.retry_count >= self.max_retries:
                    logger.error("Max retries reached. Exiting...")
                    break
                
                time.sleep(min(60, self.poll_interval * self.retry_count))

            time.sleep(self.poll_interval)