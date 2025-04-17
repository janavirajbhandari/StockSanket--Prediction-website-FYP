from nepse import Nepse
def get_nepse_historical_data(symbol):
    from nepse import Nepse
    nepse = Nepse()
    nepse.setTLSVerification(False)
    
    # ❌ Remove or comment out this invalid line
    # history = nepse.getStockHistory(symbol)

    # ✅ This is your working mock data
    from datetime import timedelta, datetime
    import random

    today = datetime.today()
    historical_data = []

    for i in range(30):
        day = today - timedelta(days=i)
        open_price = round(random.uniform(400, 600), 2)
        high = open_price + round(random.uniform(1, 10), 2)
        low = open_price - round(random.uniform(1, 10), 2)
        close = round(random.uniform(low, high), 2)

        historical_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "open_price": open_price,
            "high_price": high,
            "low_price": low,
            "close_price": close,
            "adj_close_price": close,
            "volume": random.randint(1000, 5000),
        })

    return historical_data[::-1]  # Return in oldest to newest order
