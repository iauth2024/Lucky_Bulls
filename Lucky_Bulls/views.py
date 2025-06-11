from django.shortcuts import render
# Create your views here.
from django.http import JsonResponse
from dhanhq import dhanhq
from .models import TradingAccount
# prompt: AttributeError at /trading_data/
# 'dhanhq' object has no attribute 'get_holdings_data'

from django.shortcuts import render

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import TradingAccount
from .forms import TradingAccountForm
from django.http import JsonResponse
from django.shortcuts import render
from dhanhq import dhanhq
from .models import TradingAccount
import logging
import requests


# DhanHQ API Wrapper Class
class dhanhq:
    def __init__(self, client_id, access_token, disable_ssl=False, pool=None):
        """
        Initialize the dhanhq class with client ID and access token.

        Args:
            client_id (str): The client ID for the trading account.
            access_token (str): The access token for API authentication.
            disable_ssl (bool): Flag to disable SSL verification.
            pool (dict): Optional connection pool settings.
        """
        self.client_id = str(client_id)
        self.access_token = access_token
        self.base_url = 'https://api.dhan.co/v2'
        self.timeout = 10  # Timeout for API requests
        self.session = requests.Session()
        self.header = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        if disable_ssl:
            self.session.verify = False

    def _parse_response(self, response):
        """
        Parse the API response and handle errors.

        Args:
            response (requests.Response): The response object.

        Returns:
            dict: Parsed response or error message.
        """
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                logging.error('Error parsing JSON response: %s', e)
                return {
                    'status': 'failure',
                    'remarks': 'Invalid JSON response',
                    'data': '',
                }
        else:
            logging.error('API error: %s', response.text)
            return {
                'status': 'failure',
                'remarks': response.text,
                'data': '',
            }
   

# Django View for Trading Data
from django.http import JsonResponse
from django.shortcuts import render
from dhanhq import dhanhq
from .models import TradingAccount
import logging

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO for better visibility

from django.shortcuts import render
import logging



# Configure logging for the view function
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from django.shortcuts import render
from .models import TradingAccount
from .dhanhq import dhanhq  # Assuming you have a function to interact with Dhan API
import logging

# Initialize the logger
logger = logging.getLogger(__name__)
from dhanhq import dhanhq
import logging
from django.shortcuts import render
from .models import TradingAccount

logger = logging.getLogger(__name__)

def fetch_fund_limits(dhan_client):
    """Fetches fund limits for a Dhan account."""
    try:
        fund_limits = dhan_client.get_fund_limits()
        return fund_limits.get('data', {}).get('availabelBalance', 'N/A')  # Adjust key spelling if necessary
    except Exception as e:
        logger.error(f"Error fetching fund limits: {e}")
        return None

def fetch_holdings(dhan_client):
    """Fetches holdings for a Dhan account."""
    try:
        holdings = dhan_client.get_holdings()
        if holdings and 'data' in holdings:
            return [
                {
                    'Symbol': holding.get('tradingSymbol', 'N/A'),
                    'Total Quantity': holding.get('totalQty', 'N/A'),
                    'Average Cost Price': holding.get('avgCostPrice', 'N/A'),
                }
                for holding in holdings['data']
            ]
        return "No holdings data available."
    except Exception as e:
        logger.error(f"Error fetching holdings: {e}")
        return None

def fetch_positions(dhan_client):
    """Fetches positions for a Dhan account."""
    try:
        positions = dhan_client.get_positions()
        if positions and 'data' in positions:
            return [
                {
                    'tradingSymbol': position.get('tradingSymbol', 'N/A'),
                    'buyQty': position.get('buyQty', 'N/A'),
                    'sellQty': position.get('sellQty', 'N/A'),
                    'netQty': position.get('netQty', 'N/A'),
                    'realizedProfit': position.get('realizedProfit', 'N/A'),
                    'unrealizedProfit': position.get('unrealizedProfit', 'N/A'),
                }
                for position in positions['data']
            ]
        return "No positions data available."
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        return None
def fetch_orders(dhan_client):
    """Fetches and filters the orders for a Dhan account."""
    try:
        orders = dhan_client.get_order_list()
        if orders and 'data' in orders:
            filtered_orders = []
            for order in orders['data']:
                filtered_order = {
                    'orderStatus': order.get('orderStatus', 'N/A'),
                    'transactionType': order.get('transactionType', 'N/A'),
                    'exchangeSegment': order.get('exchangeSegment', 'N/A'),
                    'productType': order.get('productType', 'N/A'),
                    'orderType': order.get('orderType', 'N/A'),
                    'validity': order.get('validity', 'N/A'),
                    'tradingSymbol': order.get('tradingSymbol', 'N/A'),
                    'securityId': order.get('securityId', 'N/A'),
                    'quantity': order.get('quantity', 'N/A'),
                    'disclosedQuantity': order.get('disclosedQuantity', 'N/A'),
                    'price': order.get('price', 'N/A'),
                    'triggerPrice': order.get('triggerPrice', 'N/A'),
                    'afterMarketOrder': order.get('afterMarketOrder', 'N/A'),
                    'createTime': order.get('createTime', 'N/A'),
                    'updateTime': order.get('updateTime', 'N/A'),
                }
                filtered_orders.append(filtered_order)
            return filtered_orders
        else:
            return "No orders data available."
    except Exception as e:
        return f"Error fetching orders: {e}"


import time
import logging
from django.shortcuts import render
from .models import TradingAccount

logger = logging.getLogger(__name__)

import logging

logger = logging.getLogger(__name__)


import time
import logging
import threading
from django.shortcuts import render
from .models import TradingAccount
from .dhanhq import dhanhq  # Ensure this is the correct import for your Dhan API wrapper

logger = logging.getLogger(__name__)

def fetch_orders(dhan_client):
    """Fetches and filters the orders for a Dhan account."""
    try:
        orders = dhan_client.get_order_list()  # Ensure this is the correct method name
        if orders and 'data' in orders:
            filtered_orders = []
            for order in orders['data']:
                filtered_order = {
                    'orderStatus': order.get('orderStatus', 'N/A'),
                    'transactionType': order.get('transactionType', 'N/A'),
                    'exchangeSegment': order.get('exchangeSegment', 'N/A'),
                    'productType': order.get('productType', 'N/A'),
                    'orderType': order.get('orderType', 'N/A'),
                    'validity': order.get('validity', 'N/A'),
                    'tradingSymbol': order.get('tradingSymbol', 'N/A'),
                    'securityId': order.get('securityId', 'N/A'),
                    'quantity': order.get('quantity', 'N/A'),
                    'disclosedQuantity': order.get('disclosedQuantity', 'N/A'),
                    'price': order.get('price', 'N/A'),
                    'triggerPrice': order.get('triggerPrice', 'N/A'),
                    'afterMarketOrder': order.get('afterMarketOrder', 'N/A'),
                    'createTime': order.get('createTime', 'N/A'),
                    'updateTime': order.get('updateTime', 'N/A'),
                }
                filtered_orders.append(filtered_order)
            return filtered_orders
        else:
            return "No orders data available."
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return f"Error fetching orders: {e}"



def trading_data_view(request):
    """Fetches trading data and copies master orders to child accounts."""
    
    # Initialize accounts if not already present
    if not TradingAccount.objects.exists():
        try:
            TradingAccount.objects.create(
                name="Master Account", client_id="master123", token="mastertoken", is_master=True
            )
            TradingAccount.objects.create(
                name="Child Account 1", client_id="child123", token="childtoken1", is_child=True, multiplier=1.5
            )
            TradingAccount.objects.create(
                name="Child Account 2", client_id="child456", token="childtoken2", is_child=True, multiplier=2.0
            )
            logger.info("Accounts initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing accounts: {e}")
            return render(request, 'error.html', {'error_message': "Error initializing accounts."})

    # Fetch accounts from the database
    accounts = TradingAccount.objects.all()
    if not accounts:
        logger.error("No accounts found in the database.")
        return render(request, 'error.html', {'error_message': "No trading accounts found."})

    master_account = None
    child_accounts_data = []
    child_accounts = []  # Store child accounts for order copying

    # Process each account and fetch data
    for account in accounts:
        dhan_client = dhanhq(account.client_id, account.token)  # Initialize the Dhan client
        try:
            account_data = {
                'name': account.name,
                'client_id': account.client_id,
                'holdings': fetch_holdings(dhan_client),
                'positions': fetch_positions(dhan_client),
                'fund_limits': fetch_fund_limits(dhan_client),
                'orders': fetch_orders(dhan_client),  # Fetch orders for each account
            }
            if account.is_master:
                master_account = account_data
                master_client = dhan_client  # Save master client for monitoring orders
                logger.info(f"Master Account Data: {master_account}")
            elif account.is_child:
                child_accounts.append(account)  # Save child accounts for order copying
                child_accounts_data.append(account_data)
                logger.info(f"Child Account Data: {account_data}")
        except Exception as e:
            logger.error(f"Error processing account {account.name}: {e}")
            continue
    
    # Monitor Master Orders and Copy to Child Accounts

    # Prepare context for the template
    context = {
        'master_account': master_account,
        'child_accounts': child_accounts_data,
    }

    return render(request, 'trading_data.html', context)




# Error View for Handling Exceptions
def error_view(request, exception):
    return render(request, 'error.html', {'error_message': str(exception)})

# List all accounts
class TradingAccountListView(ListView):
    model = TradingAccount
    template_name = 'trading_account_list.html'
    context_object_name = 'accounts'

# Add a new account
class TradingAccountCreateView(CreateView):
    model = TradingAccount
    form_class = TradingAccountForm
    template_name = 'trading_account_form.html'
    success_url = reverse_lazy('trading_account_list')

# Edit an account
class TradingAccountUpdateView(UpdateView):
    model = TradingAccount
    form_class = TradingAccountForm
    template_name = 'trading_account_form.html'
    success_url = reverse_lazy('trading_account_list')

# Delete an account
class TradingAccountDeleteView(DeleteView):
    model = TradingAccount
    template_name = 'trading_account_confirm_delete.html'
    success_url = reverse_lazy('trading_account_list')
from django.shortcuts import render, redirect
from .models import MonitorControl

from django.shortcuts import render, redirect
from .models import MonitorControl, Screener

# Monitor Control Views
def index_view(request):
    control, created = MonitorControl.objects.get_or_create(id=1, defaults={'is_active': True})
    screeners = Screener.objects.all()

    if request.method == 'POST':
        is_active = request.POST.get('is_active') == 'on'
        control.is_active = is_active
        control.save()
        return redirect('index_view')

    return render(request, 'index.html', {'control': control, 'screeners': screeners})
# Screener Views
# class ScreenerList(ListView):
#     model = Screener
#     template_name = 'screener_list.html'
#     context_object_name = 'screeners'
#     paginate_by = 10

# class ScreenerCreateView(CreateView):
#     model = Screener
#     form_class = ScreenerForm
#     template_name = 'screener_form.html'
#     success_url = reverse_lazy('screener_list')
    
#     def form_valid(self, form):
#         messages.success(self.request, 'Screener created successfully!')
#         return super().form_valid(form)

# class ScreenerUpdateView(UpdateView):
#     model = Screener
#     form_class = ScreenerForm
#     template_name = 'screener_form.html'
#     success_url = reverse_lazy('screener_list')
    
#     def form_valid(self, form):
#         messages.success(self.request, 'Screener updated successfully!')
#         return super().form_valid(form)

# class ScreenerDeleteView(DeleteView):
#     model = Screener
#     template_name = 'screener_confirm_delete.html'
#     success_url = reverse_lazy('screener_list')
    
#     def delete(self, request, *args, **kwargs):
#         messages.success(request, 'Screener deleted successfully!')
#         return super().delete(request, *args, **kwargs)
##############################################################################################################################


#########################################################################################################################
# Screener-Related Views
#########################################################################################################################
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Screener
from .forms import ScreenerForm

def screener_list(request):
    """
    Display a list of all screeners.
    """
    screeners = Screener.objects.all()
    return render(request, "screener_list.html", {"screeners": screeners})


def add_screener(request):
    """
    Add a new screener.
    """
    if request.method == 'POST':
        form = ScreenerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Screener added successfully.")
            return redirect('screener_results')
    else:
        form = ScreenerForm()
    return render(request, 'add_screener.html', {'form': form})


def edit_screener(request, screener_id):
    """
    Edit an existing screener.
    """
    screener = get_object_or_404(Screener, id=screener_id)
    if request.method == 'POST':
        form = ScreenerForm(request.POST, instance=screener)
        if form.is_valid():
            form.save()
            messages.success(request, "Screener updated successfully.")
            return redirect('screener_results')
    else:
        form = ScreenerForm(instance=screener)
    return render(request, 'edit_screener.html', {'form': form, 'screener': screener})


def delete_screener(request, screener_id):
    """
    Delete an existing screener.
    """
    screener = get_object_or_404(Screener, id=screener_id)
    if request.method == 'POST':
        screener.delete()
        messages.success(request, "Screener deleted successfully.")
        return redirect('screener_results')
    return render(request, 'confirm_delete_screener.html', {'screener': screener})
from collections import defaultdict  # Add this import at the top
from django.shortcuts import render
from .models import Screener
import logging

logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from collections import defaultdict
from django.shortcuts import render
from .models import Screener, Performance
import logging

logger = logging.getLogger(__name__)

from django.db.models import Count
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def screener_results(request):
    """
    Fetches and displays results for selected screeners with pagination and performance tracking.
    """
    try:
        # Get filter parameters
        screeners = Screener.objects.filter(is_active=True)
        screener_names = [screener.name for screener in screeners]
        screener_name = request.GET.get("screener", "ALL")
        days_selection = int(request.GET.get("days", 5))  # Default to 5 days
        logger.info(f"Selected Screener: {screener_name}, Days: {days_selection}")

        # Validate days selection
        valid_days = [1, 2, 3, 4, 5, 10, 20, 30]
        if days_selection not in valid_days:
            days_selection = 5

        all_stock_data = []
        stock_counter = defaultdict(list)

        if screener_name == "ALL":
            for screener in screeners:
                response = fetch_screener_data({"scan_clause": screener.condition}, screener.name)
                if response:
                    for stock in response:
                        symbol = stock.get("nsecode") or stock.get("symbol") or stock.get("ticker")
                        if symbol:
                            stock_counter[symbol].append(screener.name)
                            all_stock_data.append(stock)
        else:
            try:
                screener = Screener.objects.get(name=screener_name)
                response = fetch_screener_data({"scan_clause": screener.condition}, screener.name)
                if response:
                    for stock in response:
                        symbol = stock.get("nsecode") or stock.get("symbol") or stock.get("ticker")
                        if symbol:
                            stock_counter[symbol].append(screener.name)
                            all_stock_data.append(stock)
            except Screener.DoesNotExist:
                logger.error(f"Screener not found: {screener_name}")

        # Create stocks lists with performance data
        lucky_bull_stocks = []
        other_stocks = []
        
        for symbol, screener_list in stock_counter.items():
            stock_data = next(
                (s for s in all_stock_data if 
                 (s.get("nsecode") or s.get("symbol") or s.get("ticker")) == symbol),
                None
            )
            
            if stock_data:
                stock_data = stock_data.copy()
                stock_data["symbol"] = symbol
                stock_data["screener_count"] = len(screener_list)
                stock_data["screener_names"] = screener_list

                # Get performance data for selected time period
                performance_data = get_performance_data(symbol, days_selection)
                if performance_data:
                    stock_data.update({
                        'start_price': performance_data['start_price'],
                        'end_price': performance_data['end_price'],
                        'percentage_change': performance_data['percentage_change'],
                        'trend_data': performance_data['trend_data']
                    })

                if len(screener_list) > 1:
                    lucky_bull_stocks.append(stock_data)
                else:
                    other_stocks.append(stock_data)

        # Sort lucky bull stocks by screener count (descending)
        lucky_bull_stocks.sort(key=lambda x: x["screener_count"], reverse=True)

        # Sort all stocks by percentage change (descending)
        lucky_bull_stocks.sort(key=lambda x: x.get('percentage_change', 0), reverse=True)
        other_stocks.sort(key=lambda x: x.get('percentage_change', 0), reverse=True)

        # Paginate the results
        lucky_bull_paginator = Paginator(lucky_bull_stocks, 10)
        other_stocks_paginator = Paginator(other_stocks, 20)
        
        lucky_bull_page = request.GET.get('lucky_bull_page')
        other_stocks_page = request.GET.get('other_stocks_page')
        
        lucky_bull_page_obj = lucky_bull_paginator.get_page(lucky_bull_page)
        other_stocks_page_obj = other_stocks_paginator.get_page(other_stocks_page)

        logger.info(f"Found {len(lucky_bull_stocks)} lucky bull stocks")
        logger.info(f"Found {len(other_stocks)} other stocks")

        return render(
            request,
            "screener_results.html",
            {
                "lucky_bull_page_obj": lucky_bull_page_obj,
                "other_stocks_page_obj": other_stocks_page_obj,
                "screener_name": screener_name,
                "screener_names": screener_names,
                "days_selection": days_selection,
                "valid_days": valid_days,
                "debug_info": {
                    "all_stock_data_count": len(all_stock_data),
                    "stock_counter_size": len(stock_counter),
                }
            },
        )

    except Exception as e:
        logger.error(f"Error in screener_results: {str(e)}", exc_info=True)
        return render(
            request,
            "screener_results.html",
            {
                "error": f"An error occurred: {str(e)}",
                "screener_name": screener_name or "ALL",
                "screener_names": screener_names,
                "days_selection": 5,
                "valid_days": [1, 2, 3, 4, 5, 10, 20, 30],
            },
        )


def get_performance_data(symbol, days):
    """
    Helper function to get performance data for a stock over a given period.
    Returns a dictionary with performance metrics.
    """
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get historical data - implement this based on your data source
        historical_data = HistoricalPrice.objects.filter(
            symbol=symbol,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if not historical_data.exists():
            return None
        
        start_price = historical_data.first().close
        end_price = historical_data.last().close
        percentage_change = ((end_price - start_price) / start_price) * 100
        
        # Prepare trend data for chart
        trend_data = [{
            'date': data.date.strftime('%Y-%m-%d'),
            'price': data.close
        } for data in historical_data]
        
        return {
            'start_price': start_price,
            'end_price': end_price,
            'percentage_change': round(percentage_change, 2),
            'trend_data': trend_data
        }
        
    except Exception as e:
        logger.error(f"Error getting performance data for {symbol}: {str(e)}")
        return None
#########################################################################################################################
# Performance-Related Views
#########################################################################################################################

from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def performance_page(request):
    """
    Display performance data with pagination and search functionality.
    """
    # Initialize variables
    search_query = request.GET.get('q', '')
    alert_filter = request.GET.get('filter', 'all')
    
    # Base queryset
    performances = Performance.objects.all().order_by('-triggered_at')
    
    # Apply search filter if query exists
    if search_query:
        performances = performances.filter(
            Q(symbol__icontains=search_query) | 
            Q(screener__name__icontains=search_query)
        )
    
    # Apply alert status filter
    if alert_filter == 'sent':
        performances = performances.filter(alert_sent=True)
    elif alert_filter == 'pending':
        performances = performances.filter(alert_sent=False)
    
    # Get top performers
    top_performers = (
        Performance.objects.values('symbol')
        .annotate(
            count=Count('id'), 
            alert_sent_count=Count('id', filter=Q(alert_sent=True))
        )
        .order_by('-count')[:5]
    )
    
    # Paginate the results (e.g., 10 items per page)
    paginator = Paginator(performances, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    context = {
        'performances': page_obj,
        'top_performers': top_performers,
        'search_query': search_query,
        'current_filter': alert_filter,
    }
    
    return render(request, 'performance.html', context)



#########################################################################################################################
# Combined Results View
#########################################################################################################################

from django.shortcuts import render


from Lucky_Bulls.models import Screener, Performance, Stock
from django.utils.timezone import now
from datetime import datetime
import logging
from .utils import fetch_screener_data
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

def combined_results(request):
    """
    Fetch and combine screener data for all active screeners, sorted by date.
    Optionally filter by screener name and date filter from GET params.
    """
    # Get filters from request, default to ALL screeners and all time
    selected_screener = request.GET.get('screener', 'ALL')
    selected_date_filter = request.GET.get('date_filter', 'all_time')

    # Date filter options for dropdown
    date_filters = [
        ("today", "Today"),
        ("yesterday", "Yesterday"),
        ("this_week", "This Week"),
        ("last_week", "Last Week"),
        ("all_time", "All Time")
    ]

    screeners = Screener.objects.filter(is_active=True)
    combined_data = {}

    # Define a helper function for date filtering
    def filter_entries_by_date(entries, date_filter):
        if not entries:
            return entries
        today = datetime.today().date()

        def parse_date(d):
            try:
                return datetime.fromisoformat(d).date()
            except Exception:
                return None

        filtered = []
        for e in entries:
            entry_date = parse_date(e.get('date'))
            if not entry_date:
                continue
            if date_filter == "today" and entry_date == today:
                filtered.append(e)
            elif date_filter == "yesterday" and entry_date == (today - timedelta(days=1)):
                filtered.append(e)
            elif date_filter == "this_week":
                start_week = today - timedelta(days=today.weekday())
                end_week = start_week + timedelta(days=6)
                if start_week <= entry_date <= end_week:
                    filtered.append(e)
            elif date_filter == "last_week":
                start_last_week = (today - timedelta(days=today.weekday() + 7))
                end_last_week = start_last_week + timedelta(days=6)
                if start_last_week <= entry_date <= end_last_week:
                    filtered.append(e)
            elif date_filter == "all_time":
                filtered.append(e)
        return filtered

    for screener in screeners:
        # If a specific screener is selected, skip others
        if selected_screener != 'ALL' and screener.name != selected_screener:
            continue

        logger.info(f"Fetching data for screener: {screener.name}")
        screener_data = fetch_screener_data({"scan_clause": screener.condition}, screener.name)
        logger.info(f"Raw data for {screener.name}: {len(screener_data or [])} entries")

        if not screener_data:
            # Fallback to Stock model data
            stock_data = Stock.objects.filter(screener=screener).values(
                'nsecode', 'name', 'bsecode', 'per_chg', 'close', 'volume'
            )
            screener_data = list(stock_data)
            logger.info(f"Fallback to {len(screener_data)} Stock entries for {screener.name}")

        if not screener_data:
            continue

        # Add 'date' field based on Performance.triggered_at or now()
        valid_screener_data = []
        for entry in screener_data:
            try:
                if not entry.get('nsecode'):
                    logger.warning(f"Missing 'nsecode' in entry: {entry}")
                    continue
                performance = Performance.objects.filter(
                    symbol=entry.get('nsecode'),
                    screener=screener
                ).first()
                entry['date'] = performance.triggered_at.isoformat() if performance else now().isoformat()
                valid_screener_data.append(entry)
            except Exception as e:
                logger.warning(f"Error processing entry for {entry.get('nsecode', 'unknown')}: {e}")
                continue

        # Filter entries by date filter
        filtered_data = filter_entries_by_date(valid_screener_data, selected_date_filter)

        # Sort by date descending
        screener_data_sorted = sorted(
            filtered_data,
            key=lambda x: datetime.fromisoformat(x.get('date', '1970-01-01')),
            reverse=True
        )

        combined_data[screener.name] = screener_data_sorted

    # Pass dropdown options and selected filters to template
    context = {
        'combined_data': combined_data,
        'screeners': screeners,
        'date_filters': date_filters,
        'selected_screener': selected_screener,
        'selected_date_filter': selected_date_filter,
    }

    return render(request, 'combined_results.html', context)

    # Wrapper to convert list of dicts to DataFrame with 'date' column
    