"""
Resource Monitoring Script for Load Testing
Tracks CPU, Memory, Network, and Database metrics during tests
"""
import psutil
import time
import json
from datetime import datetime
from typing import Dict, List
import asyncio
import httpx


class ResourceMonitor:
    """Monitor system resources during load testing"""
    
    def __init__(self, interval: int = 5):
        self.interval = interval
        self.metrics: List[Dict] = []
        self.monitoring = False
        
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": mem.total / (1024**3),
            "available_gb": mem.available / (1024**3),
            "used_gb": mem.used / (1024**3),
            "percent": mem.percent
        }
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk I/O statistics"""
        disk_io = psutil.disk_io_counters()
        return {
            "read_mb": disk_io.read_bytes / (1024**2),
            "write_mb": disk_io.write_bytes / (1024**2),
            "read_count": disk_io.read_count,
            "write_count": disk_io.write_count
        }
    
    def get_network_usage(self) -> Dict[str, float]:
        """Get network I/O statistics"""
        net_io = psutil.net_io_counters()
        return {
            "sent_mb": net_io.bytes_sent / (1024**2),
            "recv_mb": net_io.bytes_recv / (1024**2),
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    
    async def get_backend_health(self, url: str = "http://localhost:8000/healthz") -> Dict:
        """Check backend health during monitoring"""
        try:
            async with httpx.AsyncClient() as client:
                start = time.time()
                response = await client.get(url, timeout=5)
                duration = (time.time() - start) * 1000  # ms
                
                return {
                    "status": response.status_code,
                    "response_time_ms": duration,
                    "healthy": response.status_code == 200
                }
        except Exception as e:
            return {
                "status": 0,
                "response_time_ms": 0,
                "healthy": False,
                "error": str(e)
            }
    
    def get_process_stats(self, process_name: str = "python") -> Dict:
        """Get stats for specific process (e.g., backend server)"""
        stats = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    stats.append({
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {
            "processes": stats,
            "total_cpu": sum(p["cpu_percent"] or 0 for p in stats),
            "total_memory": sum(p["memory_percent"] or 0 for p in stats)
        }
    
    async def collect_metrics(self):
        """Collect all metrics at once"""
        timestamp = datetime.now().isoformat()
        
        metrics = {
            "timestamp": timestamp,
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "network": self.get_network_usage(),
            "backend_health": await self.get_backend_health(),
            "python_processes": self.get_process_stats("python")
        }
        
        self.metrics.append(metrics)
        return metrics
    
    async def start_monitoring(self, duration_seconds: int = 300):
        """Start monitoring for specified duration"""
        print(f"🔍 Starting resource monitoring for {duration_seconds} seconds...")
        print(f"   Collecting metrics every {self.interval} seconds")
        
        self.monitoring = True
        start_time = time.time()
        
        while self.monitoring and (time.time() - start_time) < duration_seconds:
            metrics = await self.collect_metrics()
            
            # Print summary
            print(f"\n[{metrics['timestamp']}]")
            print(f"  CPU: {metrics['cpu']:.1f}%")
            print(f"  Memory: {metrics['memory']['percent']:.1f}% "
                  f"({metrics['memory']['used_gb']:.2f}GB used)")
            print(f"  Backend: {metrics['backend_health']['response_time_ms']:.2f}ms "
                  f"({'✅' if metrics['backend_health']['healthy'] else '❌'})")
            
            await asyncio.sleep(self.interval)
        
        print(f"\n✅ Monitoring complete. Collected {len(self.metrics)} data points.")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def save_results(self, filename: str = "load_test_metrics.json"):
        """Save metrics to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"📊 Metrics saved to {filename}")
    
    def generate_report(self) -> Dict:
        """Generate summary report from collected metrics"""
        if not self.metrics:
            return {"error": "No metrics collected"}
        
        cpu_values = [m["cpu"] for m in self.metrics]
        memory_values = [m["memory"]["percent"] for m in self.metrics]
        response_times = [
            m["backend_health"]["response_time_ms"] 
            for m in self.metrics 
            if m["backend_health"]["healthy"]
        ]
        
        report = {
            "duration_seconds": len(self.metrics) * self.interval,
            "data_points": len(self.metrics),
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "min": min(cpu_values),
                "max": max(cpu_values)
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values),
                "min": min(memory_values),
                "max": max(memory_values)
            },
            "backend_response_time_ms": {
                "avg": sum(response_times) / len(response_times) if response_times else 0,
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0
            },
            "backend_health_checks": {
                "total": len(self.metrics),
                "successful": sum(1 for m in self.metrics if m["backend_health"]["healthy"]),
                "failed": sum(1 for m in self.metrics if not m["backend_health"]["healthy"])
            }
        }
        
        return report
    
    def print_report(self):
        """Print formatted report"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("📊 RESOURCE MONITORING REPORT")
        print("="*60)
        
        print(f"\n⏱️  Duration: {report['duration_seconds']} seconds")
        print(f"📈 Data Points: {report['data_points']}")
        
        print(f"\n💻 CPU Usage:")
        print(f"   Average: {report['cpu']['avg']:.2f}%")
        print(f"   Min: {report['cpu']['min']:.2f}%")
        print(f"   Max: {report['cpu']['max']:.2f}%")
        
        print(f"\n🧠 Memory Usage:")
        print(f"   Average: {report['memory']['avg']:.2f}%")
        print(f"   Min: {report['memory']['min']:.2f}%")
        print(f"   Max: {report['memory']['max']:.2f}%")
        
        print(f"\n🚀 Backend Performance:")
        print(f"   Avg Response Time: {report['backend_response_time_ms']['avg']:.2f}ms")
        print(f"   Min Response Time: {report['backend_response_time_ms']['min']:.2f}ms")
        print(f"   Max Response Time: {report['backend_response_time_ms']['max']:.2f}ms")
        
        print(f"\n✅ Health Checks:")
        print(f"   Successful: {report['backend_health_checks']['successful']}")
        print(f"   Failed: {report['backend_health_checks']['failed']}")
        
        success_rate = (report['backend_health_checks']['successful'] / 
                       report['backend_health_checks']['total'] * 100)
        print(f"   Success Rate: {success_rate:.2f}%")
        
        print("\n" + "="*60)


async def main():
    """Run monitoring alongside load test"""
    monitor = ResourceMonitor(interval=5)
    
    try:
        # Monitor for 5 minutes (adjust based on load test duration)
        await monitor.start_monitoring(duration_seconds=300)
        
    except KeyboardInterrupt:
        print("\n⚠️  Monitoring interrupted by user")
        monitor.stop_monitoring()
    
    # Generate and print report
    monitor.print_report()
    monitor.save_results()


if __name__ == "__main__":
    asyncio.run(main())
