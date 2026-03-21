from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass
class StepHandle:
    step_name: str
    step_order: int
    started_at: str
    started_perf: float


class TraceRecorder:
    def __init__(self, run_id: str, trace_id: str) -> None:
        self.run_id = run_id
        self.trace_id = trace_id
        self.steps: list[dict[str, object]] = []
        self.tool_calls: list[dict[str, object]] = []
        self.error_summary: str | None = None
        self.metadata: dict[str, object] = {}

    def set_metadata(self, **metadata: object) -> None:
        for key, value in metadata.items():
            if value is not None:
                self.metadata[key] = value

    def start_step(self, step_name: str, input_ref: str | None = None) -> StepHandle:
        order = len(self.steps) + 1
        handle = StepHandle(
            step_name=step_name,
            step_order=order,
            started_at=utc_now(),
            started_perf=perf_counter(),
        )
        self.steps.append(
            {
                "step_name": step_name,
                "step_order": order,
                "status": "running",
                "started_at": handle.started_at,
                "ended_at": handle.started_at,
                "latency_ms": 0,
                "tool_calls": 0,
                "confidence": None,
                "input_ref": input_ref,
                "output_ref": None,
                "error_message": None,
            }
        )
        return handle

    def finish_step(
        self,
        handle: StepHandle,
        *,
        status: str,
        confidence: str | None = None,
        output_ref: str | None = None,
        error_message: str | None = None,
    ) -> None:
        ended_at = utc_now()
        latency_ms = int((perf_counter() - handle.started_perf) * 1000)
        step = self.steps[handle.step_order - 1]
        step["status"] = status
        step["ended_at"] = ended_at
        step["latency_ms"] = latency_ms
        step["confidence"] = confidence
        step["output_ref"] = output_ref
        step["error_message"] = error_message
        step["tool_calls"] = sum(1 for call in self.tool_calls if call["step_name"] == handle.step_name)
        if error_message and self.error_summary is None:
            self.error_summary = error_message

    def record_tool_call(
        self,
        *,
        step_name: str,
        tool_name: str,
        input_summary: str,
        output_count: int,
        status: str = "completed",
        error_message: str | None = None,
        started_perf: float | None = None,
        started_at: str | None = None,
    ) -> None:
        end_perf = perf_counter()
        self.tool_calls.append(
            {
                "step_name": step_name,
                "tool_name": tool_name,
                "status": status,
                "started_at": started_at or utc_now(),
                "ended_at": utc_now(),
                "duration_ms": int((end_perf - (started_perf or end_perf)) * 1000),
                "input_summary": input_summary,
                "output_count": output_count,
                "error_message": error_message,
            }
        )

    def export_payload(self) -> dict[str, object]:
        return {
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "steps": self.steps,
            "spans": self.steps,
            "tool_calls": self.tool_calls,
            "error_summary": self.error_summary,
            "metadata": self.metadata,
        }
