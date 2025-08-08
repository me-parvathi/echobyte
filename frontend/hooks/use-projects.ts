"use client";

import { useEffect, useMemo, useState } from "react";
import { TimesheetApiService } from "@/lib/timesheet-api";

export type ProjectItem = { id: number | string; name: string };

export function useProjects() {
  const [projects, setProjects] = useState<ProjectItem[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await TimesheetApiService.getProjects();
        if (alive) setProjects(res || []);
      } catch (e) {
        if (alive)
          setError(
            e instanceof Error ? e : new Error("Failed to load projects")
          );
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const nameToId = useMemo(() => {
    const m = new Map<string, number | string>();
    if (projects) for (const p of projects) m.set(p.name, p.id);
    return m;
  }, [projects]);

  return { projects, nameToId, loading, error };
}
