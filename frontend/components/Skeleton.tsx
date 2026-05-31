export function CardSkeleton() {
  return (
    <div className="bg-card dark:bg-slate-900 rounded-2xl shadow-card p-3 flex gap-3 animate-pulse">
      <div className="w-20 h-20 rounded-xl bg-slate-200 dark:bg-slate-800" />
      <div className="flex-1 space-y-2 py-1">
        <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-3/4" />
        <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-1/2" />
        <div className="h-5 bg-slate-200 dark:bg-slate-800 rounded w-1/3 mt-3" />
      </div>
    </div>
  );
}

export function SkeletonList({ n = 5 }: { n?: number }) {
  return <div className="grid gap-3">{Array.from({ length: n }).map((_, i) => <CardSkeleton key={i} />)}</div>;
}
