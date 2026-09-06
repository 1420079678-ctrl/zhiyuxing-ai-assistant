from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from typing import Any, Dict


class TelemetryCollector:
    """Thread-safe Prometheus-compatible telemetry collector for ZhiYuXing Copilot."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.start_time = time.time()
        self.request_count: Dict[str, int] = defaultdict(int)
        self.request_latency_sum: Dict[str, float] = defaultdict(float)
        self.chat_requests: Dict[tuple, int] = defaultdict(int)
        self.guardrail_triggers: Dict[str, int] = defaultdict(int)
        self.tokens_estimated: int = 0

    def record_request(self, method: str, path: str, status_code: int, duration: float) -> None:
        key = f'{method}:{path}:{status_code}'
        with self._lock:
            self.request_count[key] += 1
            self.request_latency_sum[f'{method}:{path}'] += duration

    def record_chat(self, mode: str, provider: str, model: str, scenario: str, is_stream: bool = False) -> None:
        key = (mode, provider, model, scenario, "true" if is_stream else "false")
        with self._lock:
            self.chat_requests[key] += 1

    def record_guardrail(self, risk_level: str) -> None:
        with self._lock:
            self.guardrail_triggers[risk_level] += 1

    def record_tokens(self, count: int) -> None:
        with self._lock:
            self.tokens_estimated += count

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            total_reqs = sum(self.request_count.values())
            total_chats = sum(self.chat_requests.values())
            total_guardrails = sum(self.guardrail_triggers.values())
            uptime = time.time() - self.start_time
            return {
                "uptime_seconds": round(uptime, 2),
                "total_http_requests": total_reqs,
                "total_chat_requests": total_chats,
                "guardrail_triggers": total_guardrails,
                "tokens_estimated": self.tokens_estimated,
            }

    def format_prometheus(self) -> str:
        with self._lock:
            lines = [
                "# HELP zhiyuxing_uptime_seconds Total runtime of the service in seconds",
                "# TYPE zhiyuxing_uptime_seconds gauge",
                f"zhiyuxing_uptime_seconds {time.time() - self.start_time:.2f}",
                "",
                "# HELP zhiyuxing_http_requests_total Total number of HTTP requests processed",
                "# TYPE zhiyuxing_http_requests_total counter",
            ]
            for key, count in sorted(self.request_count.items()):
                method, path, status = key.split(":")
                lines.append(f'zhiyuxing_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}')

            lines.extend([
                "",
                "# HELP zhiyuxing_chat_requests_total Total number of chat completions requested",
                "# TYPE zhiyuxing_chat_requests_total counter",
            ])
            for (mode, provider, model, scenario, stream_str), count in sorted(self.chat_requests.items()):
                lines.append(
                    f'zhiyuxing_chat_requests_total{{mode="{mode}",provider="{provider}",model="{model}",scenario="{scenario}",stream="{stream_str}"}} {count}'
                )

            lines.extend([
                "",
                "# HELP zhiyuxing_safety_guardrail_triggers_total Guardrail safety filter triggers by risk level",
                "# TYPE zhiyuxing_safety_guardrail_triggers_total counter",
            ])
            for level, count in sorted(self.guardrail_triggers.items()):
                lines.append(f'zhiyuxing_safety_guardrail_triggers_total{{level="{level}"}} {count}')

            lines.extend([
                "",
                "# HELP zhiyuxing_tokens_estimated_total Estimated input and output token count",
                "# TYPE zhiyuxing_tokens_estimated_total counter",
                f"zhiyuxing_tokens_estimated_total {self.tokens_estimated}",
                "",
            ])
            return "\n".join(lines)


# Global singleton instance
telemetry = TelemetryCollector()
