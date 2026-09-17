export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  label: string;
  confidence: number;
  confident: boolean;
  box: BoundingBox;
}

export interface ModelInfo {
  name: string;
  version: string;
  weights_path: string;
  weights_sha256: string;
  device: string;
  image_size: number;
  confidence_threshold: number;
  classes: string[];
  limitations: string[];
}

export interface ImagePrediction {
  request_id: string;
  model_version: string;
  confidence_threshold: number;
  width: number;
  height: number;
  count: number;
  uncertain_count: number;
  mean_confidence: number;
  processing_ms: number;
  detections: Detection[];
  annotated_image: string;
}

export interface CountSample {
  timestamp_s: number;
  frame_index: number;
  count: number;
}

export interface VideoPrediction {
  request_id: string;
  model_version: string;
  frames_processed: number;
  max_count: number;
  mean_count: number;
  peak_timestamp_s: number;
  processing_ms: number;
  annotated_video_url: string;
  samples: CountSample[];
  keyframes: string[];
}

export interface Stream {
  id: string;
  name: string;
  location: string;
  kind: string;
}

export interface ConnectRtspStream {
  name: string;
  location: string;
  uri: string;
}

export interface StreamMetrics {
  stream_id: string;
  status: string;
  sheep_count: number;
  mean_confidence: number;
  latency_ms: number;
  frame_index: number;
}

export interface DashboardSnapshot {
  total_sheep: number;
  active_streams: number;
  streams: StreamMetrics[];
}

export interface SessionRecord {
  id: number;
  kind: string;
  source_name: string;
  sheep_count: number;
  mean_confidence: number;
  model_version: string;
  created_at: string;
}

export interface AuthUser {
  id: number;
  email: string;
  role: string;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface DemoImage {
  name: string;
  url: string;
  ground_truth_count: number;
  count: number;
  uncertain_count: number;
  mean_confidence: number;
  processing_ms: number;
}

export interface DemoVideo {
  name: string;
  url: string;
  poster_url: string | null;
  frames_processed: number;
  max_count: number;
  mean_count: number;
  peak_timestamp_s: number;
  processing_ms: number;
}

export interface DemoManifest {
  generated_at: string;
  model: {
    name: string;
    version: string;
    device: string;
    weights_sha256: string;
  };
  images: DemoImage[];
  videos: DemoVideo[];
}
