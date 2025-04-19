import re
import feedparser  # ✅ Install with: pip install feedparser
import os
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Watchlist, Stock
from django.shortcuts import render, get_object_or_404
import requests
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup
# company_id = models.IntegerField(null=True, blank=True)

from django.shortcuts import redirect, render

def stock_loading_view(request, symbol):
    url = f"/stockDetail/{symbol}/"
    return render(request, "loading.html", {"target_url": url})

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def scrape_stock_data_from_nepalstock(company_id):
    try:
        url = f"https://www.nepalstock.com/company/detail/{company_id}"

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0")
        chrome_driver_path = r"C:\Users\Bishal\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(5)  # Wait for JS to render

        def get_value(label):
            rows = driver.find_elements(By.CSS_SELECTOR, "table.table-striped tr")
            for row in rows:
                try:
                    th = row.find_element(By.TAG_NAME, "th")
                    td = row.find_element(By.TAG_NAME, "td")
                    if label.lower() in th.text.lower():
                        return td.text.strip()
                except:
                    continue
            return "N/A"
        # Get combined value (e.g. "485.50 -0.77 (-0.16%)")
        raw_price = get_value("Last Traded Price")
        price_match = re.match(r"([\d,]+\.\d+)\s+(-?\d+\.\d+)\s+\((-?\d+\.\d+)%\)", raw_price)

        if price_match:
            actual_price = price_match.group(1).replace(",", "")
            price_change = price_match.group(2)
            percentage_change = price_match.group(3)
        else:
            actual_price = raw_price.replace(",", "") if raw_price else "0"
            price_change = "0"
            percentage_change = "0"

        data = {
            "last_price": actual_price,
            "price_change": price_change,
            "percentage_change": percentage_change,
            "previous_close": get_value("Previous Day Close Price"),
            "volume": get_value("Total Traded Quantity"),
            "trades": get_value("Total Trades"),
            "high_low": get_value("High Price / Low Price"),
            "week_52": get_value("52 Week High / 52 Week Low"),
            "open_price": get_value("Open Price"),
            "close_price": get_value("Close Price"),
            "market_cap": get_value("Market Capitalization"),
            "public_shares": get_value("Total Listed Shares"),
            "promoter_shares": get_value("Promoter Shareholding"),
            "share_registrar": get_value("Share Registrar"),
        }

        driver.quit()
        return data

    except Exception as e:
        print("❌ Scraping Error:", str(e))
        return None




from django.shortcuts import redirect
from django.contrib.auth import logout

def calculate_nepse_start_date(timeframe):
    today = datetime.today()
    if timeframe == "1M":
        return today - timedelta(days=30)
    elif timeframe == "6M":
        return today - timedelta(days=180)
    elif timeframe == "YTD":
        return datetime(today.year, 1, 1)
    elif timeframe == "1Y":
        return today - timedelta(days=365)
    elif timeframe == "5Y":
        return today - timedelta(days=5 * 365)
    elif timeframe == "10Y":
        return today - timedelta(days=10 * 365)
    return today - timedelta(days=30)



import os


import pandas as pd
from datetime import datetime

import json
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
import os, json
from .models import Stock


CSV_PATH = r"C:\Users\Bishal\Desktop\Final Project\StockSanket\merolagani_news.csv"

def mero_news_view(request):
    df = pd.read_csv(CSV_PATH)
    df = df.dropna(subset=["title", "link"])  # Ensure clean rows

    # Convert "date" to datetime safely
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Sort, drop invalid dates
    df = df.dropna(subset=["date"])
    df = df.sort_values(by="date", ascending=False)

    # Convert datetime to string before sending to template
    df["date"] = df["date"].dt.strftime("%Y-%m-%d %H:%M")

    # Build dictionary list
    # Add csv_index to each article
    articles = []
    for idx, row in df.iterrows():
        article = row.to_dict()
        article["csv_index"] = idx  # ✅ Add index
        articles.append(article)


    # Pagination (8 per page)
    paginator = Paginator(articles, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    trending = articles[:5]  # Just top 5 articles (no pagination)

    return render(request, "news.html", {
        "news": page_obj,
        "trending": trending
    })


def news_detail(request, news_id):
    df = pd.read_csv(CSV_PATH)
    df = df.dropna(subset=["link", "title", "date"]).reset_index(drop=True)

    try:
        article_data = df.iloc[int(news_id)]
        url = article_data["link"]

        response = requests.get(url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        img_tag = soup.find("img")
        featured_image_url = img_tag['src'] if img_tag else None

        content_div = soup.find("div", id="ctl00_ContentPlaceHolder1_newsDetail")
        content_html = content_div.decode_contents() if content_div else "Content not available"

        context = {
            "article": {
                "title": article_data["title"],
                "date": article_data["date"], 
                "content": content_html,
                "image_url": featured_image_url
            }
        }

        return render(request, "news_detail.html", context)

    except Exception as e:
        return render(request, "news_detail.html", {
            "article": {
                "title": "Error loading article",
                "date": "",
                "content": f"❌ Error: {str(e)}"
            }
        })


def compare_stocks_view(request):
    symbol = request.GET.get("symbol", "").upper()
    timeframe = request.GET.get("timeframe", "10Y")

    # ✅ Load from local CSV instead of API
    historical_data = []
    csv_path = os.path.join(BASE_DIR, "stock_history", f"{symbol.upper()}.csv")

    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            df["date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["date"])

            # Rename columns to match HTML keys
            df = df.rename(columns={
                "Open": "open_price",
                "High": "high_price",
                "Low": "low_price",
                "Close": "close_price",
                "% change": "adj_close_price",  # or keep as-is if % change
                "Volume": "volume"
            })

            historical_data = df.to_dict(orient="records")
        except Exception as e:
            print("⚠️ CSV read error:", e)
    else:
        print(f"❌ No CSV found for {symbol}")


    return render(request, "compares.html", {
        "symbol": symbol,
        "historical_data": historical_data,
        "timeframe": timeframe,
    })


from .models import Watchlist


@csrf_exempt
def add_to_watchlist(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            symbol = data.get("symbol")
            company = data.get("company")
            price = data.get("price")
            volume = data.get("volume")
            market_cap = data.get("market_cap")
            public_shares = data.get("public_shares")
            week_52 = data.get("week_52")

            print("🔍 Data received:", data)

            if Watchlist.objects.filter(symbol=symbol).exists():
                return JsonResponse({
                    "success": True,
                    "message": f"{symbol} is already in your watchlist."
                })

            Watchlist.objects.create(
                symbol=symbol,
                company=company,
                price=price,
                volume=volume,
                market_cap=int(float(str(market_cap).replace(",", ""))),  # 🛠 FIXED HERE
                public_shares=public_shares,
                week_52=week_52,
            )

            return JsonResponse({
                "success": True,
                "message": f"{symbol} was successfully added to your watchlist!"
            })

        except Exception as e:
            print("❌ Error adding to watchlist:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)



def watchlist_view(request):
    watchlist_stocks = Watchlist.objects.all()

    watchlist_data = []
    for stock in watchlist_stocks:
        watchlist_data.append({
            "symbol": stock.symbol,
            "company": stock.company,
            "price": stock.price or "N/A",
            "volume": stock.volume or "N/A",
            "public_shares": stock.public_shares or "N/A",
            "week_52": stock.week_52 or "N/A",
            "market_cap": stock.market_cap or "N/A",
        })

    return render(request, "watchlists.html", {"watchlist": watchlist_data})



@csrf_exempt
def remove_from_watchlist(request):
    """
    Removes a stock from the watchlist.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            symbol = data.get("symbol")

            Watchlist.objects.filter(symbol=symbol).delete()
            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


def fetch_blog_articles():
    """
    Fetches latest stock market blog articles from Yahoo Finance.
    """
    feed = feedparser.parse(YAHOO_FINANCE_BLOG_RSS)

    articles = []
    for entry in feed.entries[:12]:  # Fetch latest 12 articles for grid layout
        image_url = None
        if "media_content" in entry:
            image_url = entry.media_content[0]["url"] if entry.media_content else None

        articles.append({
            "title": entry.title,
            "link": entry.link,
            "image": image_url,
            "summary": entry.summary if "summary" in entry else "No summary available.",
            "author": entry.author if "author" in entry else "Unknown",
            "published_date": entry.published
        })

    return articles

def blog_articles_view(request):
    """
    View to display latest blog articles.
    """
    articles = fetch_blog_articles()
    return render(request, "articles.html", {
        "articles": articles
    })



def StocksView(request):
    stocks = Stock.objects.all()
    paginator = Paginator(stocks, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "stocks.html", {"stocks": page_obj})


def get_stock_data(request, symbol):
    try:
        symbol = symbol.upper()
        timeframe = request.GET.get("timeframe", "1Y")
        start_date = calculate_nepse_start_date(timeframe)

        csv_path = os.path.join(BASE_DIR, "stock_history", f"{symbol}.csv")
        if not os.path.exists(csv_path):
            return JsonResponse({"error": f"No CSV found for {symbol}"}, status=404)

        df = pd.read_csv(csv_path)

        # Clean & transform
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date", "Close"])
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Close"])

        df = df[df["Date"] >= start_date]
        df = df.sort_values("Date")

        # Format output
        dates = df["Date"].dt.strftime("%Y-%m-%d").tolist()
        prices = df["Close"].tolist()

        # Load stock company name (optional fallback)
        company = Stock.objects.filter(symbol=symbol).first()
        company_name = company.company if company else "N/A"

        return JsonResponse({
            "symbol": symbol,
            "dates": dates,
            "prices": prices,
            "company": company_name,
            "market_cap": "N/A",
            "price": prices[-1] if prices else "N/A",
            "change": round(prices[-1] - prices[-2], 2) if len(prices) >= 2 else "N/A",
            "volume": "N/A",
            "pe_ratio": "N/A",
        })

    except Exception as e:
        print("❌ Error in get_stock_data (CSV):", e)
        return JsonResponse({"error": "Internal server error"}, status=500)


import os
import json
import pandas as pd
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Stock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import os, json
import pandas as pd
from .models import Stock

def get_csv_index_from_link(link):
    CSV_PATHs = r"C:\Users\Bishal\Desktop\Final Project\StockSanket\merolagani_news.csv"
    try:
        
        df = pd.read_csv(CSV_PATHs)
        df = df.dropna(subset=["link"]).reset_index()
        row = df[df["link"] == link].iloc[0]
        return int(row["index"])
    except:
        return None
    
import os
import json

import os
import json

def get_prediction_chart_data(symbol):
    import tensorflow as tf
    file_path = os.path.join(BASE_DIR, "predictions", symbol.upper(), f"{symbol.upper()}.json")

    print("📁 Trying to load prediction JSON from:", file_path)

    if not os.path.exists(file_path):
        print("❌ File does NOT exist.")
        return []

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            print("✅ JSON file loaded. Keys:", data.keys())

        # Make sure both keys exist
        past = data.get("past_30_days", [])
        predicted = data.get("predicted_7_days", [])

        if not past and not predicted:
            print("⚠️ No 'past_30_days' or 'predicted_7_days' in JSON.")
            return []

        chart_data = []

        for item in past:
            if "date" in item:
                chart_data.append({
                    "time": int(datetime.strptime(item["date"], "%Y-%m-%d").timestamp()),
                    "open": item.get("open"),
                    "high": item.get("high"),
                    "low": item.get("low"),
                    "close": item.get("close"),
                    "predicted": False
                })

        for item in predicted:
            if "date" in item:
                chart_data.append({
                    "time": int(datetime.strptime(item["date"], "%Y-%m-%d").timestamp()),
                    "open": item.get("open"),
                    "high": item.get("high"),
                    "low": item.get("low"),
                    "close": item.get("close"),
                    "predicted": True
                })


        print(f"✅ Final chart data length: {len(chart_data)}")
        return chart_data

    except Exception as e:
        print(f"❌ Error loading or parsing prediction JSON: {e}")
        return []



from django.utils.safestring import mark_safe


def StockDetail(request, symbol):
    import tensorflow as tf
    try:
        stock_data = Stock.objects.filter(symbol=symbol.upper()).first()
        if not stock_data or not stock_data.company_id:
            return render(request, "stockDetail.html", {"error": "Stock or company ID not found"})

        company_id = stock_data.company_id
        live_data = scrape_stock_data_from_nepalstock(company_id)
        if not live_data:
            return render(request, "stockDetail.html", {"error": "Failed to fetch live NEPSE data."})

        try:
            last_price = float(live_data.get("last_price", "0").replace(",", ""))
            previous_close = float(live_data.get("previous_close", "0").replace(",", ""))
            price_change = round(last_price - previous_close, 2)
            percentage_change = round((price_change / previous_close) * 100, 2) if previous_close != 0 else 0
        except Exception as e:
            print("⚠️ Price calculation error:", e)
            last_price, price_change, percentage_change = 0, "-", "-"

        stock_info = {
            "symbol": stock_data.symbol,
            "company": stock_data.company,
            "price": last_price,
            "price_change": price_change,
            "percentage_change": percentage_change,
            "volume": live_data.get("volume", "N/A"),
            "previous_close": live_data.get("previous_close", "N/A"),
            "high_low": live_data.get("high_low", "N/A"),
            "week_52": live_data.get("week_52", "N/A"),
            "open_price": live_data.get("open_price", "N/A"),
            "close_price": live_data.get("close_price", "N/A"),
            "trades": live_data.get("trades", "N/A"),
            "market_cap": live_data.get("market_cap", "N/A"),
            "public_shares": live_data.get("public_shares", "N/A"),
            "promoter_shares": live_data.get("promoter_shares", "N/A"),
            "share_registrar": live_data.get("share_registrar", "N/A"),
            "todays_amount": "N/A",
            "date": datetime.today().strftime("%Y-%m-%d"),
            "currency": "NPR",
        }

        # Load and clean chart data for overview
        historical_chart_data = []
        df = pd.DataFrame()
        csv_path = os.path.join(BASE_DIR, "stock_history", f"{symbol.upper()}.csv")
        try:
            df = pd.read_csv(csv_path)
            df.rename(columns={"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close"}, inplace=True)
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
            df.dropna(subset=["date", "open", "high", "low", "close"], inplace=True)
            df.sort_values("date", inplace=True)
            df.drop_duplicates(subset=["date"], keep="first", inplace=True)

            for _, row in df.iterrows():
                if all(x > 0 and pd.notna(x) for x in [row["open"], row["high"], row["low"], row["close"]]):
                    historical_chart_data.append({
                        "time": int(row["date"].timestamp()),
                        "open": round(row["open"], 2),
                        "high": round(row["high"], 2),
                        "low": round(row["low"], 2),
                        "close": round(row["close"], 2),
                    })
        except Exception as e:
            print("⚠️ Error loading CSV for chart data:", e)

        print("✅ Chart data count:", len(historical_chart_data))

        # Historical table for history tab
        historical_data = []
        try:
            df2 = pd.read_csv(csv_path)
            df2["date"] = pd.to_datetime(df2["Date"], errors="coerce")
            df2 = df2.dropna(subset=["date"])
            df2 = df2.rename(columns={
                "Open": "open_price",
                "High": "high_price",
                "Low": "low_price",
                "Close": "close_price",
                "% change": "adj_close_price",
                "Volume": "volume"
            })
            historical_data = df2.to_dict(orient="records")
        except Exception as e:
            print("⚠️ CSV read error:", e)

        # Load sentiment
        sentiment = {}
        sentiment_path = os.path.join(BASE_DIR, "sentiment_data", "sentiment_all_stocks.json")
        try:
            with open(sentiment_path, "r", encoding="utf-8") as f:
                all_sentiments = json.load(f)
                sentiment = all_sentiments.get("stocks", {}).get(symbol.upper(), {})
        except Exception as e:
            print("⚠️ Sentiment file error:", e)

        # Top & extra news
        top_news, extra_articles = [], []
        if sentiment.get("top_positive_news", {}).get("title"):
            top_news.append({
                "title": sentiment["top_positive_news"]["title"],
                "link": sentiment["top_positive_news"]["link"],
                "timestamp": sentiment["top_positive_news"].get("date_str", ""),
                "tag": "positive"
            })
        if sentiment.get("top_negative_news", {}).get("title"):
            top_news.append({
                "title": sentiment["top_negative_news"]["title"],
                "link": sentiment["top_negative_news"]["link"],
                "timestamp": sentiment["top_negative_news"].get("date_str", ""),
                "tag": "negative"
            })

        shown_links = {a["link"] for a in top_news}
        for a in sentiment.get("articles", []):
            if a.get("link") not in shown_links and len(extra_articles) < 5:
                extra_articles.append({
                    "title": a.get("title", ""),
                    "link": a.get("link", "#"),
                    "timestamp": a.get("date", ""),
                    "tag": a.get("sentiment", "")
                })

        # 🛠 Add CSV Indexes to top_news & extra_articles
        for article in top_news + extra_articles:
            article["csv_index"] = get_csv_index_from_link(article["link"])

        # Sentiment Scores
        positive_percent = float(sentiment.get("positive_percent", 0))
        neutral_percent = float(sentiment.get("neutral_percent", 0))
        negative_percent = float(sentiment.get("negative_percent", 0))
        sentiment_scores = [
            ("positive", positive_percent),
            ("neutral", neutral_percent),
            ("negative", negative_percent),
        ]
        top_sentiment_label, top_sentiment_value = max(sentiment_scores, key=lambda x: x[1])
        is_in_watchlist = False
        if request.user.is_authenticated:
            is_in_watchlist = Watchlist.objects.filter(symbol=symbol.upper()).exists()


           
        # 🔶 1. Load prediction JSON and create prediction_chart_data
        prediction_chart_data = get_prediction_chart_data(symbol)

        predicted_data = [
            {
                "date": datetime.fromtimestamp(item["time"]).strftime("%B %d, %Y"),
                "close": round(item["close"], 2)
            }
            for item in prediction_chart_data if item.get("predicted")
        ]


        context = {
            "stock": stock_info,
            "historical_data": historical_data,  # history tab
            "historical_chart_data": json.dumps(historical_chart_data),  # overview chart
            "positive_percent": positive_percent,
            "neutral_percent": neutral_percent,
            "negative_percent": negative_percent,
            "sentiment_label": sentiment.get("sentiment_label", "N/A"),
            "bar_labels": json.dumps(sentiment.get("bar_labels", [])),
            "bar_data": {
                "positive": json.dumps(sentiment.get("bar_data", {}).get("positive", [])),
                "neutral": json.dumps(sentiment.get("bar_data", {}).get("neutral", [])),
                "negative": json.dumps(sentiment.get("bar_data", {}).get("negative", [])),
            },
            "line_sentiment_scores": json.dumps(sentiment.get("line_sentiment_scores", [])),
            "line_sentiment_labels": json.dumps(sentiment.get("line_sentiment_labels", [])),
            "top_news": top_news,
            "extra_news": extra_articles,
            "total_articles": sentiment.get("total_articles", 0),
            "last_updated": sentiment.get("last_updated", "N/A"),
            "top_sentiment_label": top_sentiment_label,
            "top_sentiment_value": top_sentiment_value,
            "is_in_watchlist": is_in_watchlist,
            "prediction_chart_data": json.dumps(prediction_chart_data),
            "predicted_data": predicted_data,

        }



        return render(request, "stockDetail.html", context)

    except Exception as e:
        print("❌ Error in StockDetail view:", e)
        return render(request, "stockDetail.html", {"error": "Something went wrong while fetching stock details."})
