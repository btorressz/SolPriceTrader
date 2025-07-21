"""
Web dashboard for the SOL/USDC Mean Reversion Trading Simulator
"""

from flask import Flask, render_template, jsonify, request
import json
import csv
import os
from datetime import datetime
import threading
import time
from data_fetcher import JupiterDataFetcher
from portfolio import Portfolio
from utils import calculate_moving_average

app = Flask(__name__)

class WebTradingDashboard:
    def __init__(self):
        self.data_fetcher = JupiterDataFetcher()
        self.portfolio = Portfolio(10000)
        self.price_history = []
        self.ma_history = []
        self.trades = []
        self.current_price = 0
        self.current_ma = 0
        self.position = 'cash'
        self.ma_period = 20
        self.is_running = False
        self.auto_trading = False
        self.slippage_rate = 0.001
        self.fetch_interval = 30
        
        # Find the most recent CSV file
        self.csv_filename = self.find_latest_csv()
        
        # Start background data fetching
        self.start_data_fetching()
        
    def find_latest_csv(self):
        """Find the most recent trades CSV file"""
        csv_files = [f for f in os.listdir('.') if f.startswith('trades_') and f.endswith('.csv')]
        if csv_files:
            return max(csv_files, key=os.path.getctime)
        return None
    
    def start_data_fetching(self):
        """Start background data fetching thread"""
        def fetch_data():
            while True:
                try:
                    # Get latest price
                    price = self.data_fetcher.get_sol_usdc_price()
                    if price:
                        self.current_price = price
                        self.price_history.append(price)
                        
                        # Keep only last 100 points for performance
                        if len(self.price_history) > 100:
                            self.price_history = self.price_history[-100:]
                        
                        # Calculate moving average
                        if len(self.price_history) >= self.ma_period:
                            ma_value = calculate_moving_average(self.price_history, self.ma_period)
                            if ma_value:
                                self.current_ma = ma_value
                                self.ma_history.append(ma_value)
                                
                                if len(self.ma_history) > 100:
                                    self.ma_history = self.ma_history[-100:]
                                
                                # Auto trading logic
                                if self.auto_trading:
                                    self.check_and_execute_trades()
                    
                    time.sleep(self.fetch_interval)
                except Exception as e:
                    print(f"Error in data fetching: {e}")
                    time.sleep(30)
        
        # Start thread
        thread = threading.Thread(target=fetch_data, daemon=True)
        thread.start()
    
    def check_and_execute_trades(self):
        """Check trading signals and execute trades if auto trading is enabled"""
        if not self.current_price or not self.current_ma:
            return
            
        # Mean reversion logic
        if self.current_price < self.current_ma and self.position == 'cash':
            self.execute_trade('buy')
        elif self.current_price > self.current_ma and self.position == 'sol':
            self.execute_trade('sell')
    
    def execute_trade(self, action):
        """Execute a trade (buy or sell)"""
        try:
            if action == 'buy' and self.position == 'cash':
                # Buy SOL with available cash
                available_cash = self.portfolio.cash
                if available_cash > 0:
                    # Calculate slippage
                    slippage = self.current_price * self.slippage_rate
                    effective_price = self.current_price + slippage
                    
                    # Calculate quantity
                    quantity = available_cash / effective_price
                    
                    # Execute trade
                    self.portfolio.buy_sol(quantity, effective_price)
                    self.position = 'sol'
                    
                    # Log trade
                    self.log_trade('BUY', effective_price, quantity, slippage, 0)
                    
            elif action == 'sell' and self.position == 'sol':
                # Sell all SOL
                sol_quantity = self.portfolio.sol_quantity
                if sol_quantity > 0:
                    # Calculate slippage
                    slippage = self.current_price * self.slippage_rate
                    effective_price = self.current_price - slippage
                    
                    # Calculate PnL
                    cost_basis = self.portfolio.sol_cost_basis
                    pnl = (effective_price - cost_basis) * sol_quantity
                    
                    # Execute trade
                    self.portfolio.sell_sol(sol_quantity, effective_price)
                    self.position = 'cash'
                    
                    # Log trade
                    self.log_trade('SELL', effective_price, sol_quantity, slippage, pnl)
                    
        except Exception as e:
            print(f"Error executing trade: {e}")
    
    def log_trade(self, action, price, quantity, slippage, pnl):
        """Log trade to CSV and memory"""
        timestamp = datetime.now().isoformat()
        total_value = self.portfolio.get_total_value(self.current_price)
        cumulative_pnl = total_value - 10000
        
        trade = {
            'timestamp': timestamp,
            'action': action,
            'price': price,
            'quantity': quantity,
            'slippage': slippage,
            'total_value': total_value,
            'pnl': pnl,
            'cumulative_pnl': cumulative_pnl,
            'ma_value': self.current_ma
        }
        
        self.trades.append(trade)
        
        # Write to CSV
        if not self.csv_filename:
            self.csv_filename = f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            # Create CSV with headers
            with open(self.csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'action', 'price', 'quantity', 'slippage', 
                               'total_value', 'pnl', 'cumulative_pnl', 'ma_value'])
        
        # Append trade
        with open(self.csv_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([timestamp, action, price, quantity, slippage,
                           total_value, pnl, cumulative_pnl, self.current_ma])

    def load_existing_data(self):
        """Load existing trade data from CSV"""
        if not self.csv_filename or not os.path.exists(self.csv_filename):
            return
            
        try:
            with open(self.csv_filename, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    trade = {
                        'timestamp': row['timestamp'],
                        'action': row['action'],
                        'price': float(row['price']),
                        'quantity': float(row['quantity']),
                        'slippage': float(row['slippage']),
                        'total_value': float(row['total_value']),
                        'pnl': float(row['pnl']),
                        'cumulative_pnl': float(row['cumulative_pnl']),
                        'ma_value': float(row['ma_value'])
                    }
                    self.trades.append(trade)
        except Exception as e:
            print(f"Error loading existing data: {e}")
    
    def get_dashboard_data(self):
        """Get current dashboard data"""
        # Portfolio stats
        portfolio_value = self.portfolio.get_total_value(self.current_price)
        total_pnl = portfolio_value - 10000
        
        return {
            'current_price': self.current_price,
            'current_ma': self.current_ma,
            'portfolio_value': portfolio_value,
            'total_pnl': total_pnl,
            'position': self.position,
            'price_history': self.price_history[-50:],  # Last 50 points
            'ma_history': self.ma_history[-50:],
            'trades': self.trades[-20:],  # Last 20 trades
            'total_trades': len(self.trades),
            'csv_file': self.csv_filename,
            'auto_trading': self.auto_trading,
            'ma_period': self.ma_period,
            'slippage_rate': self.slippage_rate,
            'fetch_interval': self.fetch_interval
        }

# Initialize dashboard
dashboard = WebTradingDashboard()
dashboard.load_existing_data()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint for dashboard data"""
    return jsonify(dashboard.get_dashboard_data())

@app.route('/api/trades')
def get_trades():
    """API endpoint for trade history"""
    return jsonify({
        'trades': dashboard.trades,
        'total_trades': len(dashboard.trades)
    })

@app.route('/api/control', methods=['POST'])
def control_trading():
    """API endpoint for trading controls"""
    data = request.json
    action = data.get('action')
    
    if action == 'toggle_auto_trading':
        dashboard.auto_trading = not dashboard.auto_trading
        return jsonify({
            'success': True,
            'auto_trading': dashboard.auto_trading,
            'message': f"Auto trading {'enabled' if dashboard.auto_trading else 'disabled'}"
        })
    
    elif action == 'manual_buy':
        if dashboard.position == 'cash' and dashboard.current_price > 0:
            dashboard.execute_trade('buy')
            return jsonify({
                'success': True,
                'message': 'Manual BUY order executed'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Cannot buy: Already holding SOL or no price data'
            })
    
    elif action == 'manual_sell':
        if dashboard.position == 'sol' and dashboard.current_price > 0:
            dashboard.execute_trade('sell')
            return jsonify({
                'success': True,
                'message': 'Manual SELL order executed'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Cannot sell: No SOL holdings or no price data'
            })
    
    elif action == 'update_settings':
        if 'ma_period' in data:
            dashboard.ma_period = max(5, min(50, int(data['ma_period'])))
        if 'slippage_rate' in data:
            dashboard.slippage_rate = max(0.001, min(0.01, float(data['slippage_rate'])))
        if 'fetch_interval' in data:
            dashboard.fetch_interval = max(10, min(300, int(data['fetch_interval'])))
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully',
            'settings': {
                'ma_period': dashboard.ma_period,
                'slippage_rate': dashboard.slippage_rate,
                'fetch_interval': dashboard.fetch_interval
            }
        })
    
    elif action == 'reset_portfolio':
        dashboard.portfolio = Portfolio(10000)
        dashboard.position = 'cash'
        dashboard.trades = []
        dashboard.csv_filename = None
        return jsonify({
            'success': True,
            'message': 'Portfolio reset to $10,000'
        })
    
    return jsonify({
        'success': False,
        'message': 'Unknown action'
    })

if __name__ == '__main__':
    print("Starting SOL/USDC Trading Dashboard...")
    print("Dashboard will be available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)