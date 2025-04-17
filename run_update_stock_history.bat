@echo off
cd /d "C:\Users\Bishal\Desktop\Final Project\StockSanket"
call venv\Scripts\activate
python manage.py update_stock_history
