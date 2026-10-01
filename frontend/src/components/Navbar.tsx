"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getHealth, HealthResponse } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isOffline, setIsOffline] = useState<boolean>(false);

  const fetchHealthStatus = async () => {
    try {
      const res = await getHealth();
      setHealth(res);
      setIsOffline(false);
    } catch {
      setIsOffline(true);
      setHealth(null);
    }
  };

  useEffect(() => {
    fetchHealthStatus();
    const interval = setInterval(fetchHealthStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = () => {
    if (isOffline) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-300 dark:border-red-800">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          API Offline
        </span>
      );
    }
    if (!health) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
          <span className="w-2 h-2 rounded-full bg-gray-400 animate-pulse" />
          Connecting...
        </span>
      );
    }
    if (health.status === "ok") {
      return (
        <span
          title={`Loaded: ${health.loaded_models.join(", ")}`}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800 cursor-help"
        >
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          API Online ({health.loaded_models.length} Models)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-800">
        <span className="w-2 h-2 rounded-full bg-amber-500" />
        Degraded Status
      </span>
    );
  };

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white font-bold text-lg shadow-md group-hover:scale-105 transition-transform">
              🛡️
            </div>
            <div>
              <span className="font-bold text-slate-900 dark:text-white text-lg tracking-tight block">
                NIDS Predictor
              </span>
              <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono tracking-widest uppercase block -mt-1">
                Security Operations
              </span>
            </div>
          </Link>

          <nav className="flex items-center gap-1">
            <Link
              href="/"
              className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors ${
                pathname === "/"
                  ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-semibold"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
            >
              Single Predict
            </Link>
            <Link
              href="/batch"
              className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors ${
                pathname === "/batch"
                  ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-semibold"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
            >
              Batch Analysis
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-3">{getStatusBadge()}</div>
      </div>
    </header>
  );
}
