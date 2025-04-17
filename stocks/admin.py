from django.contrib import admin
from .models import Stock, Watchlist  # ✅ Import Watchlist model

# Register models
admin.site.register(Stock)
admin.site.register(Watchlist)  # ✅ Register Watchlist in Django admin
