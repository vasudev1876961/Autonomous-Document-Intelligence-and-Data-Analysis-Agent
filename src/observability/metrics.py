"""
Enterprise Observability, Prometheus Metrics, and Trace Telemetry.
Provides thread-safe Prometheus metric collectors (Counters, Gauges, Histograms)
and standard exposition formatting for production monitoring and alerting.
"""
from __future__ import annotations
import threading
import time
from typing import Any, Dict, List, Tuple


class ObservabilityRegistry:
    """
    Thread-safe production metrics registry emitting Prometheus exposition format
    and structured operational telemetry.
    """
    _instance: ObservabilityRegistry | None = None
    _lock = threading.Lock()

    def __new__(cls) -> ObservabilityRegistry:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_metrics()
            return cls._instance

    def _init_metrics(self) -> None:
        self.lock = threading.Lock()
        # Request counts: (endpoint, method, status) -> int
        self.http_requests: Dict[Tuple[str, str, int], int] = {}
        # Request latencies: endpoint -> list[float]
        self.http_durations: Dict[str, List[float]] = {}
        # Agent execution steps: (node, status) -> int
        self.agent_steps: Dict[Tuple[str, str], int] = {}
        # Token usage: (model, token_type) -> int
        self.token_usage: Dict[Tuple[str, str], int] = {}
        # Retrieval queries: retriever_type -> int
        self.retrieval_queries: Dict[str, int] = {
            "bm25": 0,
            "dense": 0,
            "hybrid": 0
        }
        # Calculation errors: module -> int
        self.calc_errors: Dict[str, int] = {}
        # Active requests gauge
        self.active_requests: int = 0
        # Start timestamp
        self.start_time = time.time()

    def record_request(self, method: str, endpoint: str, status_code: int, duration_sec: float) -> None:
        """Records an HTTP transaction with method, endpoint, status, and latency."""
        with self.lock:
            key = (endpoint, method.upper(), status_code)
            self.http_requests[key] = self.http_requests.get(key, 0) + 1
            if endpoint not in self.http_durations:
                self.http_durations[endpoint] = []
            self.http_durations[endpoint].append(duration_sec)
            # Retain up to last 1000 durations per endpoint to bound memory
            if len(self.http_durations[endpoint]) > 1000:
                self.http_durations[endpoint] = self.http_durations[endpoint][-1000:]

    def record_agent_step(self, node: str, status: str = "success") -> None:
        """Tracks an agent orchestration node execution."""
        with self.lock:
            key = (node, status)
            self.agent_steps[key] = self.agent_steps.get(key, 0) + 1

    def record_tokens(self, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        """Tracks LLM prompt and completion token consumption."""
        with self.lock:
            self.token_usage[(model, "prompt")] = self.token_usage.get((model, "prompt"), 0) + prompt_tokens
            self.token_usage[(model, "completion")] = self.token_usage.get((model, "completion"), 0) + completion_tokens

    def record_retrieval(self, retriever_type: str = "hybrid") -> None:
        """Tracks knowledge retrieval queries by backend engine."""
        with self.lock:
            rtype = retriever_type.lower()
            self.retrieval_queries[rtype] = self.retrieval_queries.get(rtype, 0) + 1

    def record_calculation_error(self, module: str) -> None:
        """Tracks numerical calculation or verification failures."""
        with self.lock:
            self.calc_errors[module] = self.calc_errors.get(module, 0) + 1

    def generate_prometheus_exposition(self) -> str:
        """
        Renders all collected operational telemetry into standard Prometheus text format
        (RFC 0.0.4 specification).
        """
        lines: List[str] = []
        with self.lock:
            # Uptime Gauge
            uptime = time.time() - self.start_time
            lines.append("# HELP adida_process_uptime_seconds Total seconds since service startup.")
            lines.append("# TYPE adida_process_uptime_seconds gauge")
            lines.append(f"adida_process_uptime_seconds {uptime:.2f}")

            # Active Requests Gauge
            lines.append("# HELP adida_http_requests_active Number of concurrently active HTTP requests.")
            lines.append("# TYPE adida_http_requests_active gauge")
            lines.append(f"adida_http_requests_active {self.active_requests}")

            # Total HTTP Requests Counter
            lines.append("# HELP adida_http_requests_total Total number of HTTP requests processed.")
            lines.append("# TYPE adida_http_requests_total counter")
            if not self.http_requests:
                lines.append('adida_http_requests_total{endpoint="/health",method="GET",status="200"} 0')
            for (ep, meth, sc), cnt in sorted(self.http_requests.items()):
                lines.append(f'adida_http_requests_total{{endpoint="{ep}",method="{meth}",status="{sc}"}} {cnt}')

            # HTTP Duration Summary / Histogram
            lines.append("# HELP adida_http_request_duration_seconds HTTP request latency distribution in seconds.")
            lines.append("# TYPE adida_http_request_duration_seconds summary")
            for ep, durs in sorted(self.http_durations.items()):
                if durs:
                    count = len(durs)
                    total = sum(durs)
                    sorted_d = sorted(durs)
                    p50 = sorted_d[int(count * 0.50)]
                    p90 = sorted_d[min(int(count * 0.90), count - 1)]
                    p99 = sorted_d[min(int(count * 0.99), count - 1)]
                    lines.append(f'adida_http_request_duration_seconds{{endpoint="{ep}",quantile="0.5"}} {p50:.4f}')
                    lines.append(f'adida_http_request_duration_seconds{{endpoint="{ep}",quantile="0.9"}} {p90:.4f}')
                    lines.append(f'adida_http_request_duration_seconds{{endpoint="{ep}",quantile="0.99"}} {p99:.4f}')
                    lines.append(f'adida_http_request_duration_seconds_sum{{endpoint="{ep}"}} {total:.4f}')
                    lines.append(f'adida_http_request_duration_seconds_count{{endpoint="{ep}"}} {count}')

            # Agent Steps Counter
            lines.append("# HELP adida_agent_step_executions_total Total agent graph execution steps.")
            lines.append("# TYPE adida_agent_step_executions_total counter")
            for (node, stat), cnt in sorted(self.agent_steps.items()):
                lines.append(f'adida_agent_step_executions_total{{node="{node}",status="{stat}"}} {cnt}')

            # Token Usage Counter
            lines.append("# HELP adida_token_usage_total Total tokens consumed across LLM providers.")
            lines.append("# TYPE adida_token_usage_total counter")
            for (model, ttype), cnt in sorted(self.token_usage.items()):
                lines.append(f'adida_token_usage_total{{model="{model}",type="{ttype}"}} {cnt}')

            # Retrieval Queries Counter
            lines.append("# HELP adida_retrieval_queries_total Total knowledge queries processed by retriever.")
            lines.append("# TYPE adida_retrieval_queries_total counter")
            for rtype, cnt in sorted(self.retrieval_queries.items()):
                lines.append(f'adida_retrieval_queries_total{{engine="{rtype}"}} {cnt}')

            # Calculation Errors Counter
            lines.append("# HELP adida_calculation_errors_total Total deterministic mathematical validation errors.")
            lines.append("# TYPE adida_calculation_errors_total counter")
            for mod, cnt in sorted(self.calc_errors.items()):
                lines.append(f'adida_calculation_errors_total{{module="{mod}"}} {cnt}')

        return "\n".join(lines) + "\n"

    def get_summary(self) -> Dict[str, Any]:
        """Provides a JSON-serializable operational telemetry summary."""
        with self.lock:
            total_requests = sum(self.http_requests.values())
            all_durations = [d for durs in self.http_durations.values() for d in durs]
            avg_latency_ms = (sum(all_durations) / len(all_durations) * 1000.0) if all_durations else 0.0

            return {
                "uptime_seconds": round(time.time() - self.start_time, 2),
                "active_requests": self.active_requests,
                "total_http_requests": total_requests,
                "average_latency_ms": round(avg_latency_ms, 2),
                "retrieval_queries": dict(self.retrieval_queries),
                "agent_step_counts": {f"{k[0]}:{k[1]}": v for k, v in self.agent_steps.items()},
                "token_usage": {f"{k[0]}:{k[1]}": v for k, v in self.token_usage.items()},
                "calculation_errors": dict(self.calc_errors)
            }


# Global singleton instance
prometheus_metrics = ObservabilityRegistry()
