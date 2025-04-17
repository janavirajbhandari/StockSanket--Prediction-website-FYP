from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from stocks.models import Stock
from django.contrib.auth import logout
from django.shortcuts import redirect


import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import csv
import yfinance as yf
import pandas as pd



# Function to get stock info using yfinance
def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info  # Fetch stock details

    return {
        "symbol": ticker,
        "market_cap": info.get("marketCap", "N/A"),
        "industry": info.get("industry", "N/A"),
        "company": info.get("longName", "N/A"),
        "revenue": info.get("totalRevenue", "N/A"),
    }

# Create your views here.
recent_news = [
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
    {"time": "8h", "title": "Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
    {"time": "8h", "title": "Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications", "source": "PYMNTS"},
    {"time": "8h", "title": "December Sees 1.5% Rise in Business Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
    {"time": "8h", "title": "Applications, Signaling Cautious Optimism", "source": "PYMNTS"},
]

def HomePage(request):
    # Sample data for top gainers
    top_gainers = [
        {"symbol": "QIMI", "name": "WiMi Hologram Cloud", "price": "$45", "percentage": "77.8%"},
        {"symbol": "AAPL", "name": "Apple Inc.", "price": "$178", "percentage": "1.5%"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": "$2740", "percentage": "2.3%"},
         {"symbol": "QIMI", "name": "WiMi Hologram Cloud", "price": "$45", "percentage": "77.8%"},
        {"symbol": "AAPL", "name": "Apple Inc.", "price": "$178", "percentage": "1.5%"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": "$2740", "percentage": "2.3%"},
         {"symbol": "QIMI", "name": "WiMi Hologram Cloud", "price": "$45", "percentage": "77.8%"},
        {"symbol": "AAPL", "name": "Apple Inc.", "price": "$178", "percentage": "1.5%"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": "$2740", "percentage": "2.3%"},
    ]

    # Sample data for top losers
    top_losers = [
        {"symbol": "MSFT", "name": "Microsoft Corp.", "price": "$320", "percentage": "-0.5%"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "price": "$720", "percentage": "-2.2%"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "price": "$3345", "percentage": "-1.1%"},
         {"symbol": "MSFT", "name": "Microsoft Corp.", "price": "$320", "percentage": "-0.5%"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "price": "$720", "percentage": "-2.2%"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "price": "$3345", "percentage": "-1.1%"},
         {"symbol": "MSFT", "name": "Microsoft Corp.", "price": "$320", "percentage": "-0.5%"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "price": "$720", "percentage": "-2.2%"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "price": "$3345", "percentage": "-1.1%"},
    ]

    # Pass data to template
    context = {
        "recent_news": recent_news, # Send news to home page
        "top_gainers": top_gainers,
        "top_losers": top_losers
    }
    
    return render(request, 'home.html', context)

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1!=pass2:
            return HttpResponse("Your password and confrom password are not Same!!")
        else:

            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            return redirect('login')

    return render (request,'signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'login.html')

def LogoutPage(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', 'home'))  # reloads same page or fallback to home

    
def Articles(request):
    return render (request,'articles.html')

def News(request):
    context = {
        "recent_news": recent_news,
    }
    return render(request, 'news.html', context)


def StocksView(request):
    stocks_list = Stock.objects.all()  # ✅ Load from database instead of API

    # ✅ Paginate results (10 per page)
    paginator = Paginator(stocks_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'stocks.html', {"stocks": page_obj})  # ✅ Send database results



def Watchlists(request):
    return render (request,'watchlists.html')


