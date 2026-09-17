import { useQuery } from "@tanstack/react-query";
import { fetchDemoManifest, mediaUrl } from "../api/client";

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-lg font-bold text-slate-800">{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  );
}

export function Examples() {
  const demo = useQuery({ queryKey: ["demo-manifest"], queryFn: fetchDemoManifest });

  if (demo.isLoading) {
    return <div className="glass p-8 text-slate-500">Загрузка готовых примеров…</div>;
  }
  if (demo.isError || !demo.data) {
    return (
      <div className="glass p-8 text-slate-600">
        Демо-результаты ещё не созданы. Выполните <code>make demo-predictions</code>.
      </div>
    );
  }

  const manifest = demo.data;
  return (
    <div className="space-y-10">
      <div>
        <p className="eyebrow">Проверенные материалы</p>
        <h1 className="mt-1 text-3xl font-black text-slate-950">Примеры работы модели</h1>
        <p className="mt-2 text-slate-500">
          Готовый анализ тестовой выборки и всех локальных видео. Модель: {manifest.model.version},
          устройство: {manifest.model.device.toUpperCase()}.
        </p>
      </div>

      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Тестовые изображения</h2>
          <p className="text-sm text-slate-500">
            Кадры выбраны по квантилям плотности: от редкого до самого плотного стада.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {manifest.images.map((item) => (
            <article key={item.url} className="glass overflow-hidden">
              <img src={mediaUrl(item.url)} alt="Овцы с рамками детектора" className="aspect-video w-full object-cover" />
              <div className="grid grid-cols-3 gap-3 p-4 text-center">
                <Metric label="Нашла модель" value={String(item.count)} />
                <Metric label="В разметке" value={String(item.ground_truth_count)} />
                <Metric label="Уверенность" value={`${(item.mean_confidence * 100).toFixed(0)}%`} />
              </div>
              <p className="px-4 pb-4 text-xs text-slate-400">
                {item.uncertain_count} неуверенных · {item.processing_ms.toFixed(0)} мс
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Демонстрационные видео</h2>
          <p className="text-sm text-slate-500">
            Видео заранее обработаны той же лучшей моделью и перекодированы для браузера.
          </p>
        </div>
        <div className="grid gap-6 xl:grid-cols-3">
          {manifest.videos.map((item) => (
            <article key={item.url} className="glass overflow-hidden">
              <video
                src={mediaUrl(item.url)}
                poster={item.poster_url ? mediaUrl(item.poster_url) : undefined}
                controls
                preload="metadata"
                className="aspect-video w-full bg-black object-contain"
              />
              <div className="grid grid-cols-3 gap-3 p-4 text-center">
                <Metric label="Пиковый счёт" value={String(item.max_count)} />
                <Metric label="Средний счёт" value={item.mean_count.toFixed(1)} />
                <Metric label="Кадров" value={String(item.frames_processed)} />
              </div>
              <p className="px-4 pb-4 text-xs text-slate-400">
                {item.name} · пик на {item.peak_timestamp_s.toFixed(1)} с
              </p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
