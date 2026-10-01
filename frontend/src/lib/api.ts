export interface Features {
  duration: number;
  src_bytes: number;
  dst_bytes: number;
  protocol: string;
  service: string;
}

export interface PredictRequest {
  dataset?: string;
  features: Features;
}

export interface BatchPredictRequest {
  dataset?: string;
  flows: Features[];
}

export interface PredictionResult {
  is_attack: boolean;
  label: string;
  attack_type: string | null;
  confidence: number;
  probabilities: Record<string, number>;
  dataset: string;
  latency_ms: number;
}

export interface HealthResponse {
  status: string;
  loaded_models: string[];
  default_dataset: string;
}

export interface FeaturePropertySchema {
  name: string;
  type: string;
  description: string;
}

export interface DatasetModelDetails {
  dataset: string;
  is_loaded: boolean;
  classes: string[];
  verified: boolean;
}

export interface ModelInfoResponse {
  available_datasets: string[];
  default_dataset: string;
  feature_space: string;
  features_schema: FeaturePropertySchema[];
  datasets_info: Record<string, DatasetModelDetails>;
}

export interface APIErrorResponse {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class APIClientError extends Error {
  code: string;
  details?: unknown;
  statusCode: number;

  constructor(code: string, message: string, statusCode: number, details?: unknown) {
    super(message);
    this.name = "APIClientError";
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL.replace(/\/$/, "")}${path}`;
  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Network error";
    throw new APIClientError("NETWORK_ERROR", `Failed to connect to backend API at ${API_BASE_URL}: ${msg}`, 0);
  }

  if (!response.ok) {
    let errorData: APIErrorResponse | null = null;
    try {
      errorData = await response.json();
    } catch {
      // JSON parsing optional
    }

    if (errorData?.error) {
      throw new APIClientError(
        errorData.error.code || "HTTP_ERROR",
        errorData.error.message || `HTTP Error ${response.status}`,
        response.status,
        errorData.error.details
      );
    }

    throw new APIClientError(
      "HTTP_ERROR",
      `Request failed with HTTP status ${response.status} (${response.statusText})`,
      response.status
    );
  }

  return response.json();
}

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/v1/health", { method: "GET", cache: "no-store" });
}

export async function getModelInfo(): Promise<ModelInfoResponse> {
  return request<ModelInfoResponse>("/api/v1/model/info", { method: "GET", cache: "no-store" });
}

export async function predictSingle(payload: PredictRequest): Promise<PredictionResult> {
  return request<PredictionResult>("/api/v1/predict", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function predictBatch(payload: BatchPredictRequest): Promise<PredictionResult[]> {
  return request<PredictionResult[]>("/api/v1/predict/batch", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
