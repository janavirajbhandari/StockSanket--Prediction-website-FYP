import os
import json
import nbformat
from datetime import datetime
from nbconvert.preprocessors import ExecutePreprocessor

# Define folders
stock_history_dir = "stock_history"
output_folder = "stock_prediction"
os.makedirs(output_folder, exist_ok=True)

# Load the original notebook ONCE
with open("StockForecastNotebook_Modified.ipynb", encoding='utf-8') as f:
    original_nb = nbformat.read(f, as_version=4)

# Loop through all stock CSVs
for file in os.listdir(stock_history_dir):
    if not file.endswith(".csv"):
        continue

    symbol = file.replace(".csv", "")
    csv_path = os.path.join(stock_history_dir, file)

    # Create a subfolder for each stock
    stock_output_dir = os.path.join(output_folder, symbol)
    os.makedirs(stock_output_dir, exist_ok=True)

    print(f"📊 Running prediction for {symbol}...")

    # Copy notebook and inject variables
    nb = nbformat.from_dict(original_nb)

    # Inject a new cell at the top with the right variables
    injected_code = f"""
symbol = "{symbol}"
csv_path = r"{csv_path}"
output_dir = r"{stock_output_dir}"
"""
    injected_cell = nbformat.v4.new_code_cell(source=injected_code)
    nb.cells.insert(0, injected_cell)

    ep = ExecutePreprocessor(timeout=3600, kernel_name='py311-stock')

    try:
        ep.preprocess(nb, {'metadata': {'path': '.'}})
        print(f"✅ {symbol} complete!")
    except Exception as e:
        print(f"❌ Error running {symbol}: {e}")
