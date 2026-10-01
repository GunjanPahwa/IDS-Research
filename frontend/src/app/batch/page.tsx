"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import {
  APIClientError,
  Features,
  getModelInfo,
  ModelInfoResponse,
  predictBatch,
  PredictionResult,
} from "@/lib/api";

interface FlowRow {
  rowNum: number;
  features: Features;
  result?: PredictionResult;
  error?: string;
}

export default function BatchAnalysisPage() {
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [dataset, setDataset] = useState<string>("unsw_nb15");

  // Input & Parse State
  const [csvText, setCsvText] = useState<string>("");
  const [parsedFlows, setParsedFlows] = useState<Features[]>([]);
  const [parseError, setParseError] = useState<string | null>(null);

  // Execution State
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<PredictionResult[] | null>(null);
  const [error, setError] = useState<{ code?: string; message: string; details?: unknown } | null>(null);

  // Filter State
  const [filter, setFilter] = useState<"all" | "attacks_only">("all");

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const info = await getModelInfo();
        setModelInfo(info);
        if (info.default_dataset) {
          setDataset(info.default_dataset);
        }
      } catch {
        // Fallback defaults
      }
    };
    fetchInfo();
  }, []);

  const isUnverified = modelInfo
    ? modelInfo.datasets_info[dataset]?.verified === false
    : ["cic_ids2017", "cse_cic_ids2018", "uwf_zeekdata24"].includes(dataset);

  const handleCsvChange = (text: string) => {
    setCsvText(text);
    setParseError(null);
    setResults(null);
    setError(null);

    if (!text.trim()) {
      setParsedFlows([]);
      return;
    }

    try {
      const lines = text.trim().split("\n");
      if (lines.length < 2) {
        setParseError("CSV must contain a header row and at least one data row.");
        setParsedFlows([]);
        return;
      }

      const header = lines[0].split(",").map((c) => c.trim().toLowerCase());
      const required = ["duration", "src_bytes", "dst_bytes", "protocol", "service"];
      const missing = required.filter((r) => !header.includes(r));
      if (missing.length > 0) {
        setParseError(`CSV header missing required columns: ${missing.join(", ")}`);
        setParsedFlows([]);
        return;
      }

      const durIdx = header.indexOf("duration");
      const srcIdx = header.indexOf("src_bytes");
      const dstIdx = header.indexOf("dst_bytes");
      const protoIdx = header.indexOf("protocol");
      const srvIdx = header.indexOf("service");

      const flows: Features[] = [];
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const cols = line.split(",").map((c) => c.trim());
        if (cols.length < required.length) continue;

        const dur = parseFloat(cols[durIdx]);
        const src = parseInt(cols[srcIdx], 10);
        const dst = parseInt(cols[dstIdx], 10);
        const proto = cols[protoIdx] || "tcp";
        const srv = cols[srvIdx] || "-";

        if (isNaN(dur) || dur < 0 || isNaN(src) || src < 0 || isNaN(dst) || dst < 0) {
          setParseError(`Line ${i + 1} contains invalid or negative numbers.`);
          return;
        }

        flows.push({
          duration: dur,
          src_bytes: src,
          dst_bytes: dst,
          protocol: proto.toLowerCase(),
          service: srv.toLowerCase(),
        });
      }

      if (flows.length > 1000) {
        setParseError(`CSV contains ${flows.length} rows, exceeding maximum batch size of 1000.`);
        setParsedFlows([]);
        return;
      }

      setParsedFlows(flows);
    } catch (err: unknown) {
      setParseError(`CSV parsing error: ${err instanceof Error ? err.message : "Invalid CSV syntax"}`);
      setParsedFlows([]);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      handleCsvChange(content);
    };
    reader.readAsText(file);
  };

  const handleLoadSampleCsv = () => {
    const sample = `duration,src_bytes,dst_bytes,protocol,service
0.5,100,200,tcp,http
0.0,0,0,tcp,http
10.5,50000,100000,udp,dns
1.2,500,0,tcp,ftp
0.001,64,64,icmp,-
0.0,0,0,udp,dhcp`;
    handleCsvChange(sample);
  };

  const handleSubmitBatch = async () => {
    if (parsedFlows.length === 0) return;

    setLoading(true);
    setError(null);
    try {
      const res = await predictBatch({
        dataset,
        flows: parsedFlows,
      });
      setResults(res);
    } catch (err: unknown) {
      if (err instanceof APIClientError) {
        setError({ code: err.code, message: err.message, details: err.details });
      } else {
        setError({ message: "Failed to execute batch inference request." });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCsv = () => {
    if (!results || parsedFlows.length === 0) return;

    const header = "row_index,duration,src_bytes,dst_bytes,protocol,service,predicted_label,is_attack,confidence_pct\n";
    const rows = results
      .map((res, i) => {
        const f = parsedFlows[i];
        const conf = (res.confidence * 100).toFixed(2);
        return `${i + 1},${f.duration},${f.src_bytes},${f.dst_bytes},${f.protocol},${f.service},"${res.label}",${res.is_attack},${conf}`;
      })
      .join("\n");

    const blob = new Blob([header + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `nids_predictions_${dataset}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Metrics calculations
  const totalCount = results?.length || 0;
  const attackCount = results?.filter((r) => r.is_attack).length || 0;
  const benignCount = totalCount - attackCount;
  const attackPct = totalCount > 0 ? ((attackCount / totalCount) * 100).toFixed(1) : "0.0";

  const attackCategoryCounts: Record<string, number> = {};
  results?.forEach((r) => {
    if (r.is_attack && r.attack_type) {
      attackCategoryCounts[r.attack_type] = (attackCategoryCounts[r.attack_type] || 0) + 1;
    }
  });

  const filteredResults = results
    ? results.filter((r) => (filter === "attacks_only" ? r.is_attack : true))
    : [];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              Batch Network Flow Analysis
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Analyze batches of up to 1,000 network flows in a single vectorized model evaluation call.
            </p>
          </div>

          <button
            type="button"
            onClick={handleLoadSampleCsv}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg border border-indigo-300 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 transition-colors self-start sm:self-auto"
          >
            📋 Load Sample CSV Data
          </button>
        </div>

        {/* Input & Config Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-5 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-5">
            <h2 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <span>📂</span> Batch Upload & Configuration
            </h2>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Target Dataset Model
              </label>
              <select
                value={dataset}
                onChange={(e) => setDataset(e.target.value)}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {modelInfo?.available_datasets ? (
                  modelInfo.available_datasets.map((ds) => {
                    const verified = modelInfo.datasets_info[ds]?.verified;
                    return (
                      <option key={ds} value={ds}>
                        {ds}
                        {verified === false ? " (unverified)" : ""} {modelInfo.datasets_info[ds]?.is_loaded ? "✓" : "(Not Loaded)"}
                      </option>
                    );
                  })
                ) : (
                  <>
                    <option value="unsw_nb15">unsw_nb15</option>
                    <option value="kdd99">kdd99</option>
                    <option value="nsl_kdd">nsl_kdd</option>
                    <option value="cic_ids2017">cic_ids2017 (unverified)</option>
                    <option value="cse_cic_ids2018">cse_cic_ids2018 (unverified)</option>
                    <option value="uwf_zeekdata24">uwf_zeekdata24 (unverified)</option>
                  </>
                )}
              </select>
              {isUnverified && (
                <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-amber-800 dark:text-amber-200 text-xs flex items-start gap-2 mt-2">
                  <span className="text-sm leading-none">⚠️</span>
                  <div>
                    <span className="font-semibold block">Unverified Dataset Warning</span>
                    <span>
                      The dataset <strong>{dataset}</strong> is unverified. Raw test-set data for this benchmark is not included in the repository.
                    </span>
                  </div>
                </div>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Upload CSV File
              </label>
              <input
                type="file"
                accept=".csv,.txt"
                onChange={handleFileUpload}
                className="w-full text-xs text-slate-600 dark:text-slate-400 file:mr-3 file:py-1.5 file:px-3.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 dark:file:bg-indigo-950 dark:file:text-indigo-300 hover:file:bg-indigo-100 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Or Paste CSV Data
              </label>
              <textarea
                rows={6}
                value={csvText}
                onChange={(e) => handleCsvChange(e.target.value)}
                placeholder="duration,src_bytes,dst_bytes,protocol,service&#10;0.5,100,200,tcp,http&#10;0.0,0,0,tcp,http"
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 p-3 text-xs font-mono text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {parseError && (
              <div className="p-3 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-900 text-xs text-rose-700 dark:text-rose-400">
                ⚠️ {parseError}
              </div>
            )}

            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 font-mono">
              <span>Parsed flows: {parsedFlows.length}</span>
              <span>Max allowed: 1,000</span>
            </div>

            <button
              type="button"
              onClick={handleSubmitBatch}
              disabled={loading || parsedFlows.length === 0}
              className="w-full py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Processing Vectorized Batch...
                </>
              ) : (
                <>⚡ Evaluate {parsedFlows.length} Flows</>
              )}
            </button>
          </div>

          {/* Results Summary & Table */}
          <div className="lg:col-span-7 space-y-6">
            {error && (
              <div className="rounded-xl border border-rose-300 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 p-5 space-y-2">
                <div className="flex items-center gap-2 text-rose-700 dark:text-rose-400 font-semibold text-sm">
                  <span>🚨 Error</span>
                  {error.code && (
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-200 dark:bg-rose-900 text-rose-800 dark:text-rose-300">
                      [{error.code}]
                    </span>
                  )}
                </div>
                <p className="text-xs text-rose-800 dark:text-rose-300">{error.message}</p>
              </div>
            )}

            {results ? (
              <div className="space-y-6">
                {/* Summary Metrics Grid */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm text-center">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                      Total Analyzed
                    </span>
                    <span className="text-2xl font-bold text-slate-900 dark:text-white mt-1 block">
                      {totalCount}
                    </span>
                  </div>

                  <div className="bg-white dark:bg-slate-900 rounded-xl border border-rose-200 dark:border-rose-900/50 p-4 shadow-sm text-center">
                    <span className="text-[11px] font-semibold text-rose-600 dark:text-rose-400 uppercase tracking-wider block">
                      Attacks Flagged
                    </span>
                    <span className="text-2xl font-bold text-rose-600 dark:text-rose-400 mt-1 block">
                      {attackCount} <span className="text-xs font-normal text-slate-500">({attackPct}%)</span>
                    </span>
                  </div>

                  <div className="bg-white dark:bg-slate-900 rounded-xl border border-emerald-200 dark:border-emerald-900/50 p-4 shadow-sm text-center">
                    <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">
                      Benign Traffic
                    </span>
                    <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1 block">
                      {benignCount}
                    </span>
                  </div>
                </div>

                {/* Attack Category Breakdown */}
                {Object.keys(attackCategoryCounts).length > 0 && (
                  <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                      Attack Family Breakdown
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(attackCategoryCounts).map(([cat, count]) => (
                        <span
                          key={cat}
                          className="px-2.5 py-1 rounded-md text-xs font-medium bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300 border border-rose-300 dark:border-rose-800"
                        >
                          {cat}: <strong className="font-bold">{count}</strong>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Filter & Export Controls */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 font-medium">Filter:</span>
                    <button
                      type="button"
                      onClick={() => setFilter("all")}
                      className={`px-3 py-1 rounded-md text-xs font-semibold transition-colors ${
                        filter === "all"
                          ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900"
                          : "bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      All ({results.length})
                    </button>
                    <button
                      type="button"
                      onClick={() => setFilter("attacks_only")}
                      className={`px-3 py-1 rounded-md text-xs font-semibold transition-colors ${
                        filter === "attacks_only"
                          ? "bg-rose-600 text-white"
                          : "bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      Attacks Only ({attackCount})
                    </button>
                  </div>

                  <button
                    type="button"
                    onClick={handleDownloadCsv}
                    className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs transition-colors flex items-center gap-1.5"
                  >
                    📥 Download CSV Results
                  </button>
                </div>

                {/* Results Table */}
                <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
                  <div className="overflow-x-auto max-h-[480px]">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-semibold sticky top-0 border-b border-slate-200 dark:border-slate-700">
                        <tr>
                          <th className="p-3 w-12 text-center">#</th>
                          <th className="p-3">Protocol</th>
                          <th className="p-3">Service</th>
                          <th className="p-3">Duration</th>
                          <th className="p-3">Src / Dst Bytes</th>
                          <th className="p-3">Classification</th>
                          <th className="p-3 text-right">Confidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono">
                        {filteredResults.map((res, i) => {
                          const origIndex = results.indexOf(res);
                          const f = parsedFlows[origIndex];

                          return (
                            <tr
                              key={origIndex}
                              className={
                                res.is_attack
                                  ? "bg-rose-50/50 dark:bg-rose-950/20 hover:bg-rose-100/50"
                                  : "hover:bg-slate-50 dark:hover:bg-slate-800/50"
                              }
                            >
                              <td className="p-3 text-center text-slate-400">{origIndex + 1}</td>
                              <td className="p-3 uppercase font-sans font-medium">{f?.protocol}</td>
                              <td className="p-3">{f?.service}</td>
                              <td className="p-3">{f?.duration}s</td>
                              <td className="p-3">
                                {f?.src_bytes} / {f?.dst_bytes}
                              </td>
                              <td className="p-3 font-sans">
                                {res.is_attack ? (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300 border border-rose-300 dark:border-rose-800">
                                    ⚠️ {res.label}
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                                    ✅ BENIGN
                                  </span>
                                )}
                              </td>
                              <td className="p-3 text-right font-bold text-slate-800 dark:text-slate-200">
                                {(res.confidence * 100).toFixed(1)}%
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              !error && (
                <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-12 text-center shadow-sm">
                  <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto text-2xl mb-4">
                    📊
                  </div>
                  <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                    Batch Results Output
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto mt-1">
                    Upload or paste CSV flow data on the left to analyze multiple network flows in bulk.
                  </p>
                </div>
              )
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
