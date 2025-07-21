#!/usr/bin/env python3
"""
Main entry point for the SOL/USDC Mean Reversion Trading Simulator
"""

import time
import signal
import sys
from trading_simulator import TradingSimulator

def signal_handler(sig, frame):
    """Handle graceful shutdown on Ctrl+C"""
    print('\n\nShutting down trading simulator...')
    sys.exit(0)

def main():
    """Main function to run the trading simulator"""
    print("=" * 60)
    print("SOL/USDC Mean Reversion Trading Simulator")
    print("=" * 60)
    print("Press Ctrl+C to stop the simulation")
    print("-" * 60)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize the trading simulator
    simulator = TradingSimulator(
        initial_cash=10000,  # Start with $10,000 USDC
        ma_period=20,        # 20-period moving average
        fetch_interval=30,   # Fetch every 30 seconds
        slippage_rate=0.001  # 0.1% slippage
    )
    
    try:
        # Start the simulation
        simulator.run()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
