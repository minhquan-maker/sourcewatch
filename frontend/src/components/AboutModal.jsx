import { Brain, Database, Globe, Github, Heart } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Claim Extraction",
    desc: "Gemini 3.5 Flash identifies verifiable factual claims — from statistics to statements — that can be independently cross-checked.",
  },
  {
    icon: Database,
    title: "10+ Vietnamese Sources Indexed",
    desc: "We maintain a curated database of Vietnam's major news outlets. Propagation tracking shows where claims spread and how they changed.",
  },
  {
    icon: Globe,
    title: "Open-Source & Transparent",
    desc: "SourceWatch is built for the Vietnamese internet community. All analysis logic and source data is visible on GitHub.",
  },
];

export default function AboutModal() {
  return (
    <div className="space-y-6">
      <p className="text-body text-text-secondary leading-relaxed">
        SourceWatch is a news credibility analyzer built for Vietnamese readers. We help you understand where information comes from, how it spreads, and whether the sources are trustworthy.
      </p>

      <div className="space-y-4">
        {features.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="flex gap-4">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center">
              <Icon className="w-5 h-5 text-accent" />
            </div>
            <div>
              <h3 className="font-display text-body font-semibold text-text-primary mb-1">{title}</h3>
              <p className="text-small text-text-secondary leading-relaxed">{desc}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="pt-4 border-t border-border">
        <h4 className="font-display text-small font-semibold text-text-secondary uppercase tracking-wide mb-3">
          Tech Stack
        </h4>
        <div className="flex flex-wrap gap-2">
          {[
            "Gemini 3.5 Flash",
            "Playwright",
            "ChromaDB",
            "PostgreSQL",
            "FastAPI",
            "React 19",
            "Tailwind v4",
          ].map((tech) => (
            <span
              key={tech}
              className="px-2.5 py-1 rounded-md bg-surface text-micro text-text-tertiary border border-border"
            >
              {tech}
            </span>
          ))}
        </div>
      </div>

      <div className="pt-2 border-t border-border flex items-center gap-2">
        <Heart className="w-4 h-4 text-accent" />
        <p className="text-small text-text-tertiary">
          Built with care for the Vietnamese internet community
        </p>
      </div>
    </div>
  );
}