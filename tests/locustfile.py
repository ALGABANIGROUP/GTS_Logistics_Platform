"""
Load Testing Configuration for GTS Logistics
Tests backend API under various load conditions
"""
from locust import HttpUser, task, between, events
import json
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GTSUser(HttpUser):
    """Simulates a GTS Logistics user"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    host = "http://localhost:8000"
    
    def on_start(self):
        """Login before starting tasks"""
        self.login()
    
    def login(self):
        """Authenticate and get token"""
        response = self.client.post(
            "/api/v1/auth/token",
            data="username=tester%40gts.com&password=123456",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="Login",
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            logger.info("User authenticated successfully")
            response.success()
        else:
            logger.error(f"Login failed: {response.status_code} - {response.text}")
            response.failure(f"Login failed with {response.status_code}")
            self.token = None
            self.headers = {}
    
    @task(5)
    def get_health_check(self):
        """Health check endpoint (most frequent)"""
        self.client.get("/healthz", name="Health Check")
    
    @task(3)
    def get_user_info(self):
        """Get current user information"""
        if self.token:
            self.client.get("/api/v1/auth/me", headers=self.headers, name="Get User Info")
    
    @task(4)
    def list_bots(self):
        """List all available bots"""
        if self.token:
            self.client.get("/api/v1/bots", headers=self.headers, name="List Bots")
    
    @task(2)
    def get_bot_stats(self):
        """Get bot statistics"""
        if self.token:
            self.client.get("/api/v1/bots/stats", headers=self.headers, name="Bot Stats")
    
    @task(1)
    def get_bot_history(self):
        """Get bot execution history"""
        if self.token:
            self.client.get(
                "/api/v1/bots/history",
                params={"limit": 10},
                headers=self.headers,
                name="Bot History"
            )
    
    @task(1)
    def execute_bot_command(self):
        """Execute a bot command (rate-limited)"""
        if self.token:
            commands = [
                "Show me today's loads",
                "Check bot status",
                "What's my role?",
                "List active users"
            ]
            
            response = self.client.post(
                "/api/v1/commands/human",
                json={"command": random.choice(commands)},
                headers=self.headers,
                name="Execute Bot Command"
            )
            
            if response.status_code == 429:
                logger.warning("Rate limit hit for bot commands")


class AdminUser(GTSUser):
    """Simulates an admin user with more privileges"""
    
    weight = 1  # 1 admin for every 10 regular users
    
    def login(self):
        """Login as admin"""
        response = self.client.post(
            "/api/v1/auth/token",
            data="username=admin%40gts.com&password=admin123",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="Admin Login",
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            logger.info("Admin authenticated successfully")
            response.success()
        else:
            logger.warning(f"Admin login failed: {response.status_code}, falling back to regular user")
            response.failure(f"Admin login failed with {response.status_code}")
            super().login()
    
    @task(2)
    def manage_bots(self):
        """Admin bot management tasks"""
        if self.token:
            # Get bot list first
            response = self.client.get("/api/v1/bots", headers=self.headers)
            
            if response.status_code == 200:
                bots = response.json()
                if bots:
                    # Randomly pause/resume a bot
                    bot_name = random.choice([b.get("name") for b in bots if b.get("name")])
                    if bot_name:
                        self.client.post(
                            f"/api/v1/bots/{bot_name}/pause",
                            headers=self.headers,
                            name="Pause/Resume Bot"
                        )


class OperatorUser(GTSUser):
    """Simulates an operator user"""
    
    weight = 3  # 3 operators for every 10 users
    
    def login(self):
        """Login as operator"""
        operator_num = random.randint(1, 5)
        response = self.client.post(
            "/api/v1/auth/token",
            data=f"username=operator{operator_num}%40gts.com&password=operator123",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="Operator Login",
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            logger.info(f"Operator{operator_num} authenticated successfully")
            response.success()
        else:
            logger.warning(f"Operator login failed: {response.status_code}, falling back to regular user")
            response.failure(f"Operator login failed with {response.status_code}")
            super().login()
    
    @task(3)
    def check_loads(self):
        """Check available loads"""
        if self.token:
            self.client.get(
                "/api/v1/loads",
                params={"status": "available"},
                headers=self.headers,
                name="Check Loads"
            )


# Event listeners for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log slow requests"""
    if response_time > 1000:  # Over 1 second
        logger.warning(f"Slow request: {name} took {response_time}ms")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Final report when test ends"""
    stats = environment.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Total failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time}ms")
    logger.info(f"Requests per second: {stats.total.current_rps}")


# Usage:
# locust -f tests/locustfile.py --host=http://localhost:8000
# 
# Load test scenarios:
# 1. Light load: 10 users, spawn rate 1/s
# 2. Normal load: 100 users, spawn rate 10/s
# 3. Heavy load: 500 users, spawn rate 50/s
# 4. Stress test: 1000 users, spawn rate 100/s
