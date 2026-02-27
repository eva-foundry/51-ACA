/**
 * EffortBadge -- colour-coded effort classification badge.
 * Effort classes: trivial | easy | medium | involved | strategic
 */

type EffortClass = "trivial" | "easy" | "medium" | "involved" | "strategic";

interface Props {
  effort: EffortClass | string;
}

const COLORS: Record<string, { bg: string; fg: string }> = {
  trivial:    { bg: "#d4edda", fg: "#155724" },
  easy:       { bg: "#d1ecf1", fg: "#0c5460" },
  medium:     { bg: "#fff3cd", fg: "#856404" },
  involved:   { bg: "#ffe5b4", fg: "#7b4e00" },
  strategic:  { bg: "#f8d7da", fg: "#721c24" },
};

export function EffortBadge({ effort }: Props) {
  const key = effort.toLowerCase();
  const { bg, fg } = COLORS[key] ?? { bg: "#e0e0e0", fg: "#333" };

  return (
    <span
      role="img"
      aria-label={`Effort: ${effort}`}
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 12,
        fontSize: 11,
        fontWeight: 600,
        textTransform: "capitalize",
        background: bg,
        color: fg,
      }}
    >
      {effort}
    </span>
  );
}
