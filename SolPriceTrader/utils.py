"""
Utility functions for the trading simulator
"""

import statistics
from datetime import datetime

def calculate_moving_average(prices, period):
    """Calculate simple moving average for the given period"""
    if len(prices) < period:
        return None
    
    return statistics.mean(prices[-period:])

def calculate_exponential_moving_average(prices, period, alpha=None):
    """Calculate exponential moving average"""
    if len(prices) < period:
        return None
    
    if alpha is None:
        alpha = 2 / (period + 1)
    
    ema = prices[0]
    for price in prices[1:]:
        ema = alpha * price + (1 - alpha) * ema
    
    return ema

def format_currency(amount, currency='$'):
    """Format currency amount with appropriate color coding"""
    if amount >= 0:
        return f"💚 {currency}{amount:,.2f}"
    else:
        return f"❤️ {currency}{amount:,.2f}"

def calculate_slippage(price, slippage_rate):
    """Calculate slippage amount"""
    return price * slippage_rate

def calculate_percentage_change(old_value, new_value):
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def timestamp_to_readable(timestamp):
    """Convert timestamp to readable format"""
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp)
    else:
        dt = datetime.fromtimestamp(timestamp)
    
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def validate_price(price):
    """Validate that price is a positive number"""
    if price is None:
        return False
    
    try:
        price = float(price)
        return price > 0
    except (ValueError, TypeError):
        return False

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio for the returns"""
    if len(returns) < 2:
        return 0
    
    excess_returns = [r - risk_free_rate/252 for r in returns]  # Daily risk-free rate
    
    if statistics.stdev(excess_returns) == 0:
        return 0
    
    return statistics.mean(excess_returns) / statistics.stdev(excess_returns)

def calculate_max_drawdown(pnl_values):
    """Calculate maximum drawdown from PnL values"""
    if len(pnl_values) < 2:
        return 0
    
    peak = pnl_values[0]
    max_drawdown = 0
    
    for pnl in pnl_values[1:]:
        if pnl > peak:
            peak = pnl
        
        drawdown = peak - pnl
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return max_drawdown

def calculate_win_rate(trades):
    """Calculate win rate from trade history"""
    if not trades:
        return 0
    
    profitable_trades = [trade for trade in trades if trade.get('pnl', 0) > 0]
    return len(profitable_trades) / len(trades) * 100

def get_trading_session_stats(trades):
    """Get comprehensive trading session statistics"""
    if not trades:
        return {}
    
    pnl_values = [trade.get('pnl', 0) for trade in trades if trade.get('pnl') is not None]
    cumulative_pnl = [trade.get('cumulative_pnl', 0) for trade in trades if trade.get('cumulative_pnl') is not None]
    
    return {
        'total_trades': len(trades),
        'win_rate': calculate_win_rate(trades),
        'total_pnl': cumulative_pnl[-1] if cumulative_pnl else 0,
        'max_drawdown': calculate_max_drawdown(cumulative_pnl),
        'avg_pnl_per_trade': statistics.mean(pnl_values) if pnl_values else 0,
        'best_trade': max(pnl_values) if pnl_values else 0,
        'worst_trade': min(pnl_values) if pnl_values else 0
    }

def print_trading_stats(trades):
    """Print formatted trading statistics"""
    stats = get_trading_session_stats(trades)
    
    print("\n" + "="*50)
    print("TRADING SESSION STATISTICS")
    print("="*50)
    print(f"Total Trades:      {stats.get('total_trades', 0):>10}")
    print(f"Win Rate:          {stats.get('win_rate', 0):>9.1f}%")
    print(f"Total P&L:         ${stats.get('total_pnl', 0):>10.2f}")
    print(f"Max Drawdown:      ${stats.get('max_drawdown', 0):>10.2f}")
    print(f"Avg P&L per Trade: ${stats.get('avg_pnl_per_trade', 0):>10.2f}")
    print(f"Best Trade:        ${stats.get('best_trade', 0):>10.2f}")
    print(f"Worst Trade:       ${stats.get('worst_trade', 0):>10.2f}")
    print("="*50)
