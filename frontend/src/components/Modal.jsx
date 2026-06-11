import { X } from "lucide-react";

export default function Modal({ open, onClose, title, children }) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-bg/90 backdrop-blur-sm" />
      <div
        className="relative bg-surface border border-border rounded-2xl w-full max-w-lg max-h-[85vh] overflow-y-auto animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 flex items-center justify-between px-6 py-4 border-b border-border bg-surface rounded-t-2xl">
          <h2 className="font-display text-lg font-bold text-text-primary">{title}</h2>
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-text-primary transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}
