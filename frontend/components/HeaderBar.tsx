export function HeaderBar({ title, subtitle, right }:
  { title: string; subtitle?: string; right?: React.ReactNode }) {
  return (
    <header className="bg-gradient-to-br from-primary to-secondary text-white rounded-b-3xl px-5 pt-9 pb-8 shadow-card">
      <div className="mx-auto max-w-2xl flex items-end justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-2xl font-extrabold tracking-tight">{title}</h1>
          {subtitle && <p className="text-white/80 text-sm mt-0.5">{subtitle}</p>}
        </div>
        {right}
      </div>
    </header>
  );
}
