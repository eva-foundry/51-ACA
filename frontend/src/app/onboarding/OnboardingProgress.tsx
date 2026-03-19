// EVA-STORY: ACA-15-012
import { useMemo } from "react";

type GateStatus = "pending" | "in_progress" | "completed" | "failed";

type OnboardingGate = {
  id: string;
  title: string;
  status: GateStatus;
};

type Props = {
  roleAssessment: "ready" | "blocked";
  preflight: "pass" | "warn" | "fail";
  gates: OnboardingGate[];
};

export function OnboardingProgress({ roleAssessment, preflight, gates }: Props) {
  const completed = useMemo(() => gates.filter((g) => g.status === "completed").length, [gates]);
  const percent = gates.length === 0 ? 0 : Math.round((completed / gates.length) * 100);

  return (
    <section aria-label="Onboarding extraction progress" style={{ border: "1px solid #d0d7de", borderRadius: 8, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Onboarding Progress</h2>
      <p>Role assessment: <strong>{roleAssessment}</strong></p>
      <p>Preflight status: <strong>{preflight}</strong></p>
      <div aria-label="progress-bar" style={{ background: "#eef2f6", borderRadius: 6, height: 12, overflow: "hidden" }}>
        <div style={{ width: `${percent}%`, background: "#0f766e", height: "100%", transition: "width 0.3s ease" }} />
      </div>
      <p>{completed}/{gates.length} gates complete ({percent}%)</p>
      <ul>
        {gates.map((gate) => (
          <li key={gate.id}>
            {gate.title} - {gate.status}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default OnboardingProgress;
