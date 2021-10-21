from django.urls import path
from . import views

urlpatterns = [
    path("api/check/", views.ValidateSymbol.as_view(), name='check_symbol'),
    path("api/balance/", views.ProfitLoss.as_view(), name='balance'),
    path("api/held-shares/", views.HeldShares.as_view(), name='held_shares'),
    path("api/current-value-of-shares/", views.CurrentValueOfTheShares.as_view(), name='current_value_of_shares'),
    path("api/current-day-reference-prices/", views.CurrentDayReferencePrice.as_view(), name='current_day_reference_price'),
    path("api/historic-price-of-stock/", views.GetHistoricPriceInterval.as_view(), name='historic_price_of_stock'),
    path("api/trade/", views.TradeShare.as_view(), name='trade'),
]