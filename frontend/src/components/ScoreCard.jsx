import { useEffect, useRef } from "react";
import { Shield } from "lucide-react";

const RADIUS = 54;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function getScoreColor(score) {
  if (score >= 7) return "#22c55e";
  if (score >= 4) return "#f59e0b";
  return "#ef4444";
}

function ScoreRing({ score }) {
  const circleRef = useRef(null);
  const offset = CIRCUMFERENCE - (score / 10) * CIRCUMFERENCE;
  const color = getScoreColor(score);

  useEffect(() => {
    if (circleRef.current) {
      circleRef.current.style.strokeDashoffset = CIRCUMFERENCE;
      setTimeout(() => {
        if (circleRef.current) {
          circleRef.current.style.transition = "stroke-dashoffset 1.5s ease-out";
          circleRef.current.style.strokeDashoffset = offset;
        }
      }, 100);
    }
  }, [score, offset]);

  return (
    <svg
      width="140"
      height="140"
      viewBox="0 0 140 140"
      className="transform -rotate-90"
    >
      <circle
        cx="70"
        cy="70"
        r={RADIUS}
        fill="none"
        stroke="#1e2a3d"
        strokeWidth="10"
      />
      <circle
        ref={circleRef}
        cx="70"
        cy="70"
        r={RADIUS}
        fill="none"
        stroke={color}
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={CIRCUMFERENCE}
        strokeDashoffset={CIRCUMFERENCE}
      />
    </svg>
  );
}

export default function ScoreCard({ score }) {
  const { total, breakdown } = score;
  const color = getScoreColor(total);

  const bars = [
    { label: "Source Reputation", value: breakdown?.source_reputation ?? 5 },
    { label: "Claim Consistency", value: breakdown?.claim_consistency ?? 5 },
    { label: "Amplification", value: breakdown?.amplification_pattern ?? 5 },
  ];

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 animate-scale-in">
      <div className="flex items-center gap-2 mb-5">
        <Shield className="w-5 h-5 text-accent" />
        <span className="font-display text-sm font-semibold tracking-wide text-text-secondary uppercase">
          Credibility Score
        </span>
      </div>

      <div className="flex flex-col items-center mb-6">
        <div className="relative">
          <ScoreRing score={total} />
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span
              className="font-mono text-score font-bold"
              style={{ color }}
 >
              {total}
            </span>
            <span className="text-micro text-text-tertiary font-mono">/10</span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {bars.map((bar) => (
          <div key={bar.label}>
            <div className="flex justify-between items-center mb-1">
              <span className="text-micro text-text-secondary tracking-wide">
                {bar.label}
              </span>
              <span className="font-mono text-micro text-text-tertiary">
                {bar.value}
              </span>
            </div>
            <div className="h-1.5 bg-border rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-1000 ease-out"
                style={{
                  width: `${bar.value * 10}%`,
                  backgroundColor: getScoreColor(bar.value),
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
