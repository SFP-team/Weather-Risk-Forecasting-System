"use client";

import { useRouter, usePathname, useSearchParams } from "next/navigation";
import type { Farm } from "@/lib/api";

export function FarmPicker({
  farms,
  selectedId,
}: {
  farms: Farm[];
  selectedId: string;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  return (
    <div className="card" style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
      <label className="muted" htmlFor="farm">
        Farm
      </label>
      <select
        id="farm"
        value={selectedId}
        onChange={(e) => {
          const next = new URLSearchParams(params.toString());
          next.set("farm", e.target.value);
          router.push(`${pathname}?${next.toString()}`);
        }}
        style={{ minWidth: 260 }}
      >
        {farms.map((f) => (
          <option key={f.id} value={f.id}>
            {f.name} ({f.county})
          </option>
        ))}
      </select>
    </div>
  );
}
