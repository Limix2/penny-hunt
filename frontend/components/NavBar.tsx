import Link from "next/link";
const links: [string, string][] = [["/", "Radar"], ["/scan", "Scan"], ["/map", "Map"], ["/stores", "Stores"]];
export function NavBar() {
  return (
    <nav className="fixed bottom-0 inset-x-0 z-50 bg-white border-t border-slate-200 safe-bottom">
      <div className="mx-auto max-w-2xl grid grid-cols-4">
        {links.map(([href, label]) => (
          <Link key={href} href={href} className="py-3 text-center text-sm font-medium text-slate-700 active:bg-slate-100">{label}</Link>
        ))}
      </div>
    </nav>
  );
}
