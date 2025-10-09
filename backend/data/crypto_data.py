import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import aiohttp
from typing import List, Dict, Optional
import yfinance as yf
import requests
import time
import os
import pickle
import json

class CryptoDataProvider:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.session = None
        self.last_coingecko_call = 0
        self.coingecko_delay = 2  # 2 seconds between calls
        self.cache_dir = "data_cache"
        self.cache_file = os.path.join(self.cache_dir, "crypto_data.pkl")
        self.cache_metadata_file = os.path.join(self.cache_dir, "cache_metadata.json")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load cached data
        self.cached_data = self._load_cached_data()
    
    def _load_cached_data(self) -> Dict[str, pd.DataFrame]:
        """Load cached crypto data from disk"""
        try:
            print(f"Looking for cache file at: {self.cache_file}")
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                print(f"✅ Loaded cached data for {len(cached_data)} symbols: {list(cached_data.keys())}")
                return cached_data
            else:
                print(f"❌ Cache file not found at: {self.cache_file}")
        except Exception as e:
            print(f"Error loading cached data: {e}")
        return {}
    
    def _save_cached_data(self, data: Dict[str, pd.DataFrame]):
        """Save crypto data to disk cache"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # Save metadata
            metadata = {
                'last_updated': datetime.now().isoformat(),
                'symbols': list(data.keys()),
                'total_symbols': len(data)
            }
            with open(self.cache_metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Cached data for {len(data)} symbols")
        except Exception as e:
            print(f"Error saving cached data: {e}")
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid (less than 24 hours old)"""
        try:
            if not os.path.exists(self.cache_metadata_file):
                return False
            
            with open(self.cache_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            last_updated = datetime.fromisoformat(metadata['last_updated'])
            cache_age = datetime.now() - last_updated
            
            # Cache is valid for 24 hours
            return cache_age.total_seconds() < 24 * 3600
        except Exception as e:
            print(f"Error checking cache validity: {e}")
            return False
    
    async def get_historical_data(self, symbol: str, start_date: str, end_date: str, timeframe: str = '1h') -> pd.DataFrame:
        """Get historical OHLCV data for a symbol"""
        try:
            # Validate dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            today = datetime.now().date()
            
            # Check for future dates
            if start_dt.date() > today or end_dt.date() > today:
                raise ValueError("Cannot fetch historical data for future dates")
            
            # Check date range
            if start_dt >= end_dt:
                raise ValueError("Start date must be before end date")
            
            # Check cache first
            if symbol in self.cached_data:
                cached_df = self.cached_data[symbol]
                # Filter cached data to requested date range
                filtered_df = cached_df[(cached_df.index >= start_dt) & (cached_df.index <= end_dt)]
                if not filtered_df.empty:
                    print(f"Using cached data for {symbol} ({len(filtered_df)} days)")
                    return filtered_df
            
            # If not in cache or cache is invalid, fetch fresh data
            print(f"Fetching fresh data for {symbol}...")
            fresh_data = await self._fetch_fresh_data(symbol, start_date, end_date)
            
            # Update cache
            if not fresh_data.empty:
                self.cached_data[symbol] = fresh_data
                self._save_cached_data(self.cached_data)
            
            return fresh_data
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def _fetch_fresh_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch fresh data from APIs"""
        # Try CoinGecko first (more reliable) with rate limiting
        print(f"Trying CoinGecko for {symbol}...")
        coingecko_data = await self._get_coingecko_data(symbol, start_date, end_date)
        if not coingecko_data.empty:
            return coingecko_data
        
        # Try Binance as fallback
        print(f"Trying Binance for {symbol}...")
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_ts = int(start_dt.timestamp() * 1000)
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1d', start_ts, limit=1000)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        except Exception as e:
            print(f"Binance failed for {symbol}: {e}")
        
        # Try yfinance as final fallback
        print(f"Trying yfinance for {symbol}...")
        return await self._get_yfinance_data(symbol, start_date, end_date)
    
    async def populate_cache(self, symbols: List[str] = None, days_back: int = 365):
        """Pre-populate cache with data for all symbols"""
        if symbols is None:
            symbols = [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT',
                'XRP/USDT', 'DOT/USDT', 'DOGE/USDT', 'AVAX/USDT', 'MATIC/USDT'
            ]
        
        print(f"🔄 Populating cache with {len(symbols)} symbols ({days_back} days back)...")
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        successful_downloads = 0
        
        for i, symbol in enumerate(symbols, 1):
            print(f"📊 [{i}/{len(symbols)}] Downloading {symbol}...")
            
            try:
                # Check if already cached
                if symbol in self.cached_data:
                    print(f"  ✅ {symbol} already cached, skipping")
                    continue
                
                # Fetch data
                data = await self._fetch_fresh_data(symbol, start_date_str, end_date_str)
                
                if not data.empty:
                    self.cached_data[symbol] = data
                    successful_downloads += 1
                    print(f"  ✅ Downloaded {len(data)} days of data")
                else:
                    print(f"  ❌ No data available")
                
                # Rate limiting between downloads
                if i < len(symbols):
                    print(f"  ⏳ Waiting 3 seconds before next download...")
                    await asyncio.sleep(3)
                    
            except Exception as e:
                print(f"  ❌ Error downloading {symbol}: {e}")
        
        # Save all cached data
        if successful_downloads > 0:
            self._save_cached_data(self.cached_data)
            print(f"🎉 Cache populated successfully! Downloaded {successful_downloads}/{len(symbols)} symbols")
        else:
            print("❌ No data was downloaded")
    
    def get_cache_info(self) -> Dict[str, any]:
        """Get information about the current cache"""
        try:
            if os.path.exists(self.cache_metadata_file):
                with open(self.cache_metadata_file, 'r') as f:
                    metadata = json.load(f)
                return metadata
        except Exception as e:
            print(f"Error reading cache metadata: {e}")
        
        return {
            'cached_symbols': len(self.cached_data),
            'symbols': list(self.cached_data.keys()),
            'cache_valid': self._is_cache_valid()
        }
    
    async def _get_coingecko_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get data from CoinGecko API with rate limiting"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last_call = current_time - self.last_coingecko_call
            if time_since_last_call < self.coingecko_delay:
                sleep_time = self.coingecko_delay - time_since_last_call
                print(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
                await asyncio.sleep(sleep_time)
            
            self.last_coingecko_call = time.time()
            
            # Map symbols to CoinGecko IDs
            symbol_map = {
                'BTC/USDT': 'bitcoin',
                'ETH/USDT': 'ethereum',
                'BNB/USDT': 'binancecoin',
                'ADA/USDT': 'cardano',
                'SOL/USDT': 'solana',
                'XRP/USDT': 'ripple',
                'DOT/USDT': 'polkadot',
                'DOGE/USDT': 'dogecoin',
                'AVAX/USDT': 'avalanche-2',
                'MATIC/USDT': 'matic-network'
            }
            
            coin_id = symbol_map.get(symbol)
            if not coin_id:
                print(f"No CoinGecko mapping for {symbol}")
                return pd.DataFrame()
            
            # Convert dates to timestamps
            start_ts = int(pd.to_datetime(start_date).timestamp())
            end_ts = int(pd.to_datetime(end_date).timestamp())
            
            # CoinGecko API endpoint
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
            params = {
                'vs_currency': 'usd',
                'from': start_ts,
                'to': end_ts
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract price data
                        prices = data.get('prices', [])
                        volumes = data.get('total_volumes', [])
                        
                        if not prices:
                            print(f"No price data from CoinGecko for {symbol}")
                            return pd.DataFrame()
                        
                        # Create DataFrame
                        df_data = []
                        for i, price_point in enumerate(prices):
                            timestamp = pd.to_datetime(price_point[0], unit='ms')
                            price = price_point[1]
                            volume = volumes[i][1] if i < len(volumes) else 0
                            
                            df_data.append({
                                'timestamp': timestamp,
                                'open': price,
                                'high': price * 1.01,  # Approximate
                                'low': price * 0.99,   # Approximate
                                'close': price,
                                'volume': volume
                            })
                        
                        df = pd.DataFrame(df_data)
                        df.set_index('timestamp', inplace=True)
                        
                        print(f"Successfully fetched {len(df)} days from CoinGecko for {symbol}")
                        return df
                    elif response.status == 429:
                        print(f"CoinGecko rate limit exceeded for {symbol}, trying again later...")
                        return pd.DataFrame()
                    elif response.status == 401:
                        print(f"CoinGecko unauthorized for {symbol}, skipping...")
                        return pd.DataFrame()
                    else:
                        print(f"CoinGecko API error: {response.status}")
                        return pd.DataFrame()
                        
        except Exception as e:
            print(f"Error fetching CoinGecko data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def _get_yfinance_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fallback method using yfinance"""
        try:
            # Convert symbol format for yfinance - try multiple formats
            base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
            
            # Try different symbol formats
            symbol_formats = [
                f"{base_symbol}-USD",
                f"{base_symbol}",
                f"{base_symbol}USDT"
            ]
            
            for yf_symbol in symbol_formats:
                try:
                    ticker = yf.Ticker(yf_symbol)
                    df = ticker.history(start=start_date, end=end_date, interval='1d')
                    
                    if not df.empty:
                        print(f"Successfully fetched data for {symbol} using {yf_symbol}")
                        return df
                except Exception as e:
                    print(f"Failed to fetch {yf_symbol}: {e}")
                    continue
            
            print(f"No data found for {symbol} with any symbol format")
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error with yfinance fallback for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return 0.0
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple symbols"""
        prices = {}
        for symbol in symbols:
            prices[symbol] = await self.get_current_price(symbol)
        return prices
    
    async def stream_realtime_data(self, symbols: List[str], callback):
        """Stream real-time price data"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            while True:
                prices = await self.get_multiple_prices(symbols)
                await callback(prices)
                await asyncio.sleep(1)  # Update every second
        except Exception as e:
            print(f"Error in real-time streaming: {e}")
        finally:
            if self.session:
                await self.session.close()
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        try:
            markets = self.exchange.load_markets()
            # Filter for major crypto pairs
            crypto_symbols = []
            for symbol in markets:
                if 'USDT' in symbol and '/' in symbol:
                    crypto_symbols.append(symbol)
            return sorted(crypto_symbols)[:50]  # Return top 50
        except Exception as e:
            print(f"Error getting available symbols: {e}")
            return ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate common technical indicators"""
        try:
            # Create a copy to avoid SettingWithCopyWarning
            df = df.copy()
            
            # Simple Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            return df
            
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return df
