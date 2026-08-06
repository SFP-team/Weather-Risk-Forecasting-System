"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function NavInner({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const params = useSearchParams();
  const farm = params.get("farm");
  const q = farm ? `?farm=${encodeURIComponent(farm)}` : "";

  const links = [
    { href: `/${q}`, label: "Tonight", match: pathname === "/" },
    { href: `/seven-day${q}`, label: "7-Day", match: pathname.startsWith("/seven-day") },
    { href: `/season${q}`, label: "Season", match: pathname.startsWith("/season") },
    { href: `/farm${q}`, label: "My Farm", match: pathname.startsWith("/farm") },
  ];

  return (
    <>
      <main>
        <header className="topbar">
          <div className="brand">
            <h1>Blueberry Risk Co-Pilot</h1>
            <span>Florida freeze · chill · seasonal risk</span>
          </div>
          <nav className="nav">
            {links.map((l) => (
              <Link key={l.label} href={l.href} className={l.match ? "active" : ""}>
                {l.label}
              </Link>
            ))}
          </nav>
        </header>
        {children}
        <p className="disclaimer">
          Decision support prototype only. Not a substitute for National Weather Service
          warnings, field thermometers, or UF/IFAS Extension freeze advice. Seasonal cards
          are probabilistic risk outlooks — not daily weather 90 days out. Data: FAWN-style
          local history, Open-Meteo, NWS when available.
        </p>
      </main>
      <nav className="bottom-nav">
        {links.map((l) => (
          <Link key={l.label} href={l.href} className={l.match ? "active" : ""}>
            {l.label}
          </Link>
        ))}
      </nav>
    </>
  );
}

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<main className="loading">Loading…</main>}>
      <NavInner>{children}</NavInner>
    </Suspense>
  );
}
