"""
Main trading simulator class that orchestrates the mean reversion trading strategy
"""

import time
import csv
import os
from datetime import datetime
from data_fetcher import JupiterDataFetcher
from portfolio import Portfolio
from visualizer import TradingVisualizer
from utils import calculate_moving_average, format_currency

class TradingSimulator:
    """Main trading simulator implementing mean reversion strategy"""
    
    def __init__(self, initial_cash=10000, ma_period=20, fetch_interval=30, slippage_rate=0.001):
        self.initial_cash = initial_cash
        self.ma_period = ma_period
        self.fetch_interval = fetch_interval
        self.slippage_rate = slippage_rate
        
        # Initialize components
        self.data_fetcher = JupiterDataFetcher()
        self.portfolio = Portfolio(initial_cash)
        self.visualizer = TradingVisualizer()
        
        # Trading state
        self.price_history = []
        self.ma_history = []
        self.trades = []
        self.position = 'cash'  # 'cash' or 'sol'
        
        # CSV file for logging trades
        self.csv_filename = f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.init_csv_file()
        
        print(f"Initialized trading simulator with:")
        print(f"  Initial Cash: ${initial_cash:,.2f}")
        print(f"  MA Period: {ma_period}")
        print(f"  Fetch Interval: {fetch_interval}s")
        print(f"  Slippage Rate: {slippage_rate*100:.2f}%")
        print(f"  Trade Log: {self.csv_filename}")
        print()
    
    def init_csv_file(self):
        """Initialize CSV file with headers"""
        headers = [
            'timestamp', 'action', 'price', 'quantity', 'slippage', 
            'total_value', 'pnl', 'cumulative_pnl', 'ma_value'
        ]
        
        with open(self.csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
    
    def log_trade(self, action, price, quantity, slippage, total_value, pnl, cumulative_pnl, ma_value):
        """Log trade details to CSV file"""
        timestamp = datetime.now().isoformat()
        
        trade_data = [
            timestamp, action, price, quantity, slippage,
            total_value, pnl, cumulative_pnl, ma_value
        ]
        
        with open(self.csv_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(trade_data)
        
        # Also store in memory for visualization
        self.trades.append({
            'timestamp': timestamp,
            'action': action,
            'price': price,
            'quantity': quantity,
            'slippage': slippage,
            'total_value': total_value,
            'pnl': pnl,
            'cumulative_pnl': cumulative_pnl,
            'ma_value': ma_value
        })
    
    def execute_trade(self, action, current_price, ma_value):
        """Execute a trade based on the mean reversion strategy"""
        if action == 'buy' and self.position == 'cash':
            # Buy SOL with available cash
            available_cash = self.portfolio.cash
            if available_cash > 0:
                # Calculate slippage
                slippage = current_price * self.slippage_rate
                effective_price = current_price + slippage
                
                # Calculate quantity of SOL to buy
                quantity = available_cash / effective_price
                
                # Execute the trade
                self.portfolio.buy_sol(quantity, effective_price)
                self.position = 'sol'
                
                # Calculate PnL (0 for buy trades)
                pnl = 0
                cumulative_pnl = self.portfolio.get_total_value(current_price) - self.initial_cash
                
                # Log the trade
                self.log_trade('BUY', effective_price, quantity, slippage, 
                             self.portfolio.get_total_value(current_price), 
                             pnl, cumulative_pnl, ma_value)
                
                print(f"🟢 BUY  | SOL: {quantity:.4f} @ ${effective_price:.4f} | "
                      f"Slippage: ${slippage:.4f} | Total: ${self.portfolio.get_total_value(current_price):.2f}")
        
        elif action == 'sell' and self.position == 'sol':
            # Sell all SOL for cash
            sol_quantity = self.portfolio.sol_quantity
            if sol_quantity > 0:
                # Calculate slippage
                slippage = current_price * self.slippage_rate
                effective_price = current_price - slippage
                
                # Calculate PnL
                cost_basis = self.portfolio.sol_cost_basis
                pnl = (effective_price - cost_basis) * sol_quantity
                
                # Execute the trade
                self.portfolio.sell_sol(sol_quantity, effective_price)
                self.position = 'cash'
                
                cumulative_pnl = self.portfolio.get_total_value(current_price) - self.initial_cash
                
                # Log the trade
                self.log_trade('SELL', effective_price, sol_quantity, slippage,
                             self.portfolio.get_total_value(current_price),
                             pnl, cumulative_pnl, ma_value)
                
                print(f"🔴 SELL | SOL: {sol_quantity:.4f} @ ${effective_price:.4f} | "
                      f"Slippage: ${slippage:.4f} | PnL: {format_currency(pnl)} | "
                      f"Total: ${self.portfolio.get_total_value(current_price):.2f}")
    
    def check_trading_signal(self, current_price, ma_value):
        """Check if we should buy or sell based on mean reversion strategy"""
        if current_price < ma_value and self.position == 'cash':
            return 'buy'
        elif current_price > ma_value and self.position == 'sol':
            return 'sell'
        return None
    
    def display_status(self, current_price, ma_value):
        """Display current trading status"""
        total_value = self.portfolio.get_total_value(current_price)
        cumulative_pnl = total_value - self.initial_cash
        
        print(f"📊 Price: ${current_price:.4f} | MA: ${ma_value:.4f} | "
              f"Position: {self.position.upper()} | "
              f"Total: ${total_value:.2f} | "
              f"PnL: {format_currency(cumulative_pnl)}")
    
    def run(self):
        """Main simulation loop"""
        print("Starting simulation...")
        print("Waiting for initial data to calculate moving average...")
        
        while True:
            try:
                # Fetch current price
                current_price = self.data_fetcher.get_sol_usdc_price()
                
                if current_price is None:
                    print("❌ Failed to fetch price, retrying in 30 seconds...")
                    time.sleep(self.fetch_interval)
                    continue
                
                # Add to price history
                self.price_history.append(current_price)
                
                # Calculate moving average if we have enough data
                if len(self.price_history) >= self.ma_period:
                    ma_value = calculate_moving_average(self.price_history, self.ma_period)
                    self.ma_history.append(ma_value)
                    
                    # Check for trading signals
                    signal = self.check_trading_signal(current_price, ma_value)
                    
                    if signal:
                        self.execute_trade(signal, current_price, ma_value)
                    
                    # Display current status
                    self.display_status(current_price, ma_value)
                    
                    # Update visualization every 10 data points
                    if len(self.price_history) % 10 == 0:
                        self.visualizer.update_plot(
                            self.price_history[-100:],  # Last 100 prices
                            self.ma_history[-100:],     # Last 100 MA values
                            self.trades[-20:] if len(self.trades) > 20 else self.trades  # Last 20 trades
                        )
                
                else:
                    remaining = self.ma_period - len(self.price_history)
                    print(f"📈 Price: ${current_price:.4f} | "
                          f"Collecting data... ({remaining} more needed for MA)")
                
                # Wait for next fetch
                time.sleep(self.fetch_interval)
                
            except Exception as e:
                print(f"❌ Error in simulation loop: {e}")
                print("Retrying in 30 seconds...")
                time.sleep(self.fetch_interval)
