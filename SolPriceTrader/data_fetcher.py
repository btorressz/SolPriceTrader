"""
Data fetcher for Jupiter API to get SOL/USDC prices
"""

import requests
import json
import time
from datetime import datetime

class JupiterDataFetcher:
    """Fetches SOL/USDC price data from Jupiter API"""
    
    def __init__(self):
        self.base_url = "https://quote-api.jup.ag/v6/quote"
        self.sol_mint = "So11111111111111111111111111111111111111112"  # SOL mint address
        self.usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC mint address
        self.amount = 1000000000  # 1 SOL in lamports (1 SOL = 1e9 lamports)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1  # Minimum 1 second between requests
        
        print(f"Initialized Jupiter data fetcher")
        print(f"  SOL Mint: {self.sol_mint}")
        print(f"  USDC Mint: {self.usdc_mint}")
        print(f"  Quote Amount: {self.amount / 1e9} SOL")
    
    def get_sol_usdc_price(self):
        """
        Fetch SOL to USDC price from Jupiter API
        Returns the price of 1 SOL in USDC
        """
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_request_time < self.min_request_interval:
                time.sleep(self.min_request_interval - (current_time - self.last_request_time))
            
            # Prepare request parameters
            params = {
                'inputMint': self.sol_mint,
                'outputMint': self.usdc_mint,
                'amount': self.amount,
                'slippageBps': 50  # 0.5% slippage tolerance
            }
            
            # Make the request
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10,
                headers={'User-Agent': 'SOL-USDC-Trading-Simulator/1.0'}
            )
            
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract the output amount (USDC received for 1 SOL)
                if 'outAmount' in data:
                    # USDC has 6 decimals, so divide by 1e6
                    usdc_amount = int(data['outAmount']) / 1e6
                    sol_amount = self.amount / 1e9  # Convert lamports to SOL
                    
                    price = usdc_amount / sol_amount
                    
                    return price
                else:
                    print(f"❌ Unexpected API response format: {data}")
                    return None
            
            else:
                print(f"❌ API request failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout - Jupiter API is slow to respond")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - Check internet connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return None
        except json.JSONDecodeError:
            print("❌ Invalid JSON response from API")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching price: {e}")
            return None
    
    def test_connection(self):
        """Test the connection to Jupiter API"""
        print("Testing connection to Jupiter API...")
        price = self.get_sol_usdc_price()
        
        if price is not None:
            print(f"✅ Connection successful! Current SOL/USDC price: ${price:.4f}")
            return True
        else:
            print("❌ Connection test failed")
            return False
