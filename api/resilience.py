"""
Advanced resilience patterns for production-grade reliability
- Retry logic with exponential backoff
- Circuit breaker pattern
- Request caching
- Cost monitoring
- Rate limiting
"""

import asyncio
import logging
import time
from typing import Callable, Any, Optional, Dict
from functools import wraps
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

# ============================================================================
# CIRCUIT BREAKER PATTERN
# ============================================================================

class CircuitState(Enum):
    """States for circuit breaker"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: int = 60  # Seconds before attempting recovery
    half_open_max_calls: int = 3  # Max calls in half-open state


class CircuitBreaker:
    """Circuit breaker for API resilience"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.config.half_open_max_calls:
                raise Exception(f"Circuit breaker '{self.name}' max half-open calls exceeded")
            self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if recovery timeout has passed"""
        if not self.last_failure_time:
            return False
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info(f"Circuit breaker '{self.name}' is CLOSED (recovered)")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count += 1
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker '{self.name}' is OPEN after {self.failure_count} failures")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker '{self.name}' REOPENED during recovery")


# ============================================================================
# RETRY LOGIC WITH EXPONENTIAL BACKOFF
# ============================================================================

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd


class RetryableError(Exception):
    """Indicates error is retryable"""
    pass


def async_retry(config: RetryConfig = None):
    """Decorator for retryable async functions"""
    config = config or RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            delay = config.initial_delay
            
            while attempt < config.max_attempts:
                try:
                    return await func(*args, **kwargs)
                except (RetryableError, asyncio.TimeoutError, ConnectionError) as e:
                    attempt += 1
                    if attempt >= config.max_attempts:
                        logger.error(f"Max retries ({config.max_attempts}) exceeded for {func.__name__}")
                        raise
                    
                    # Calculate backoff with jitter
                    if config.jitter:
                        import random
                        delay = delay * config.exponential_base * (0.5 + random.random())
                    else:
                        delay = delay * config.exponential_base
                    
                    delay = min(delay, config.max_delay)
                    logger.warning(f"Retry {attempt}/{config.max_attempts} for {func.__name__} after {delay:.1f}s")
                    
                    await asyncio.sleep(delay)
                except Exception as e:
                    logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
                    raise
            
        return wrapper
    return decorator


# ============================================================================
# REQUEST CACHING
# ============================================================================

@dataclass
class CacheEntry:
    """Single cache entry"""
    value: Any
    created_at: datetime
    ttl_seconds: int
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds


class RequestCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self.hits = 0
        self.misses = 0
        
    def _generate_key(self, namespace: str, data: Any) -> str:
        """Generate cache key from data"""
        key_str = f"{namespace}:{json.dumps(data, sort_keys=True, default=str)}"
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    async def get(self, namespace: str, data: Any) -> Optional[Any]:
        """Get from cache"""
        async with self._lock:
            key = self._generate_key(namespace, data)
            
            if key not in self._cache:
                self.misses += 1
                return None
            
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                self.misses += 1
                return None
            
            self.hits += 1
            return entry.value
    
    async def set(self, namespace: str, data: Any, value: Any, ttl_seconds: int = 3600):
        """Set cache entry"""
        async with self._lock:
            key = self._generate_key(namespace, data)
            self._cache[key] = CacheEntry(
                value=value,
                created_at=datetime.now(),
                ttl_seconds=ttl_seconds
            )
            logger.debug(f"Cached {namespace}: {key[:8]}... (TTL: {ttl_seconds}s)")
    
    async def clear_expired(self):
        """Remove expired entries"""
        async with self._lock:
            expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                logger.debug(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate": round(hit_rate, 2),
            "cached_items": len(self._cache)
        }


# ============================================================================
# COST MONITORING
# ============================================================================

@dataclass
class APICallMetrics:
    """Metrics for API calls"""
    provider: str
    model: str
    timestamp: datetime = field(default_factory=datetime.now)
    cost: float = 0.0
    tokens_used: int = 0
    latency_ms: float = 0.0


class CostMonitor:
    """Monitor and track API costs"""
    
    # Typical costs per provider (these would come from actual pricing)
    COST_PER_1K_TOKENS = {
        "openrouter": 0.001,  # Approximate
        "openai": 0.002,
        "anthropic": 0.003,
        "google": 0.0005,
    }
    
    def __init__(self, monthly_budget: float = 100.0, alert_threshold: float = 0.8):
        self.monthly_budget = monthly_budget
        self.alert_threshold = alert_threshold
        self.metrics: list[APICallMetrics] = []
        self.total_spent = 0.0
        self._lock = asyncio.Lock()
    
    async def record_call(self, provider: str, model: str, tokens: int, latency_ms: float):
        """Record an API call"""
        async with self._lock:
            cost = (tokens / 1000) * self.COST_PER_1K_TOKENS.get(provider, 0.001)
            self.total_spent += cost
            
            metric = APICallMetrics(
                provider=provider,
                model=model,
                tokens_used=tokens,
                latency_ms=latency_ms,
                cost=cost
            )
            self.metrics.append(metric)
            
            # Check budget alert
            spent_percentage = (self.total_spent / self.monthly_budget) * 100
            if spent_percentage > (self.alert_threshold * 100):
                logger.warning(
                    f"⚠️  Budget alert: {spent_percentage:.1f}% of monthly budget used "
                    f"(${self.total_spent:.2f}/${self.monthly_budget:.2f})"
                )
            
            logger.debug(f"Recorded API call: {provider}/{model} - ${cost:.4f}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cost statistics"""
        if not self.metrics:
            return {"status": "no_metrics"}
        
        total_calls = len(self.metrics)
        avg_latency = sum(m.latency_ms for m in self.metrics) / total_calls
        total_tokens = sum(m.tokens_used for m in self.metrics)
        
        return {
            "total_spent": round(self.total_spent, 2),
            "monthly_budget": self.monthly_budget,
            "budget_used_percent": round((self.total_spent / self.monthly_budget) * 100, 2),
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "avg_latency_ms": round(avg_latency, 2),
            "remaining_budget": round(self.monthly_budget - self.total_spent, 2),
        }
    
    def should_throttle(self) -> bool:
        """Determine if we should throttle requests due to budget"""
        spent_percentage = (self.total_spent / self.monthly_budget)
        return spent_percentage > 0.95  # Stop at 95% of budget


# ============================================================================
# RATE LIMITER
# ============================================================================

@dataclass
class RateLimitWindow:
    """Rate limit window tracking"""
    max_requests: int
    window_seconds: int
    requests: list[datetime] = field(default_factory=list)
    
    def add_request(self):
        """Add a request"""
        self.requests.append(datetime.now())
        # Clean old requests outside window
        cutoff = datetime.now() - timedelta(seconds=self.window_seconds)
        self.requests = [r for r in self.requests if r > cutoff]
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        cutoff = datetime.now() - timedelta(seconds=self.window_seconds)
        valid_requests = [r for r in self.requests if r > cutoff]
        return len(valid_requests) < self.max_requests


class RateLimiter:
    """Per-user/IP rate limiting"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.minute_limit = requests_per_minute
        self.hour_limit = requests_per_hour
        self.windows: Dict[str, Dict[str, RateLimitWindow]] = {}
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, client_id: str) -> tuple[bool, Dict[str, int]]:
        """Check if client is allowed to make request"""
        async with self._lock:
            if client_id not in self.windows:
                self.windows[client_id] = {
                    "minute": RateLimitWindow(self.minute_limit, 60),
                    "hour": RateLimitWindow(self.hour_limit, 3600),
                }
            
            windows = self.windows[client_id]
            minute_allowed = windows["minute"].is_allowed()
            hour_allowed = windows["hour"].is_allowed()
            
            if minute_allowed and hour_allowed:
                windows["minute"].add_request()
                windows["hour"].add_request()
                
            remaining_minute = self.minute_limit - len(windows["minute"].requests)
            remaining_hour = self.hour_limit - len(windows["hour"].requests)
            
            return (minute_allowed and hour_allowed), {
                "remaining_per_minute": max(0, remaining_minute),
                "remaining_per_hour": max(0, remaining_hour),
            }


# ============================================================================
# TIMEOUT MANAGEMENT
# ============================================================================

class TimeoutManager:
    """Manage request timeouts with smart escalation"""
    
    def __init__(self):
        self.base_timeout = 15  # seconds
        self.max_timeout = 60
        self.failure_history: Dict[str, list[datetime]] = {}
    
    async def execute_with_timeout(self, func: Callable, client_id: str, *args, **kwargs) -> Any:
        """Execute function with intelligent timeout"""
        timeout = self._calculate_timeout(client_id)
        
        try:
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            self._record_timeout(client_id)
            raise
    
    def _calculate_timeout(self, client_id: str) -> float:
        """Calculate timeout based on client history"""
        if client_id not in self.failure_history:
            return self.base_timeout
        
        # Increase timeout if client has history of timeouts
        failure_count = len([f for f in self.failure_history[client_id] 
                           if (datetime.now() - f).total_seconds() < 3600])
        return min(self.base_timeout + (failure_count * 5), self.max_timeout)
    
    def _record_timeout(self, client_id: str):
        """Record a timeout for this client"""
        if client_id not in self.failure_history:
            self.failure_history[client_id] = []
        self.failure_history[client_id].append(datetime.now())


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Initialize global resilience components
circuit_breaker_llm = CircuitBreaker("llm_api")
request_cache = RequestCache()
cost_monitor = CostMonitor(monthly_budget=100.0)
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
timeout_manager = TimeoutManager()
