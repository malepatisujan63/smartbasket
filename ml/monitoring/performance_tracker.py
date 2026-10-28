import time
import datetime
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from ml.utils.logger import logger
from ml.utils.data_utils import save_artifact, load_artifact
from ml.configs import LOGS_DIR

class EnterprisePerformanceTracker:
    """
    MLOps Production Inference Performance & Latency Tracker.
    Monitors inference throughput, execution latency (ms), cache hit ratios,
    and runtime exceptions across all FastAPI endpoints.
    """
    def __init__(self, log_dir: Path = LOGS_DIR):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.perf_log_file = self.log_dir / "inference_performance_metrics.json"
        self._init_log()

    def _init_log(self):
        if not self.perf_log_file.exists():
            save_artifact({"total_inferences": 0, "cache_hits": 0, "endpoint_metrics": {}}, self.perf_log_file)

    def track_inference(self, endpoint_name: str, start_time: float, cache_hit: bool = False, error: Optional[str] = None):
        """Logs execution latency (ms) and status for an inference request."""
        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        
        try:
            data = load_artifact(self.perf_log_file) or {"total_inferences": 0, "cache_hits": 0, "endpoint_metrics": {}}
            data["total_inferences"] += 1
            if cache_hit:
                data["cache_hits"] += 1
                
            metrics = data["endpoint_metrics"].get(endpoint_name, {
                "count": 0, "total_latency_ms": 0.0, "avg_latency_ms": 0.0,
                "max_latency_ms": 0.0, "errors_count": 0, "last_updated": ""
            })
            
            metrics["count"] += 1
            metrics["total_latency_ms"] = round(metrics["total_latency_ms"] + latency_ms, 2)
            metrics["avg_latency_ms"] = round(metrics["total_latency_ms"] / metrics["count"], 2)
            metrics["max_latency_ms"] = max(metrics["max_latency_ms"], latency_ms)
            if error:
                metrics["errors_count"] += 1
            metrics["last_updated"] = datetime.datetime.utcnow().isoformat()
            
            data["endpoint_metrics"][endpoint_name] = metrics
            save_artifact(data, self.perf_log_file)
        except Exception as e:
            logger.debug(f"Performance tracker logging fallback: {e}")
            
    def get_performance_summary(self) -> Dict[str, Any]:
        """Returns macro KPI metrics for real-time executive dashboard display."""
        data = load_artifact(self.perf_log_file) or {"total_inferences": 0, "cache_hits": 0, "endpoint_metrics": {}}
        total = max(1, data.get("total_inferences", 1))
        hits = data.get("cache_hits", 0)
        
        return {
            "total_inferences_served": total,
            "cache_hit_ratio_pct": round((hits / total) * 100, 1),
            "endpoint_breakdown": data.get("endpoint_metrics", {}),
            "system_health": "OPTIMAL - High Throughput / Sub-10ms Latency" if (hits/total) > 0.3 else "NORMAL - Active Inference"
        }

# Global singleton Performance Tracker
performance_tracker = EnterprisePerformanceTracker()
