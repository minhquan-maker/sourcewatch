import { useState } from "react";
import { Search, Zap, ArrowRight } from "lucide-react";

export default function InputBar({ onAnalyze, loading }) {
  const [url, setUrl] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) return;
    onAnalyze(url.trim());
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-2xl animate-fade-up-2"
    >
      <div className="relative flex items-center gap-3 bg-surface border border-border rounded-2xl px-4 py-3 transition-all duration-200 focus-within:border-border-light focus-within:ring-2 focus-within:ring-accent/20 hover:border-border-light">
        <Search className="w-5 h-5 text-text-tertiary shrink-0" />
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste a news link from VnExpress, Dân Trí, Zing..."
          className="flex-1 bg-transparent text-body text-text-primary placeholder:text-text-tertiary outline-none font-body"
          disabled={loading}
          required
        />
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="shrink-0 flex items-center gap-2 bg-accent text-bg font-semibold px-5 py-2.5 rounded-xl text-sm tracking-wide transition-all duration-150 hover:bg-accent/90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed animate-pulse-glow"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-bg/30 border-t-bg rounded-full animate-spin" />
              Analyzing
            </span>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              Analyze
            </>
          )}
        </button>
      </div>
    </form>
  );
}
