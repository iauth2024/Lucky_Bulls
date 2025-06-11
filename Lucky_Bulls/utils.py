# Lucky_Bulls/utils.py
import logging
from unittest.mock import Mock


# Mock requests module
requests = Mock()

def mock_get(url, headers):
    if 'orders' in url:
        return Mock(status_code=200, json=lambda: mock_orders.pop(0) if mock_orders else [])
    return Mock(status_code=500)

def mock_post(url, headers, json):
    return Mock(status_code=200, json=lambda: {'orderId': f"child_{json['quantity']}"})

requests.get = mock_get
requests.post = mock_post

# Step 1: Retrieve orders from the master account
def get_master_orders(master_account):
    url = 'https://api.dhan.co/v2/orders'
    headers = {'Content-Type': 'application/json', 'access-token': master_account.token}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Failed to retrieve orders from master account {master_account.name}: {e}")
        return []

# Step 2: Filter valid orders
def filter_orders(orders):
    valid_statuses = ['TRADED', 'PENDING', 'TRANSIT']
    return [order for order in orders if order.get('orderStatus') in valid_statuses]

# Step 3: Place orders in child accounts with multiplier
def place_order_in_child_account(order, child_account, multiplier):
    url = 'https://api.dhan.co/v2/orders'
    headers = {'Content-Type': 'application/json', 'access-token': child_account.token}
    
    order['dhanClientId'] = child_account.client_id
    original_quantity = order.get('quantity')
    child_quantity = int(original_quantity * multiplier)  # Round to integer
    order['quantity'] = child_quantity
    order['afterMarketOrder'] = True
    order['amoTime'] = 'OPEN'

    try:
        response = requests.post(url, headers=headers, json=order)
        response.raise_for_status()
        child_order_id = response.json().get('orderId')
        logging.info(f"Order placed in child account {child_account.name}. Order ID: {child_order_id}, Quantity: {child_quantity}")
        return child_order_id, child_quantity
    except Exception as e:
        logging.error(f"Failed to place order in child account {child_account.name}: {e}")
        return None, None

# Step 4: Place sell order in child accounts with proportional remaining quantity
def place_sell_order_in_child_account(order, child_account, child_order_id, original_multiplier, master_original_qty, master_sell_qty, child_remaining_qty):
    url = 'https://api.dhan.co/v2/orders'
    headers = {'Content-Type': 'application/json', 'access-token': child_account.token}
    
    # Calculate sell quantity proportional to remaining child quantity
    proportion = master_sell_qty / master_original_qty
    sell_quantity = min(int(child_remaining_qty * proportion), child_remaining_qty)  # Ensure we don’t oversell
    
    # If this is the last sell (master qty = 0 after this), sell all remaining
    if master_sell_qty == master_original_qty:
        sell_quantity = child_remaining_qty
    
    payload = {
        'dhanClientId': child_account.client_id,
        'transactionType': 'SELL',
        'exchangeSegment': order.get('exchangeSegment'),
        'productType': order.get('productType'),
        'orderType': order.get('orderType'),
        'validity': order.get('validity'),
        'securityId': order.get('securityId'),
        'quantity': sell_quantity,
        'afterMarketOrder': True,
        'amoTime': 'OPEN'
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        new_child_order_id = response.json().get('orderId')
        logging.info(f"Sell order placed in child account {child_account.name}. Order ID: {new_child_order_id}, Quantity: {sell_quantity}")
        return new_child_order_id, sell_quantity
    except Exception as e:
        logging.error(f"Failed to place sell order in child account {child_account.name}: {e}")
        return None, 0
    

###############################################################################################################################



import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from django.db import transaction
from django.utils.timezone import now
from Lucky_Bulls.models import Screener, Performance

import logging
from Lucky_Bulls.telegram_alert import send_telegram_alert


logger = logging.getLogger(__name__)

def fetch_screener_data(condition, screener_name):
    """
    Fetch screener data from Chartink, annotate it with the screener name,
    and send Telegram alerts for new or unalerted stocks.
    """
    try:
        with requests.session() as s:
            # Get CSRF token
            r_data = s.get("https://chartink.com")
            soup = bs(r_data.content, "lxml")
            meta = soup.find("meta", {"name": "csrf-token"})["content"]

            # POST screener condition
            headers = {
                "x-csrf-token": meta,
                "Content-Type": "application/x-www-form-urlencoded",
            }
            response = s.post(
                "https://chartink.com/screener/process", headers=headers, data=condition
            ).json()

            # Parse results
            stock_list = pd.DataFrame(response.get("data", []))
            required_columns = [
                "sr", "nsecode", "name", "bsecode", "per_chg", "close", "volume"
            ]
            for col in required_columns:
                if col not in stock_list.columns:
                    stock_list[col] = None

            stock_list["screener_name"] = screener_name
            stock_list = stock_list[required_columns + ["screener_name"]]

            # Fetch screener
            screener_instance = Screener.objects.get(name=screener_name)

            performances_to_update = []

            for _, row in stock_list.iterrows():
                symbol = row["nsecode"]
                close_price = row["close"]

                performance, created = Performance.objects.get_or_create(
                    symbol=symbol,
                    screener=screener_instance,
                    defaults={
                        "triggered_at": now(),
                        "initial_price": close_price,
                        "alert_sent": False,
                    }
                )

                if created or not performance.alert_sent:
                    stock_details = (
                        f"Symbol: {symbol}\n"
                        f"Close Price: ₹{close_price}\n"
                        f"Triggered At: {performance.triggered_at}\n"
                        f"Screener: {screener_name}"
                    )
                    try:
                        if send_telegram_alert(symbol, screener_name, stock_details):
                            performance.alert_sent = True
                            performance.alert_sent_at = now()
                            performances_to_update.append(performance)
                            logger.info(f"Alert sent for {symbol} in {screener_name}")
                        else:
                            logger.warning(f"Telegram API returned False for {symbol}")
                    except Exception as e:
                        logger.error(f"Telegram error for {symbol}: {e}")
                        continue

            # Save updated performances
            if performances_to_update:
                with transaction.atomic():
                    Performance.objects.bulk_update(performances_to_update, ["alert_sent", "alert_sent_at"])

            return stock_list.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Error fetching screener '{screener_name}': {e}")
        return None
