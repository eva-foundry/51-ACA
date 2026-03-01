# EVA-STORY: ACA-14-001
import uuid
import json
from datetime import datetime
from .aca_lm_tracer import ACALMTracer

class SprintContext:
    def __init__(self, sprint_id: str):
        self.sprint_id = sprint_id
        self.correlation_id = self._generate_correlation_id()
        self.timeline = []
        self.lm_calls = []
        self.tracer = ACALMTracer(self.correlation_id)

    def _generate_correlation_id(self) -> str:
        today = datetime.utcnow().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8]
        return f"ACA-{self.sprint_id}-{today}-{unique_id}"

    def log(self, phase: str, message: str):
        log_entry = f"[TRACE:{self.correlation_id}] [{phase}] {message}"
        print(log_entry)  # [TRACE] token per encoding rules
        self.timeline.append({"phase": phase, "message": message, "timestamp": datetime.utcnow().isoformat()})

    def record_lm_call(self, model: str, tokens_in: int, tokens_out: int, phase: str):
        lm_call = {
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "phase": phase,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.lm_calls.append(lm_call)
        self.log(phase, f"LM call recorded: {lm_call}")

    def save(self):
        context_data = {
            "correlation_id": self.correlation_id,
            "timeline": self.timeline,
            "lm_calls": self.lm_calls
        }
        file_path = f".eva/sprints/{self.sprint_id}-context.json"
        with open(file_path, "w", encoding="ascii") as f:
            json.dump(context_data, f, ensure_ascii=True, indent=4)
        self.log("SAVE", f"Context saved to {file_path}")
