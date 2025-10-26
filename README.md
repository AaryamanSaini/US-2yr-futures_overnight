# US 2-Year Futures Dashboard

A simple dashboard for analyzing US 2-Year futures data with a focus on overnight trading sessions.

## Features

### Main Dashboard (`dashboard.py`)
- **Simple Interface**: Clean and straightforward design
- **Relative Yield Chart**: Shows yield fluctuations across different trading sessions
- **Key Metrics Display**: 
  - Current 2-Year Yield with latest date and change
  - 2s10s Spread (difference between 2-year and 10-year yields)
  - 1-Month Volatility (rolling σ of daily yield changes)
  - Fed Funds Upper Bound (current policy rate)
- **Interactive Visualization**: Hover to see detailed information

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Run the Dashboard
```bash
python3 dashboard.py
```

Then open your browser to `http://localhost:8050`

The dashboard will show:
- Key metrics at the top (Current 2-Year Yield, 2s10s Spread, Volatility, Fed Funds Rate)
- Interactive chart showing relative yield over time for the latest 6 trading sessions
- Average yield line (black dashed)

## Data Format

The CSV file should contain:
- `Date`: DateTime column with timestamps
- `Lst Trd/Lst Px`: Last trade price (fractional notation)
- `Decimal`: Decimal price values

## Key Metrics Explained

1. **Current 2-Year Yield**: Latest value of the 2-year treasury futures yield
2. **2s10s Spread**: The yield difference between 2-year and 10-year treasuries (key indicator)
3. **1-Month Volatility**: Annualized volatility calculated from daily yield changes over the past month
4. **Fed Funds Upper Bound**: Current upper bound of the Federal Reserve's target range

## Technical Details

- **Backend**: Python with Pandas for data processing
- **Frontend**: Plotly Dash for interactive visualizations
- **Data Processing**: Automatic overnight session detection (18:00-08:00)
- **Relative Yield**: Calculated as deviation from session start