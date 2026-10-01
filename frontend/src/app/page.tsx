"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import ProbabilityChart from "@/components/ProbabilityChart";
import {
  APIClientError,
  Features,
  getModelInfo,
  ModelInfoResponse,
  predictSingle,
  PredictionResult,
} from "@/lib/api";

const COMMON_SERVICES = ["http", "dns", "ftp", "ssh", "smtp", "telnet", "dhcp", "ntp", "snmp", "-"];

export default function SinglePredictPage() {
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [dataset, setDataset] = useState<string>("unsw_nb15");

  // Form state
  const [duration, setDuration] = useState<string>("0.5");
  const [srcBytes, setSrcBytes] = useState<string>("100");
  const [dstBytes, setDstBytes] = useState<string>("200");
  const [protocol, setProtocol] = useState<string>("tcp");
  const [service, setService] = useState<string>("http");

  // UX state
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<{ code?: string; message: string; details?: unknown } | null>(null);
  const [formValidationErrors, setFormValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const info = await getModelInfo();
        setModelInfo(info);
        if (info.default_dataset) {
          setDataset(info.default_dataset);
        }
      } catch (err: unknown) {
        if (err instanceof APIClientError) {
          setError({ code: err.code, message: err.message, details: err.details });
        } else {
          setError({ message: "Failed to connect to backend server. Make sure the API is running." });
        }
      }
    };
    fetchInfo();
  }, []);

  const validateForm = (): Features | null => {
    const errors: Record<string, string> = {};

    const durVal = parseFloat(duration);
    if (isNaN(durVal) || !isFinite(durVal) || durVal < 0) {
      errors.duration = "Duration must be a valid non-negative number";
    }

    const srcVal = parseInt(srcBytes, 10);
    if (isNaN(srcVal) || srcVal < 0) {
      errors.src_bytes = "Source bytes must be a non-negative integer";
    }

    const dstVal = parseInt(dstBytes, 10);
    if (isNaN(dstVal) || dstVal < 0) {
      errors.dst_bytes = "Destination bytes must be a non-negative integer";
    }

    if (!protocol.trim()) {
      errors.protocol = "Protocol is required";
    }

    if (!service.trim()) {
      errors.service = "Service is required";
    }

    setFormValidationErrors(errors);
    if (Object.keys(errors).length > 0) {
      return null;
    }

    return {
      duration: durVal,
      src_bytes: srcVal,
      dst_bytes: dstVal,
      protocol: protocol.trim().toLowerCase(),
      service: service.trim().toLowerCase(),
    };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    const validatedFeatures = validateForm();
    if (!validatedFeatures) return;

    setLoading(true);
    try {
      const res = await predictSingle({
        dataset,
        features: validatedFeatures,
      });
      setResult(res);
    } catch (err: unknown) {
      if (err instanceof APIClientError) {
        setError({ code: err.code, message: err.message, details: err.details });
      } else {
        setError({ message: "An unexpected error occurred during prediction." });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFillBenignSample = () => {
    setDataset("unsw_nb15");
    setDuration("1.005339");
    setSrcBytes("1580");
    setDstBytes("10168");
    setProtocol("tcp");
    setService("http");
    setFormValidationErrors({});
    setError(null);
  };

  const handleFillAttackSample = () => {
    setDataset("unsw_nb15");
    setDuration("0.258515");
    setSrcBytes("1064");
    setDstBytes("268");
    setProtocol("tcp");
    setService("http");
    setFormValidationErrors({});
    setError(null);
  };

  const isUnverified = modelInfo
    ? modelInfo.datasets_info[dataset]?.verified === false
    : ["cic_ids2017", "cse_cic_ids2018", "uwf_zeekdata24"].includes(dataset);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Header Title */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              Single Network Flow Classifier
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Classify individual network flow features in real-time across canonical dataset models.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleFillBenignSample}
              className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-emerald-300 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 transition-colors"
            >
              🌱 Fill Benign Sample
            </button>
            <button
              type="button"
              onClick={handleFillAttackSample}
              className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-rose-300 dark:border-rose-800 bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 hover:bg-rose-100 dark:hover:bg-rose-900/60 transition-colors"
            >
              ⚠️ Fill Attack Sample
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Input Form Column */}
          <div className="lg:col-span-6 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
            <form onSubmit={handleSubmit} className="space-y-5">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                <span>⚙️</span> Flow Feature Input
              </h2>

              {/* Dataset Selection */}
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
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                  Select dataset model used for feature inference.
                </p>
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

              {/* Flow Duration */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Duration (Seconds)
                </label>
                <input
                  type="number"
                  step="any"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  placeholder="e.g. 0.5"
                  className={`w-full rounded-lg border bg-white dark:bg-slate-800 px-3.5 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    formValidationErrors.duration
                      ? "border-rose-500 focus:ring-rose-500"
                      : "border-slate-300 dark:border-slate-700"
                  }`}
                />
                {formValidationErrors.duration && (
                  <p className="text-xs text-rose-500 mt-1">{formValidationErrors.duration}</p>
                )}
              </div>

              {/* Bytes Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Src Bytes
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={srcBytes}
                    onChange={(e) => setSrcBytes(e.target.value)}
                    placeholder="e.g. 100"
                    className={`w-full rounded-lg border bg-white dark:bg-slate-800 px-3.5 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                      formValidationErrors.src_bytes
                        ? "border-rose-500 focus:ring-rose-500"
                        : "border-slate-300 dark:border-slate-700"
                    }`}
                  />
                  {formValidationErrors.src_bytes && (
                    <p className="text-xs text-rose-500 mt-1">{formValidationErrors.src_bytes}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Dst Bytes
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={dstBytes}
                    onChange={(e) => setDstBytes(e.target.value)}
                    placeholder="e.g. 200"
                    className={`w-full rounded-lg border bg-white dark:bg-slate-800 px-3.5 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                      formValidationErrors.dst_bytes
                        ? "border-rose-500 focus:ring-rose-500"
                        : "border-slate-300 dark:border-slate-700"
                    }`}
                  />
                  {formValidationErrors.dst_bytes && (
                    <p className="text-xs text-rose-500 mt-1">{formValidationErrors.dst_bytes}</p>
                  )}
                </div>
              </div>

              {/* Protocol Selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Protocol
                </label>
                <select
                  value={protocol}
                  onChange={(e) => setProtocol(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="tcp">TCP</option>
                  <option value="udp">UDP</option>
                  <option value="icmp">ICMP</option>
                </select>
              </div>

              {/* Service Input */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Service
                </label>
                <input
                  type="text"
                  value={service}
                  onChange={(e) => setService(e.target.value)}
                  placeholder="e.g. http, dns, ftp, ssh, or '-'"
                  className={`w-full rounded-lg border bg-white dark:bg-slate-800 px-3.5 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    formValidationErrors.service
                      ? "border-rose-500 focus:ring-rose-500"
                      : "border-slate-300 dark:border-slate-700"
                  }`}
                />
                {formValidationErrors.service && (
                  <p className="text-xs text-rose-500 mt-1">{formValidationErrors.service}</p>
                )}

                <div className="flex flex-wrap gap-1.5 mt-2">
                  <span className="text-[11px] text-slate-500 self-center">Suggestions:</span>
                  {COMMON_SERVICES.map((srv) => (
                    <button
                      key={srv}
                      type="button"
                      onClick={() => setService(srv)}
                      className="px-2 py-0.5 text-[11px] font-mono rounded bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950 text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                    >
                      {srv}
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Evaluating Model...
                  </>
                ) : (
                  <>🚀 Classify Flow</>
                )}
              </button>
            </form>
          </div>

          {/* Results Column */}
          <div className="lg:col-span-6 space-y-6">
            {/* Error Banner */}
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
                {Boolean(error.details) && (
                  <pre className="text-[11px] font-mono bg-rose-100 dark:bg-rose-900/50 p-2.5 rounded text-rose-900 dark:text-rose-200 overflow-x-auto">
                    {JSON.stringify(error.details, null, 2)}
                  </pre>
                )}
              </div>
            )}

            {/* Results Card */}
            {result ? (
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-6 animate-fadeIn">
                <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
                  <div>
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                      Classification Output
                    </span>
                    <span className="text-xs font-mono text-slate-600 dark:text-slate-400">
                      Dataset: <strong className="text-slate-900 dark:text-white">{result.dataset}</strong>
                    </span>
                  </div>
                  <span className="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md">
                    ⚡ {result.latency_ms} ms
                  </span>
                </div>

                {/* Primary Prediction Badge */}
                <div className="flex flex-col items-center justify-center py-6 px-4 rounded-xl border border-slate-100 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-800/40 space-y-2">
                  {result.is_attack ? (
                    <>
                      <span className="inline-flex items-center gap-2 px-5 py-2 rounded-full text-base font-bold bg-rose-500 text-white shadow-md animate-pulse">
                        ⚠️ ATTACK DETECTED
                      </span>
                      {result.attack_type && (
                        <span className="text-sm font-semibold text-rose-600 dark:text-rose-400 font-mono">
                          Category: {result.attack_type}
                        </span>
                      )}
                    </>
                  ) : (
                    <span className="inline-flex items-center gap-2 px-5 py-2 rounded-full text-base font-bold bg-emerald-500 text-white shadow-md">
                      ✅ BENIGN TRAFFIC
                    </span>
                  )}

                  <span className="text-xs text-slate-500 dark:text-slate-400 pt-1 font-mono">
                    Model Confidence: <strong className="text-slate-900 dark:text-white">{(result.confidence * 100).toFixed(2)}%</strong>
                  </span>
                </div>

                {/* Probability Distribution */}
                <div className="pt-2">
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
                    Class Probabilities Breakdown
                  </h3>
                  <ProbabilityChart probabilities={result.probabilities} predictedLabel={result.label} />
                </div>
              </div>
            ) : (
              !error && (
                <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-12 text-center shadow-sm">
                  <div className="w-16 h-16 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-500 flex items-center justify-center mx-auto text-2xl mb-4">
                    🔍
                  </div>
                  <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                    Ready for Classification
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto mt-1">
                    Fill in network flow features on the left or click a sample button to evaluate against the trained NIDS model.
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
