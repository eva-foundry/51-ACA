# EVA-STORY: ACA-14-001
import uuid
from datetime import datetime

class ACALMTracer:
    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        self.trace_log = []

    def trace(self, phase: str, message: str):
        trace_entry = {
            "correlation_id": self.correlation_id,
            "phase": phase,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.trace_log.append(trace_entry)
        print(f"[TRACE:{self.correlation_id}] [{phase}] {message}")  # [TRACE] token per encoding rules

    def get_trace_log(self):
        return self.trace_log

    def save_trace_log(self, sprint_id: str):
        file_path = f".eva/sprints/{sprint_id}-trace-log.json"
        with open(file_path, "w", encoding="ascii") as f:
            json.dump(self.trace_log, f, ensure_ascii=True, indent=4)
        print(f"[INFO:{self.correlation_id}] Trace log saved to {file_path}")  # [INFO] token per encoding rules
