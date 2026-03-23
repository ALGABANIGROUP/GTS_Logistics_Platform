"""
🤖 Database Orchestrator Bot - Smart intermediary between frontend and database
Optimizes performance and reduces server load
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

import asyncpg
import redis.asyncio as redis
from aiohttp import web
import aiohttp
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== Data Structure ======================

class OperationType(Enum):
    READ = "read"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    BATCH = "batch"

@dataclass
class DataOperation:
    """Data operation structure"""
    operation_id: str
    operation_type: OperationType
    table: str
    data: Dict[str, Any]
    filters: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    priority: int = 1  # 1-10, 10 EN
    cache_ttl: int = 300  # 5 EN

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self):
        return asdict(self)

# ====================== Connection Settings ======================

DB_CONFIG = {
    "host": "dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com",
    "database": "gabani_transport_solutions",
    "user": "gabani_transport_solutions_user",
    "password": "8yCHEOG5yRgwzpihA3ocDu6Cc13v4lLv",
    "port": 5432,
    "ssl": "require"
}

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True
}

# ====================== Main Classes ======================

class ConnectionPool:
    """Database connection manager"""

    def __init__(self):
        self.pool = None
        self.redis_pool = None

    async def initialize(self):
        """Initialize connections"""
        # EN PostgreSQL
        self.pool = await asyncpg.create_pool(
            min_size=5,
            max_size=20,
            **DB_CONFIG
        )

        # EN Redis EN
        self.redis_pool = redis.Redis(**REDIS_CONFIG)

        logger.info("✅ EN")

    @asynccontextmanager
    async def get_connection(self):
        """EN"""
        if not self.pool:
            await self.initialize()

        async with self.pool.acquire() as connection:
            yield connection

    async def close(self):
        """Close connections"""
        if self.pool:
            await self.pool.close()
        if self.redis_pool:
            await self.redis_pool.aclose()  # EN aclose EN close

class QueryOptimizer:
    """Query optimizer"""

    def __init__(self):
        self.query_cache = {}
        self.stats = {"optimized": 0, "cache_hits": 0}

    def optimize_query(self, query: str, params: Dict) -> tuple:
        """Optimize query"""
        query_hash = self._generate_query_hash(query, params)

        # Check cache
        if query_hash in self.query_cache:
            self.stats["cache_hits"] += 1
            cached = self.query_cache[query_hash]
            return cached["optimized_query"], cached["optimized_params"]

        # Optimize query
        optimized = self._apply_optimizations(query, params)

        # Cache
        self.query_cache[query_hash] = {
            "optimized_query": optimized[0],
            "optimized_params": optimized[1],
            "timestamp": datetime.now()
        }

        self.stats["optimized"] += 1
        return optimized

    def _generate_query_hash(self, query: str, params: Dict) -> str:
        """Generate query hash"""
        combined = f"{query}{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _apply_optimizations(self, query: str, params: Dict) -> tuple:
        """Apply optimizations to query"""
        optimized_query = query

        # 1. Add LIMIT if not present
        if "LIMIT" not in query.upper() and "SELECT" in query.upper():
            if not query.strip().endswith(";"):
                optimized_query += " LIMIT 1000"
            else:
                optimized_query = optimized_query[:-1] + " LIMIT 1000;"

        # 2. Replace SELECT * with column names (simplified)
        if "SELECT *" in query.upper():
            # EN
            pass

        return optimized_query, params

class DataValidator:
    """Data validator"""

    VALIDATION_RULES = {
        "users": {
            "email": {"type": "email", "required": True},
            "name": {"type": "string", "min_length": 2, "max_length": 100},
            "phone": {"type": "phone", "required": False}
        },
        "orders": {
            "amount": {"type": "float", "min": 0},
            "status": {"type": "enum", "values": ["pending", "processing", "completed", "cancelled"]}
        }
    }

    async def validate(self, table: str, data: Dict) -> Dict:
        """Validate data"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        if table not in self.VALIDATION_RULES:
            validation_result["warnings"].append(f"No validation rules for table {table}")
            return validation_result

        rules = self.VALIDATION_RULES[table]

        for field, rule in rules.items():
            if rule.get("required", False) and field not in data:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Field {field} is required")

            if field in data:
                value = data[field]

                # Type validation
                if rule["type"] == "email" and value:
                    if not self._is_valid_email(value):
                        validation_result["is_valid"] = False
                        validation_result["errors"].append(f"Email {value} is invalid")

                elif rule["type"] == "string":
                    if "min_length" in rule and len(str(value)) < rule["min_length"]:
                        validation_result["errors"].append(f"Field {field} is too short")
                    if "max_length" in rule and len(str(value)) > rule["max_length"]:
                        validation_result["errors"].append(f"Field {field} is too long")

        return validation_result

    def _is_valid_email(self, email: str) -> bool:
        """Validate email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

class CacheManager:
    """Cache manager"""

    def __init__(self, redis_pool):
        self.redis = redis_pool
        self.hit_rate = 0
        self.total_requests = 0
        self.hits = 0

    async def get(self, key: str) -> Optional[str]:
        """Get data from cache"""
        self.total_requests += 1
        value = await self.redis.get(key)

        if value:
            self.hits += 1
            self.hit_rate = self.hits / self.total_requests
            logger.debug(f"✅ Cache HIT: {key}")
            return json.loads(value)

        logger.debug(f"❌ Cache MISS: {key}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Store data in cache"""
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
        logger.debug(f"💾 Cache SET: {key} for {ttl} seconds")

    async def invalidate(self, pattern: str):
        """Remove data from cache"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
            logger.info(f"🗑️  Removed {len(keys)} keys from cache: {pattern}")

    async def clear_table_cache(self, table: str):
        """Clear cache for specific table"""
        await self.invalidate(f"table:{table}:*")

class BatchProcessor:
    """Batch processor"""

    def __init__(self, batch_size: int = 100, flush_interval: int = 300):
        self.batch_size = batch_size
        self.flush_interval = flush_interval  # 5 minutes
        self.batches: Dict[str, List[DataOperation]] = {}
        self.last_flush = datetime.now()

    async def add_operation(self, operation: DataOperation):
        """Add operation to batch"""
        table = operation.table

        if table not in self.batches:
            self.batches[table] = []

        self.batches[table].append(operation)

        # Check if batch reached required size
        if len(self.batches[table]) >= self.batch_size:
            await self.flush_table(table)

        # Check if time interval has passed
        if (datetime.now() - self.last_flush).seconds >= self.flush_interval:
            await self.flush_all()

    async def flush_table(self, table: str):
        """Execute batch for specific table"""
        if table not in self.batches or not self.batches[table]:
            return

        operations = self.batches[table]
        logger.info(f"🔄 Executing batch for table {table} ({len(operations)} operations)")

        # Group operations by type
        write_ops = [op for op in operations if op.operation_type == OperationType.WRITE]
        update_ops = [op for op in operations if op.operation_type == OperationType.UPDATE]

        # EN
        if write_ops:
            await self._batch_insert(table, write_ops)

        # EN
        for op in update_ops:
            await self._execute_update(op)

        # EN
        self.batches[table] = []

    async def flush_all(self):
        """EN"""
        for table in list(self.batches.keys()):
            await self.flush_table(table)
        self.last_flush = datetime.now()

    async def _batch_insert(self, table: str, operations: List[DataOperation]):
        """EN"""
        if not operations:
            return

        # EN INSERT EN
        columns = set()
        for op in operations:
            columns.update(op.data.keys())

        columns = list(columns)
        values_placeholders = []
        all_values = []

        for i, op in enumerate(operations):
            placeholders = []
            for col in columns:
                value = op.data.get(col)
                if value is None:
                    placeholders.append("NULL")
                else:
                    all_values.append(value)
                    placeholders.append(f"${len(all_values)}")

            values_placeholders.append(f"({', '.join(placeholders)})")

        query = f"""
        INSERT INTO {table} ({', '.join(columns)})
        VALUES {', '.join(values_placeholders)}
        ON CONFLICT DO NOTHING
        """

        try:
            async with connection_pool.get_connection() as conn:
                await conn.execute(query, *all_values)
                logger.info(f"✅ Inserted {len(operations)} rows into table {table}")
        except Exception as e:
            logger.error(f"❌ Batch insert error: {e}")

    async def _execute_update(self, operation: DataOperation):
        """Execute update operation"""
        # EN
        pass

class DatabaseOrchestratorBot:
    """Main database orchestration bot"""

    def __init__(self):
        self.connection_pool = ConnectionPool()
        self.query_optimizer = QueryOptimizer()
        self.data_validator = DataValidator()
        self.cache_manager = None
        self.batch_processor = BatchProcessor()

        # Statistics
        self.metrics = {
            "requests_served": 0,
            "cache_hits": 0,
            "batch_operations": 0,
            "avg_response_time": 0,
            "errors": 0
        }

        # Scheduled operations table
        self.scheduled_operations = {}

    async def initialize(self):
        """Initialize bot"""
        await self.connection_pool.initialize()
        self.cache_manager = CacheManager(self.connection_pool.redis_pool)

        # Start background tasks
        asyncio.create_task(self._periodic_flush())
        asyncio.create_task(self._health_check())
        asyncio.create_task(self._cleanup_old_data())

        logger.info("🚀 Database Orchestrator Bot started")

    async def process_request(self, operation: DataOperation) -> Dict:
        """Process data request"""
        start_time = time.time()
        self.metrics["requests_served"] += 1

        try:
            # 1. EN
            validation = await self.data_validator.validate(operation.table, operation.data)
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "errors": validation["errors"],
                    "warnings": validation["warnings"]
                }

            # 2. EN
            if operation.operation_type == OperationType.READ:
                result = await self._handle_read(operation)
            elif operation.operation_type == OperationType.WRITE:
                result = await self._handle_write(operation)
            elif operation.operation_type == OperationType.UPDATE:
                result = await self._handle_update(operation)
            elif operation.operation_type == OperationType.DELETE:
                result = await self._handle_delete(operation)
            elif operation.operation_type == OperationType.BATCH:
                result = await self._handle_batch(operation)
            else:
                result = {"success": False, "error": "EN"}

            # 3. EN
            response_time = time.time() - start_time
            self.metrics["avg_response_time"] = (
                (self.metrics["avg_response_time"] * (self.metrics["requests_served"] - 1) + response_time)
                / self.metrics["requests_served"]
            )

            result["metrics"] = {
                "response_time": response_time,
                "cache_used": result.get("from_cache", False)
            }

            return result

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"❌ EN: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_read(self, operation: DataOperation) -> Dict:
        """EN"""
        # 1. EN
        cache_key = f"table:{operation.table}:{hashlib.md5(json.dumps(operation.filters or {}).encode()).hexdigest()}"
        cached_data = await self.cache_manager.get(cache_key)

        if cached_data:
            self.metrics["cache_hits"] += 1
            return {
                "success": True,
                "data": cached_data,
                "from_cache": True,
                "cache_key": cache_key
            }

        # 2. Build query
        base_query = f"SELECT * FROM {operation.table}"
        params = {}

        if operation.filters:
            where_clauses = []
            for i, (key, value) in enumerate(operation.filters.items(), 1):
                where_clauses.append(f"{key} = ${i}")
                params[i] = value

            if where_clauses:
                base_query += f" WHERE {' AND '.join(where_clauses)}"

        # 3. Optimize query
        optimized_query, optimized_params = self.query_optimizer.optimize_query(base_query, params)

        # 4. Execute query
        try:
            async with self.connection_pool.get_connection() as conn:
                rows = await conn.fetch(optimized_query, *list(optimized_params.values()))

                data = [dict(row) for row in rows]

                # 5. Cache
                await self.cache_manager.set(
                    cache_key,
                    data,
                    ttl=operation.cache_ttl
                )

                return {
                    "success": True,
                    "data": data,
                    "from_cache": False,
                    "rows_count": len(data),
                    "cache_key": cache_key
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_write(self, operation: DataOperation) -> Dict:
        """EN"""
        # 1. EN
        if operation.priority < 5:  # EN
            await self.batch_processor.add_operation(operation)
            self.metrics["batch_operations"] += 1

            return {
                "success": True,
                "message": "EN",
                "batch_processing": True,
                "operation_id": operation.operation_id
            }
        else:
            # 2. EN
            columns = list(operation.data.keys())
            values = list(operation.data.values())

            placeholders = ', '.join([f"${i+1}" for i in range(len(values))])

            query = f"""
            INSERT INTO {operation.table} ({', '.join(columns)})
            VALUES ({placeholders})
            RETURNING id
            """

            try:
                async with self.connection_pool.get_connection() as conn:
                    result = await conn.fetchrow(query, *values)

                    # 3. EN
                    await self.cache_manager.clear_table_cache(operation.table)

                    return {
                        "success": True,
                        "inserted_id": result["id"] if result else None,
                        "rows_affected": 1,
                        "operation_id": operation.operation_id
                    }

            except Exception as e:
                return {"success": False, "error": str(e)}

    async def _handle_update(self, operation: DataOperation) -> Dict:
        """EN"""
        # EN WHERE clause
        pass

    async def _handle_delete(self, operation: DataOperation) -> Dict:
        """EN"""
        # EN
        pass

    async def _handle_batch(self, operation: DataOperation) -> Dict:
        """Handle batch operation"""
        # EN
        pass

    async def _periodic_flush(self):
        """Flush batches periodically"""
        while True:
            await asyncio.sleep(300)  # every 5 minutes
            try:
                await self.batch_processor.flush_all()
                logger.info("🔄 Periodic flush of all batches completed")
            except Exception as e:
                logger.error(f"❌ Error in batch flush: {e}")

    async def _health_check(self):
        """System health check"""
        while True:
            await asyncio.sleep(60)  # every minute

            try:
                # Check database connection
                async with self.connection_pool.get_connection() as conn:
                    await conn.fetch("SELECT 1")

                # Check Redis connection
                await self.connection_pool.redis_pool.ping()

                # Log statistics
                self._log_metrics()

                logger.info("✅ Health check: All systems operating normally")

            except Exception as e:
                logger.error(f"❌ Health check failed: {e}")

    async def _cleanup_old_data(self):
        """Clean up old data"""
        while True:
            await asyncio.sleep(3600)  # every hour

            try:
                # Clean up old operation logs
                cutoff_time = datetime.now() - timedelta(days=7)

                async with self.connection_pool.get_connection() as conn:
                    await conn.execute("""
                        DELETE FROM operation_logs
                        WHERE timestamp < $1
                    """, cutoff_time)

                logger.info("🧹 EN")

            except Exception as e:
                logger.error(f"❌ EN: {e}")

    def _log_metrics(self):
        """EN"""
        logger.info(f"""
📊 EN:
• EN: {self.metrics['requests_served']}
• EN: {self.metrics['cache_hits']}
• EN: {self.metrics['batch_operations']}
• EN: {self.metrics['avg_response_time']:.3f} EN
• EN: {self.metrics['errors']}
        """)

# ====================== EN REST API ======================

app = web.Application()
bot = DatabaseOrchestratorBot()

async def startup(app):
    """EN"""
    await bot.initialize()

async def shutdown(app):
    """EN"""
    await bot.connection_pool.close()

app.on_startup.append(startup)
app.on_shutdown.append(shutdown)

async def handle_request(request):
    """EN API"""
    try:
        data = await request.json()

        operation = DataOperation(
            operation_id=data.get("id", hashlib.md5(str(time.time()).encode()).hexdigest()),
            operation_type=OperationType(data["operation_type"]),
            table=data["table"],
            data=data.get("data", {}),
            filters=data.get("filters"),
            priority=data.get("priority", 1),
            cache_ttl=data.get("cache_ttl", 300)
        )

        result = await bot.process_request(operation)

        return web.json_response(result)

    except Exception as e:
        return web.json_response(
            {"success": False, "error": str(e)},
            status=400
        )

async def get_metrics(request):
    """Get system metrics"""
    return web.json_response(bot.metrics)

async def flush_batches(request):
    """Flush batches manually"""
    await bot.batch_processor.flush_all()
    return web.json_response({"success": True, "message": "All batches flushed"})

async def clear_cache(request):
    """Clear cache"""
    table = request.query.get("table")
    if table:
        await bot.cache_manager.clear_table_cache(table)
        message = f"Cache cleared for table {table}"
    else:
        # Clear all
        await bot.cache_manager.invalidate("*")
        message = "All cache cleared"

    return web.json_response({"success": True, "message": message})

# Register routes
app.router.add_post('/api/v1/operation', handle_request)
app.router.add_get('/api/v1/metrics', get_metrics)
app.router.add_post('/api/v1/flush', flush_batches)
app.router.add_post('/api/v1/clear-cache', clear_cache)

# Create global pool object
connection_pool = ConnectionPool()

if __name__ == "__main__":
    # Run web server
    web.run_app(
        app,
        host="0.0.0.0",
        port=8081,  # Change port to 8081
        access_log=logger
    )