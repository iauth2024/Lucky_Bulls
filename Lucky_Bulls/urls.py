from django.urls import path
from .views import (
    index_view,
    screener_list, 
    trading_data_view,
    TradingAccountListView,
    TradingAccountCreateView,
    TradingAccountUpdateView,
    TradingAccountDeleteView,
    add_screener,
    
    
    
    edit_screener,
    delete_screener,
)
from .views import monitor_control_view

from Lucky_Bulls import views
from django.contrib.auth import views as auth_views
from .views import monitor_control_view, toggle_monitor_view
urlpatterns = [
    # Home page
    path('', views.index_view, name='index_view'), 
    path('monitor/', monitor_control_view, name='monitor_control'),
    path('toggle-monitor/', toggle_monitor_view, name='toggle_monitor'),
    path('toggle/<str:monitor_type>/', toggle_monitor_view, name='toggle_monitor'),
    # Trading Data
    path('trading_data/', trading_data_view, name='trading_data'),
    path('stocks/', views.stock_page, name='stock_page'),
    path('monitor-control/', monitor_control_view, name='monitor_control'),

    path('fetch-screener-list/', views.fetch_screener_list, name='fetch_screener_list'),
    path('fetch-screener/<int:screener_id>/', views.fetch_chartink_data, name='fetch_chartink_data'),
 


    # Trading Accounts
    path('accounts/', TradingAccountListView.as_view(), name='trading_account_list'),
    path('accounts/add/', TradingAccountCreateView.as_view(), name='trading_account_add'),
    path('accounts/<int:pk>/edit/', TradingAccountUpdateView.as_view(), name='trading_account_edit'),
    path('accounts/<int:pk>/delete/', TradingAccountDeleteView.as_view(), name='trading_account_delete'),
    path('fetch-halal-stocks/', views.fetch_halal_stocks, name='fetch-halal-stocks'),
    path('fetch-all-screeners/', views.fetch_all_screeners, name='fetch_all_screeners'),
    
    # Screener Results
    path('screener_results/', views.screener_results, name='screener_results'),

    # Combined Screener Results
   

    # Performance Tracking Page
    path('performance/', views.performance_page, name='performance_page'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # Screener Management
     path('screeners/', screener_list, name='screener_list'),
    
    # Add Screener
    path('screeners/add/', add_screener, name='add_screener'),
    path('fetch-halal-stocks/', views.fetch_halal_stocks, name='fetch-halal-stocks'),
    
    # Edit Screener
    path('screeners/edit/<int:screener_id>/', edit_screener, name='edit_screener'),
    
    # Delete Screener
    path('screeners/delete/<int:screener_id>/', delete_screener, name='delete_screener'),
    
    # Trading Journal Page
    # path('trading_journal/', views.trading_journal, name='trading_journal'),

    # Delete selected stocks from the performance page (if needed)
    # path('delete-selected-stocks/', views.delete_selected_stocks, name='delete_selected_stocks'),
]
