from django.contrib import admin
from django.urls import path
from authentication import views as auth_views  
from stocks import views as stock_views  


urlpatterns = [
    path('admin/', admin.site.urls),

    # Public Pages
    path('', auth_views.HomePage, name='home'),  # ✅ Now homepage is root
    path('signup/', auth_views.SignupPage, name='signup'),
    path('login/', auth_views.LoginPage, name='login'),
    path('logout/', auth_views.LogoutPage, name='logout'),

    # Stocks-related Pages (Login required inside views)
    path('stocks/', stock_views.StocksView, name='stocks'),
    path("compare_stocks/", stock_views.compare_stocks_view, name="compare_stocks"),
    path('get_stock_data/<str:symbol>/', stock_views.get_stock_data, name='get_stock_data'),
    path('stockDetail/<str:symbol>/', stock_views.StockDetail, name='stockDetail'),

    path("news/", stock_views.mero_news_view, name="news"),
    path("news/detail/<int:news_id>/", stock_views.news_detail, name="news_detail"),


    path('articles/', stock_views.blog_articles_view, name="articles"),
    # path("predict/<str:symbol>/", stock_views.stock_prediction_view, name="predict_stock"),
    path("sentiment/<str:symbol>/", stock_views.StockDetail, name="sentiment_stock"),
    path('loading/<str:symbol>/', stock_views.stock_loading_view, name='stock_loading'),


    # Watchlist Paths
    path('watchlists/', stock_views.watchlist_view, name='watchlists'),
    path('add_to_watchlist/', stock_views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/', stock_views.remove_from_watchlist, name='remove_from_watchlist'),
    # path("api/stock_data/<str:symbol>/", stock_views.stock_data_api, name="stock_data_api"),
]
