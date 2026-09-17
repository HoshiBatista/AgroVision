import { useEffect, useState } from "react";
import { mediaUrl, streamMjpegUrl } from "../api/client";
import type { Stream, StreamMetrics } from "../api/types";

interface Props {
  stream: Stream;
  metrics?: StreamMetrics;
  onDisconnect?: () => void;
}

const statusLabels: Record<string, string> = {
  running: "В эфире",
  error: "Ошибка подключения",
  stopped: "Остановлен",
  idle: "Подключение",
};

const filePreviews: Record<string, string> = {
  "drone-close-flight": "/demo-media/posters/12831053_1080_1920_60fps.jpg",
  "drone-wide-flight": "/demo-media/posters/7438342-uhd_4096_1974_30fps.jpg",
};

export function StreamTile({ stream, metrics, onDisconnect }: Props) {
  const [errored, setErrored] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const running = metrics?.status === "running";
  const preview = filePreviews[stream.id];
  useEffect(() => {
    setErrored(false);
    setLoaded(false);
  }, [stream.id]);

  return (
    <article className="group overflow-hidden rounded-[1.75rem] border border-white/70 bg-white shadow-xl shadow-slate-200/60 transition duration-300 hover:-translate-y-1 hover:shadow-2xl">
      <div className="relative aspect-video overflow-hidden bg-slate-950">
        {preview && (
          <img
            src={mediaUrl(preview)}
            alt="Предпросмотр аэросъёмки"
            className="absolute inset-0 h-full w-full object-cover"
          />
        )}
        {errored && !preview ? (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-sm text-slate-300">
            <span className="text-3xl">⌁</span>
            Ожидаем видеосигнал
          </div>
        ) : null}
        {!errored && (
          <img
            src={streamMjpegUrl(stream.id)}
            alt={stream.name}
            className={`absolute inset-0 h-full w-full object-cover transition duration-700 group-hover:scale-[1.02] ${loaded ? "opacity-100" : "opacity-0"}`}
            onLoad={() => setLoaded(true)}
            onError={() => setErrored(true)}
          />
        )}
        <div className="absolute inset-x-0 top-0 flex items-start justify-between bg-gradient-to-b from-black/70 to-transparent p-4 pb-10">
          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-black/40 px-3 py-1.5 text-xs font-bold text-white backdrop-blur-md">
            <span className={`h-2 w-2 rounded-full ${running ? "animate-pulse bg-emerald-400" : metrics?.status === "error" ? "bg-rose-400" : "bg-amber-300"}`} />
            {statusLabels[metrics?.status ?? "idle"] ?? "Подключение"}
          </div>
          <div className="rounded-2xl bg-lime-300 px-3 py-1.5 text-lg font-black text-slate-950 shadow-lg">
            {metrics?.sheep_count ?? 0} <span className="text-xs">овец</span>
          </div>
        </div>
        <div className="absolute bottom-3 left-3 rounded-full bg-black/45 px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-white backdrop-blur">
          {stream.kind === "rtsp" ? "RTSP · камера" : "Дрон · видеозапись"}
        </div>
      </div>
      <div className="flex items-center justify-between gap-4 px-5 py-4">
        <div className="min-w-0">
          <p className="truncate text-base font-bold text-slate-950">{stream.name}</p>
          <p className="mt-1 truncate text-xs text-slate-500">{stream.location}</p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <span className="text-xs font-semibold text-slate-400">
            {metrics ? `${metrics.latency_ms.toFixed(0)} мс` : "—"}
          </span>
          {onDisconnect && (
            <button onClick={onDisconnect} className="rounded-xl bg-rose-50 px-3 py-2 text-xs font-bold text-rose-600 transition hover:bg-rose-100">
              Отключить
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
