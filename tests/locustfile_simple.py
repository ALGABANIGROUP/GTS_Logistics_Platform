"""
Simplified Load Testing for GTS Logistics
"""
from locust import HttpUser, task, between, events
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GTSUser(HttpUser):
    """Basic GTS user for load testing"""
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login when user starts"""
        # Simple health check - no auth needed
        pass
    
    @task(10)
    def health_check(self):
        """Most common task: health check"""
        self.client.get("/healthz", name="Health Check")
    
    @task(2)
    def list_bots(self):
        """List bots (requires auth)"""
        self.client.get(
            "/api/v1/bots",
            headers={"Authorization": "Bearer dummy-token"},
            name="List Bots"
        )
    
    @task(1)
    def get_stats(self):
        """Get stats"""
        self.client.get(
            "/api/v1/bots/stats",
            headers={"Authorization": "Bearer dummy-token"},
            name="Bot Stats"
        )


class AuthUser(HttpUser):
    """User that attempts authentication"""
    weight = 1
    wait_time = between(5, 10)
    
    @task
    def attempt_login(self):
        """Attempt to login"""
        response = self.client.post(
            "/api/v1/auth/token",
            data="username=tester%40gts.com&password=123456",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="User Login"
        )


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Print summary when test ends"""
    logger.info(f"Test completed")
    logger.info(f"Total requests: {environment.stats.total.num_requests}")
    logger.info(f"Total failures: {environment.stats.total.num_failures}")
    if environment.stats.total.num_requests > 0:
        logger.info(f"Average response time: {environment.stats.total.avg_response_time}ms")
        logger.info(f"Requests per second: {environment.stats.total.current_rps}")
