import { Radio } from "lucide-react";

const ROLE_CONFIG = {
  origin: { color: "#22d3ee", bg: "rgba(34,211,238,0.15)", label: "ORIGIN" },
  copy: { color: "#f59e0b", bg: "rgba(245,158,11,0.15)", label: "COPY" },
  amplify: { color: "#ef4444", bg: "rgba(239,68,68,0.15)", label: "AMPLIFY" },
};

export default function Timeline({ timeline }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="bg-surface border border-border rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Radio className="w-5 h-5 text-accent" />
          <span className="font-display text-sm font-semibold tracking-wide text-text-secondary uppercase">
            Propagation Timeline
          </span>
        </div>
        <p className="text-body text-text-tertiary">
          No propagation data found for this article.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 animate-fade-up-1">
      <div className="flex items-center gap-2 mb-5">
        <Radio className="w-5 h-5 text-accent" />
        <span className="font-display text-sm font-semibold tracking-wide text-text-secondary uppercase">
          Propagation Timeline
        </span>
      </div>

      <ol className="relative border-l-2 border-border pl-6 space-y-6" role="list">
        {timeline.map((event, i) => {
          const config = ROLE_CONFIG[event.role] || ROLE_CONFIG.copy;
          return (
            <li
              key={i}
              className="relative animate-fade-up"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div
                className="absolute -left-[29px] w-4 h-4 rounded-full border-2 border-bg"
                style={{ backgroundColor: config.color }}
              />

              <div className="flex items-start justify-between gap-3 flex-wrap">
                <div>
                  <p className="font-body text-body font-semibold text-text-primary">
                    {event.source}
                  </p>
                  {event.time && (
                    <p className="font-mono text-micro text-text-tertiary mt-0.5">
                      {event.time}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <span
                    className="text-micro tracking-widest uppercase px-2 py-1 rounded-md font-body font-medium"
                    style={{ color: config.color, backgroundColor: config.bg }}
                  >
                    {config.label}
                  </span>
                  {event.altered && (
                    <span className="text-micro text-disputed tracking-wide">
                      ⚠️ altered
                    </span>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
