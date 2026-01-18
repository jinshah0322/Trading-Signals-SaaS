import asyncio
import json
import random
from datetime import datetime
from typing import List, Dict, Any
from app.redis_client import get_redis
from app.models.signal import Signal


# Cache configuration
CACHE_KEY = "signals:all"
CACHE_TTL = 300  # 5 minutes


# Mock instruments
INSTRUMENTS = [
    {"symbol": "NIFTY", "base_price": 21500},
    {"symbol": "BANKNIFTY", "base_price": 45200},
    {"symbol": "RELIANCE", "base_price": 2450},
    {"symbol": "TCS", "base_price": 3650},
    {"symbol": "INFY", "base_price": 1550},
    {"symbol": "HDFCBANK", "base_price": 1650},
    {"symbol": "ICICIBANK", "base_price": 950},
    {"symbol": "SBIN", "base_price": 580},
    {"symbol": "WIPRO", "base_price": 450},
    {"symbol": "TATAMOTORS", "base_price": 780},
    {"symbol": "LT", "base_price": 3200},
    {"symbol": "BAJFINANCE", "base_price": 6800},
    {"symbol": "MARUTI", "base_price": 11500},
    {"symbol": "KOTAKBANK", "base_price": 1750},
    {"symbol": "ITC", "base_price": 420},
    {"symbol": "BHARTIARTL", "base_price": 1250},
    {"symbol": "AXISBANK", "base_price": 1050},
    {"symbol": "SUNPHARMA", "base_price": 1480},
    {"symbol": "HINDUNILVR", "base_price": 2350},
    {"symbol": "ASIANPAINT", "base_price": 2900},
]

async def generate_mock_signals() -> List[Dict[str, Any]]:
    print("Generating trading signals")
    
    # Simulate network delay / expensive computation (2 seconds)
    await asyncio.sleep(2)
    
    signals = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for instrument in INSTRUMENTS:
        symbol = instrument["symbol"]
        base_price = instrument["base_price"]
        
        # Random price variation (±2%)
        price_variation = random.uniform(-0.02, 0.02)
        current_price = round(base_price * (1 + price_variation), 2)
        
        # Random action (60% BUY, 40% SELL for realism)
        action = random.choices(["BUY", "SELL"], weights=[0.6, 0.4])[0]
        
        # Calculate target and stoploss based on action
        if action == "BUY":
            target = round(current_price * 1.03, 2)  # 3% profit target
            stoploss = round(current_price * 0.98, 2)  # 2% stoploss
        else:  # SELL
            target = round(current_price * 0.97, 2)  # 3% profit target
            stoploss = round(current_price * 1.02, 2)  # 2% stoploss
        
        signal = {
            "symbol": symbol,
            "action": action,
            "price": current_price,
            "target": target,
            "stoploss": stoploss,
            "timestamp": timestamp
        }
        
        signals.append(signal)
    
    print(f"Generated {len(signals)} trading signals")
    return signals


async def get_cached_signals() -> List[Dict[str, Any]] | None:
    """Get signals from Redis cache"""
    redis = get_redis()
    
    cached_data = await redis.get(CACHE_KEY)
    
    if cached_data:
        print("Cache HIT - Returning signals from Redis")
        return json.loads(cached_data)
    
    print("Cache MISS - Need to generate signals")
    return None


async def cache_signals(signals: List[Dict[str, Any]]) -> None:
    """Store signals in Redis cache with TTL"""
    redis = get_redis()
    
    signals_json = json.dumps(signals)
    await redis.setex(CACHE_KEY, CACHE_TTL, signals_json)
    
    print(f"Signals cached in Redis (TTL: {CACHE_TTL} seconds)")


async def get_signals_for_user(is_paid: bool) -> Dict[str, Any]:
    """
    Get trading signals for user (with caching)
    
    Args:
        is_paid: Whether user has paid subscription
    
    Returns:
        Dictionary with signals and metadata
    """
    # Try to get from cache first
    signals = await get_cached_signals()
    cached = True
    
    # If cache miss, generate new signals
    if signals is None:
        signals = await generate_mock_signals()
        await cache_signals(signals)
        cached = False
    
    # Filter signals based on user type
    if is_paid:
        # Paid users see all signals
        filtered_signals = signals
        message = None
    else:
        # Free users see only first 3 signals
        filtered_signals = signals[:3]
        message = f"Subscribe for ₹499 to see all {len(signals)} signals"
    
    return {
        "signals": filtered_signals,
        "total": len(filtered_signals),
        "is_paid": is_paid,
        "cached": cached,
        "message": message
    }