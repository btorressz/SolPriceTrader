"""
Portfolio management for tracking cash, SOL holdings, and calculating PnL
"""

from datetime import datetime

class Portfolio:
    """Manages portfolio state including cash and SOL holdings"""
    
    def __init__(self, initial_cash):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.sol_quantity = 0.0
        self.sol_cost_basis = 0.0  # Average cost per SOL
        self.trades_count = 0
        
        print(f"Portfolio initialized with ${initial_cash:,.2f} USDC")
    
    def buy_sol(self, quantity, price):
        """Buy SOL with available cash"""
        total_cost = quantity * price
        
        if total_cost > self.cash:
            raise ValueError(f"Insufficient cash: ${self.cash:.2f} < ${total_cost:.2f}")
        
        # Update cash and SOL holdings
        self.cash -= total_cost
        
        # Calculate new cost basis (weighted average)
        if self.sol_quantity > 0:
            total_sol_value = (self.sol_quantity * self.sol_cost_basis) + total_cost
            self.sol_quantity += quantity
            self.sol_cost_basis = total_sol_value / self.sol_quantity
        else:
            self.sol_quantity = quantity
            self.sol_cost_basis = price
        
        self.trades_count += 1
        
        return {
            'action': 'buy',
            'quantity': quantity,
            'price': price,
            'total_cost': total_cost,
            'remaining_cash': self.cash,
            'sol_holdings': self.sol_quantity
        }
    
    def sell_sol(self, quantity, price):
        """Sell SOL for cash"""
        if quantity > self.sol_quantity:
            raise ValueError(f"Insufficient SOL: {self.sol_quantity:.4f} < {quantity:.4f}")
        
        total_proceeds = quantity * price
        
        # Update cash and SOL holdings
        self.cash += total_proceeds
        self.sol_quantity -= quantity
        
        # If all SOL is sold, reset cost basis
        if self.sol_quantity == 0:
            self.sol_cost_basis = 0.0
        
        self.trades_count += 1
        
        return {
            'action': 'sell',
            'quantity': quantity,
            'price': price,
            'total_proceeds': total_proceeds,
            'remaining_cash': self.cash,
            'sol_holdings': self.sol_quantity
        }
    
    def get_total_value(self, current_sol_price):
        """Calculate total portfolio value in USDC"""
        sol_value = self.sol_quantity * current_sol_price
        return self.cash + sol_value
    
    def get_unrealized_pnl(self, current_sol_price):
        """Calculate unrealized PnL on SOL holdings"""
        if self.sol_quantity == 0:
            return 0.0
        
        current_value = self.sol_quantity * current_sol_price
        cost_value = self.sol_quantity * self.sol_cost_basis
        return current_value - cost_value
    
    def get_total_pnl(self, current_sol_price):
        """Calculate total PnL (realized + unrealized)"""
        total_value = self.get_total_value(current_sol_price)
        return total_value - self.initial_cash
    
    def get_portfolio_summary(self, current_sol_price):
        """Get comprehensive portfolio summary"""
        total_value = self.get_total_value(current_sol_price)
        total_pnl = self.get_total_pnl(current_sol_price)
        unrealized_pnl = self.get_unrealized_pnl(current_sol_price)
        
        return {
            'cash': self.cash,
            'sol_quantity': self.sol_quantity,
            'sol_cost_basis': self.sol_cost_basis,
            'sol_current_price': current_sol_price,
            'sol_market_value': self.sol_quantity * current_sol_price,
            'total_value': total_value,
            'initial_cash': self.initial_cash,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / self.initial_cash) * 100,
            'unrealized_pnl': unrealized_pnl,
            'trades_count': self.trades_count
        }
    
    def print_summary(self, current_sol_price):
        """Print formatted portfolio summary"""
        summary = self.get_portfolio_summary(current_sol_price)
        
        print("\n" + "="*50)
        print("PORTFOLIO SUMMARY")
        print("="*50)
        print(f"Cash (USDC):      ${summary['cash']:>10,.2f}")
        print(f"SOL Holdings:     {summary['sol_quantity']:>10.4f}")
        print(f"SOL Cost Basis:   ${summary['sol_cost_basis']:>10.4f}")
        print(f"SOL Market Price: ${summary['sol_current_price']:>10.4f}")
        print(f"SOL Market Value: ${summary['sol_market_value']:>10.2f}")
        print("-"*50)
        print(f"Total Value:      ${summary['total_value']:>10.2f}")
        print(f"Initial Cash:     ${summary['initial_cash']:>10.2f}")
        print(f"Total P&L:        ${summary['total_pnl']:>10.2f}")
        print(f"Total P&L %:      {summary['total_pnl_pct']:>9.2f}%")
        print(f"Unrealized P&L:   ${summary['unrealized_pnl']:>10.2f}")
        print(f"Total Trades:     {summary['trades_count']:>10}")
        print("="*50)
