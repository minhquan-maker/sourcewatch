import { Globe, Sparkles, Radio, Shield } from "lucide-react";

const steps = [
  {
    icon: Globe,
    title: "1. Fetch Article",
    desc: "We use a headless browser to extract the full article text from any Vietnamese news URL you paste — bypassing paywalls and JS rendering.",
  },
  {
    icon: Sparkles,
    title: "2. Extract Claims",
    desc: "Gemini AI scans the article and extracts 3–7 verifiable claims — factual statements that can be independently checked.",
  },
  {
    icon: Radio,
    title: "3. Track Propagation",
    desc: "We search our indexed database of 10+ Vietnamese news sources to find where each claim appeared, building a propagation timeline.",
  },
  {
    icon: Shield,
    title: "4. Score Credibility",
    desc: "Your article gets a 0–10 credibility score: 40% source reputation, 30% claim consistency, 30% amplification pattern across the source network.",
  },
];

export default function HowItWorksModal() {
  return (
    <div className="space-y-6">
      <p className="text-body text-text-secondary leading-relaxed">
        SourceWatch analyzes Vietnamese news articles through a 4-step pipeline to help you understand how information spreads and whether it can be trusted.
      </p>
      <div className="space-y-5">
        {steps.map(({ icon: Icon, title, desc }) => (
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
      <div className="pt-2 border-t border-border">
        <p className="text-small text-text-tertiary">
          <span className="text-accent font-semibold">10 sources tracked:</span> vnexpress.net, tuoitre.vn, vov.vn, vtv.vn, dantri.com.vn, thanhnien.vn, zing.vn, laodong.vn, tienphong.vn, nguoiduatin.vn
        </p>
      </div>
    </div>
  );
}
