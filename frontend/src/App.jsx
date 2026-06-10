import { useState } from "react";
import { Menu, X, Github, Zap, Globe, Shield } from "lucide-react";
import InputBar from "./components/InputBar";
import ScoreCard from "./components/ScoreCard";
import Timeline from "./components/Timeline";
import SourceGraph from "./components/SourceGraph";
import FactCheckBadge from "./components/FactCheckBadge";
import { analyzeUrl } from "./services/api";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <nav className="sticky top-0 z-50 flex items-center justify-between px-6 md:px-10 py-5 bg-bg/80 backdrop-blur-lg border-b border-border">
        <span className="font-display text-xl font-bold tracking-widest text-accent uppercase">
          SourceWatch
        </span>

        <div className="hidden md:flex items-center gap-8">
          {["How it works", "About", "GitHub"].map((link) => (
            <a
              key={link}
              href="#"
              className="text-sm text-text-secondary hover:text-text-primary transition-colors tracking-wide"
            >
              {link}
            </a>
          ))}
 </div>

        <button
          className="md:hidden text-text-primary"
          onClick={() => setMenuOpen(true)}
          aria-label="Open menu"
        >
          <Menu className="w-6 h-6" />
        </button>
      </nav>

      {menuOpen && (
        <div className="fixed inset-0 z-50 bg-bg/95 backdrop-blur-sm flex flex-col animate-fade-in">
          <div className="flex items-center justify-between px-6 py-5 border-b border-border">
            <span className="font-display text-xl font-bold tracking-widest text-accent uppercase">
              SourceWatch
            </span>
            <button
              className="text-text-primary"
              onClick={() => setMenuOpen(false)}
              aria-label="Close menu"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="flex-1 flex flex-col items-center justify-center gap-8">
            {["How it works", "About", "GitHub"].map((link, i) => (
              <a
                key={link}
                href="#"
                className="font-display text-4xl text-text-primary uppercase hover:text-accent transition-colors"
                style={{ transitionDelay: `${i * 80 + 100}ms` }}
                onClick={() => setMenuOpen(false)}
              >
                {link}
              </a>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

function Hero({ onAnalyze, loading }) {
  return (
    <section className="min-h-screen flex flex-col items-center justify-center px-6 md:px-10 pt-20 pb-10">
      <div className="w-full max-w-3xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 mb-8 animate-fade-up">
          <Globe className="w-4 h-4 text-text-tertiary" />
          <span className="text-micro tracking-widest uppercase text-text-tertiary">
            Vietnamese News Verifier
          </span>
        </div>

        <h1 className="font-display font-bold uppercase leading-[0.95] tracking-tight mb-6 animate-fade-up-1">
          <span className="block text-display text-text-primary">
            Know the source.
          </span>
          <span className="block text-display text-accent">Know the truth.</span>
        </h1>

        <p className="text-body text-text-secondary max-w-lg mx-auto leading-relaxed mb-10 animate-fade-up-2">
          Paste any Vietnamese news link. Get instant propagation timeline,
          source network, and credibility score.
        </p>

        <div className="flex justify-center mb-12 animate-fade-up-3">
          <InputBar onAnalyze={onAnalyze} loading={loading} />
        </div>

        <div className="flex flex-wrap justify-center gap-6 md:gap-12 animate-fade-up-4">
          {[
            { icon: Globe, text: "10+ Sources tracked" },
            { icon: Zap, text: "Real-time analysis" },
            { icon: Shield, text: "Free forever" },
          ].map(({ icon: Icon, text }) => (
            <div
              key={text}
              className="flex items-center gap-2 text-micro tracking-widest uppercase text-text-tertiary"
            >
              <Icon className="w-4 h-4" />
              {text}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Results({ data }) {
  if (!data) return null;

  const { article, claims, propagation, source_network, fact_checks, credibility_score } = data;

  return (
    <section className="px-6 md:px-10 py-16 max-w-7xl mx-auto">
      <div className="mb-8 animate-fade-up">
        <p className="text-micro tracking-widest uppercase text-text-tertiary mb-2">
          Analysis Result
        </p>
        <h2 className="font-display text-heading font-bold text-text-primary">
          {article?.title || "Article Analysis"}
        </h2>
        {article?.source && (
          <p className="text-small text-text-tertiary mt-1">{article.source}</p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6 mb-6">
        <ScoreCard score={credibility_score} />
        <Timeline timeline={propagation?.timeline} />
      </div>

      <div className="mb-6">
        <SourceGraph sourceNetwork={source_network} />
      </div>

      {claims && claims.length > 0 && (
        <div>
          <h3 className="font-display text-sm font-semibold tracking-wide text-text-secondary uppercase mb-4">
            Claims & Fact-Check
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {claims.map((claim, i) => (
              <FactCheckBadge
                key={claim.id}
                factCheck={fact_checks?.find((fc) => fc.claim_id === claim.id) || {
                  claim: claim.text,
                  status: "unverified",
                  source: "Custom DB",
                }}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function Footer() {
  return (
    <footer className="px-6 py-8 border-t border-border text-center">
      <p className="text-micro text-text-tertiary tracking-wide">
        Built for Vietnamese internet ·{" "}
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent hover:underline inline-flex items-center gap-1"
        >
          <Github className="w-3.5 h-3.5" />
          View on GitHub
        </a>
      </p>
    </footer>
  );
}

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleAnalyze(url) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeUrl(url);
      setResult(data);
    } catch (err) {
      setError(err.message || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-bg text-text-primary">
      <Navbar />
      <Hero onAnalyze={handleAnalyze} loading={loading} />

      {error && (
        <div className="px-6 md:px-10 max-w-3xl mx-auto mb-8">
          <div className="bg-false/10 border border-false/30 rounded-xl p-4 text-false text-body">
            {error}
          </div>
        </div>
      )}

      {result && <Results data={result} />}

      <Footer />
    </div>
  );
}
