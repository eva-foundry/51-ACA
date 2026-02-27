/**
 * MoneyRangeBar -- visual low/high saving range bar.
 *
 * Renders:
 *   [$2,400 - $4,800 CAD]  [===========|~~~~]
 *
 * Fully accessible: aria-label describes the range in text.
 */

interface Props {
  low: number;
  high: number;
  maxValue?: number;
  currency?: string;
  locale?: string;
}

export function MoneyRangeBar({
  low,
  high,
  maxValue,
  currency = "CAD",
  locale = "en-CA",
}: Props) {
  const fmt = (n: number) =>
    new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(n);

  const cap = maxValue ?? high * 1.5;
  const lowPct = Math.min(100, (low / cap) * 100);
  const highPct = Math.min(100, ((high - low) / cap) * 100);

  return (
    <div
      aria-label={`Estimated saving: ${fmt(low)} to ${fmt(high)} ${currency} per year`}
      title={`${fmt(low)} - ${fmt(high)}`}
      style={{ marginBlock: 4 }}
    >
      <div style={{ fontSize: 12, color: "#555", marginBottom: 3 }}>
        {fmt(low)} &ndash; {fmt(high)}
      </div>
      <div
        style={{ height: 6, background: "#e0e0e0", borderRadius: 3, position: "relative" }}
      >
        <div
          style={{
            position: "absolute",
            left: `${lowPct}%`,
            width: `${highPct}%`,
            height: "100%",
            background: "#0078d4",
            borderRadius: 3,
          }}
        />
      </div>
    </div>
  );
}
