import { useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { mediaUrl, predictImage, predictVideo } from "../api/client";
import type { ImagePrediction, VideoPrediction } from "../api/types";

function FilePicker({
  label,
  accept,
  onPick,
  busy,
}: {
  label: string;
  accept: string;
  onPick: (file: File) => void;
  busy: boolean;
}) {
  return (
    <label className="group flex cursor-pointer flex-col items-center justify-center gap-2 rounded-3xl border-2 border-dashed border-emerald-300 bg-gradient-to-br from-white to-emerald-50/70 px-6 py-12 text-center shadow-lg shadow-emerald-100/40 transition hover:-translate-y-1 hover:border-emerald-500 hover:shadow-xl">
      <span className="text-4xl">{accept.includes("video") ? "🎬" : "🖼️"}</span>
      <span className="font-semibold text-slate-700">{label}</span>
      <span className="text-xs text-slate-400">{busy ? "Обработка…" : "Нажмите, чтобы выбрать файл"}</span>
      <input
        type="file"
        accept={accept}
        className="hidden"
        disabled={busy}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onPick(file);
          e.target.value = "";
        }}
      />
    </label>
  );
}

export function Upload() {
  const [image, setImage] = useState<ImagePrediction | null>(null);
  const [video, setVideo] = useState<VideoPrediction | null>(null);
  const [imageBusy, setImageBusy] = useState(false);
  const [videoBusy, setVideoBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onImage(file: File) {
    setImageBusy(true);
    setError(null);
    try {
      setImage(await predictImage(file));
    } catch {
      setError("Не удалось обработать изображение");
    } finally {
      setImageBusy(false);
    }
  }

  async function onVideo(file: File) {
    setVideoBusy(true);
    setError(null);
    try {
      setVideo(await predictVideo(file));
    } catch {
      setError("Не удалось обработать видео");
    } finally {
      setVideoBusy(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <p className="eyebrow">Разовый анализ</p>
        <h1 className="mt-1 text-3xl font-black text-slate-950">Загрузка фото и видео</h1>
        <p className="mt-2 text-slate-500">Модель разметит кадр и посчитает овец.</p>
      </div>

      {error && <div className="glass p-4 text-sm font-medium text-red-500">{error}</div>}

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="space-y-4">
          <FilePicker label="Фото с дрона" accept="image/*" onPick={onImage} busy={imageBusy} />
          {image && (
            <div className="glass overflow-hidden">
              <img src={image.annotated_image} alt="Результат" className="w-full" />
              <div className="grid grid-cols-3 gap-2 p-4 text-center">
                <Metric label="Овец" value={String(image.count)} />
                <Metric label="Неуверенных" value={String(image.uncertain_count)} />
                <Metric label="Время" value={`${image.processing_ms.toFixed(0)} мс`} />
              </div>
              <p className="px-4 pb-4 text-xs text-slate-400">Модель: {image.model_version}</p>
            </div>
          )}
        </section>

        <section className="space-y-4">
          <FilePicker label="Видео с дрона" accept="video/*" onPick={onVideo} busy={videoBusy} />
          {video && (
            <div className="glass overflow-hidden">
              <video src={mediaUrl(video.annotated_video_url)} controls className="w-full bg-black" />
              <div className="grid grid-cols-3 gap-2 p-4 text-center">
                <Metric label="Пик овец" value={String(video.max_count)} />
                <Metric label="Кадров" value={String(video.frames_processed)} />
                <Metric label="Пик, с" value={video.peak_timestamp_s.toFixed(1)} />
              </div>
              {video.samples.length > 0 && (
                <div className="h-40 px-2 pb-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={video.samples}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis
                        dataKey="timestamp_s"
                        tick={{ fontSize: 10 }}
                        tickFormatter={(v: number) => `${v.toFixed(0)} с`}
                      />
                      <YAxis allowDecimals={false} tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="count"
                        stroke="#16a34a"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
              {video.keyframes.length > 0 && (
                <div className="flex gap-2 overflow-x-auto px-4 pb-4">
                  {video.keyframes.map((frame, index) => (
                    <img key={index} src={frame} alt="" className="h-20 rounded-lg" />
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-sky-50 py-3">
      <p className="text-lg font-bold text-slate-800">{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  );
}
