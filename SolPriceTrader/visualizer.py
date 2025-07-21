"""
Real-time visualization of trading data using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

class TradingVisualizer:
    """Creates and updates real-time trading charts"""
    
    def __init__(self):
        # Set up the figure and subplots
        plt.ion()  # Turn on interactive mode
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 10))
        self.fig.suptitle('SOL/USDC Mean Reversion Trading Simulator', fontsize=16, fontweight='bold')
        
        # Initialize empty lines
        self.price_line, = self.ax1.plot([], [], 'b-', linewidth=2, label='SOL/USDC Price')
        self.ma_line, = self.ax1.plot([], [], 'r-', linewidth=2, label='20-Period MA')
        self.buy_markers, = self.ax1.plot([], [], '^', markersize=10, color='green', label='Buy')
        self.sell_markers, = self.ax1.plot([], [], 'v', markersize=10, color='red', label='Sell')
        
        # Configure first subplot (Price and MA)
        self.ax1.set_title('SOL/USDC Price and Moving Average')
        self.ax1.set_ylabel('Price (USDC)')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend()
        
        # Second subplot for cumulative PnL
        self.pnl_line, = self.ax2.plot([], [], 'g-', linewidth=2, label='Cumulative P&L')
        self.ax2.set_title('Cumulative P&L')
        self.ax2.set_xlabel('Time')
        self.ax2.set_ylabel('P&L (USDC)')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend()
        self.ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Data storage for plotting
        self.timestamps = []
        self.prices = []
        self.ma_values = []
        self.pnl_values = []
        self.buy_times = []
        self.buy_prices = []
        self.sell_times = []
        self.sell_prices = []
        
        plt.tight_layout()
        plt.show(block=False)
        
        print("📊 Trading visualizer initialized")
    
    def update_plot(self, price_history, ma_history, trades):
        """Update the trading chart with new data"""
        try:
            # Update price and MA data
            current_time = datetime.now()
            
            # Limit data to last 100 points for performance
            max_points = 100
            
            if len(price_history) > max_points:
                price_history = price_history[-max_points:]
                ma_history = ma_history[-max_points:]
            
            # Generate timestamps for price data
            time_interval = 30  # seconds
            timestamps = [
                datetime.fromtimestamp(current_time.timestamp() - (len(price_history) - i - 1) * time_interval)
                for i in range(len(price_history))
            ]
            
            # Update price and MA lines
            self.price_line.set_data(timestamps, price_history)
            if len(ma_history) > 0:
                ma_timestamps = timestamps[-len(ma_history):]
                self.ma_line.set_data(ma_timestamps, ma_history)
            
            # Update trade markers
            buy_times = []
            buy_prices = []
            sell_times = []
            sell_prices = []
            pnl_values = []
            
            for trade in trades:
                trade_time = datetime.fromisoformat(trade['timestamp'])
                if trade['action'] == 'BUY':
                    buy_times.append(trade_time)
                    buy_prices.append(trade['price'])
                elif trade['action'] == 'SELL':
                    sell_times.append(trade_time)
                    sell_prices.append(trade['price'])
                
                pnl_values.append(trade['cumulative_pnl'])
            
            # Update markers
            self.buy_markers.set_data(buy_times, buy_prices)
            self.sell_markers.set_data(sell_times, sell_prices)
            
            # Update PnL line
            if len(trades) > 0:
                trade_times = [datetime.fromisoformat(trade['timestamp']) for trade in trades]
                self.pnl_line.set_data(trade_times, pnl_values)
            
            # Auto-scale axes
            self.ax1.relim()
            self.ax1.autoscale_view()
            
            # Format x-axis for time
            self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            self.ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
            plt.setp(self.ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # Update PnL subplot
            if len(pnl_values) > 0:
                self.ax2.relim()
                self.ax2.autoscale_view()
                self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                self.ax2.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
                plt.setp(self.ax2.xaxis.get_majorticklabels(), rotation=45)
                
                # Color PnL line based on profit/loss
                if pnl_values[-1] >= 0:
                    self.pnl_line.set_color('green')
                else:
                    self.pnl_line.set_color('red')
            
            # Add current stats as text
            if len(price_history) > 0 and len(trades) > 0:
                current_price = price_history[-1]
                current_pnl = pnl_values[-1] if pnl_values else 0
                
                stats_text = f'Current Price: ${current_price:.4f}\n'
                stats_text += f'Current P&L: ${current_pnl:.2f}\n'
                stats_text += f'Total Trades: {len(trades)}'
                
                # Remove previous text if exists
                for txt in self.ax1.texts:
                    txt.remove()
                
                self.ax1.text(0.02, 0.98, stats_text, transform=self.ax1.transAxes,
                            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            plt.draw()
            plt.pause(0.01)  # Small pause to allow plot to update
            
        except Exception as e:
            print(f"❌ Error updating visualization: {e}")
    
    def save_chart(self, filename=None):
        """Save the current chart to a file"""
        if filename is None:
            filename = f"trading_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        try:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Chart saved as {filename}")
        except Exception as e:
            print(f"❌ Error saving chart: {e}")
    
    def close(self):
        """Close the visualization"""
        plt.close(self.fig)
        print("📊 Trading visualizer closed")
