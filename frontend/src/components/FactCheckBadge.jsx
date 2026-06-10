import { CheckCircle, AlertCircle, XCircle, HelpCircle, ExternalLink } from "lucide-react";

const STATUS_CONFIG = {
  verified: {
    icon: CheckCircle,
    color: "#22c55e",
    bg: "rgba(34,197,94,0.15)",
    label: "VERIFIED",
  },
  unverified: {
    icon: HelpCircle,
    color: "#94a3b8",
    bg: "rgba(148,163,184,0.15)",
    label: "UNVERIFIED",
  },
  disputed: {
    icon: AlertCircle,
    color: "#f59e0b",
    bg: "rgba(245,158,11,0.15)",
    label: "DISPUTED",
  },
  false: {
    icon: XCircle,
    color: "#ef4444",
    bg: "rgba(239,68,68,0.15)",
    label: "FALSE",
  },
};

export default function FactCheckBadge({ factCheck }) {
  const config = STATUS_CONFIG[factCheck.status] || STATUS_CONFIG.unverified;
  const Icon = config.icon;

  return (
    <div className="bg-surface border border-border rounded-xl p-5 animate-scale-in">
      <div className="flex items-start justify-between gap-3 mb-3">
<div
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-micro tracking-widest uppercase font-body font-semibold"
          style={{ color: config.color, backgroundColor: config.bg }}
        >
          <Icon className="w-3.5 h-3.5" />
          {config.label}
        </div>
        {factCheck.url && (
          <a
            href={factCheck.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-text-tertiary hover:text-accent transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>

      <p className="font-body text-body text-text-primary leading-relaxed mb-3">
        "{factCheck.claim}"
      </p>

      <div className="flex items-center gap-2">
        <span className="text-micro text-text-tertiary tracking-wide">
          via {factCheck.source}
        </span>
        {factCheck.date && (
          <span className="text-micro text-text-tertiary font-mono">
            · {factCheck.date}
          </span>
        )}
      </div>
    </div>
  );
}
