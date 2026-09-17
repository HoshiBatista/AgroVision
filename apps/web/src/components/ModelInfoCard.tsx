import type { ModelInfo } from "../api/types";

const classNames: Record<string, string> = { sheep: "Овцы" };

export function ModelInfoCard({ model }: { model: ModelInfo }) {
  return (
    <section className="panel relative overflow-hidden p-6" aria-labelledby="model-info-title">
      <div className="absolute -bottom-20 -right-16 h-56 w-56 rounded-full bg-sky-100 blur-3xl" />
      <div className="relative">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="eyebrow">Активная нейросеть</p>
            <h2 id="model-info-title" className="mt-2 text-xl font-black text-slate-950">{model.name}</h2>
            <p className="mt-1 font-mono text-xs text-slate-400">{model.version}</p>
          </div>
          <span className="rounded-2xl bg-slate-950 px-4 py-2 text-xs font-black uppercase tracking-wider text-emerald-300">{model.device}</span>
        </div>
        <dl className="mt-6 grid grid-cols-3 gap-3 text-sm">
          <div className="rounded-2xl bg-slate-50 p-3">
            <dt className="text-xs text-slate-400">Объекты</dt>
            <dd className="mt-1 font-bold text-slate-800">{model.classes.map((item) => classNames[item] ?? item).join(", ")}</dd>
          </div>
          <div className="rounded-2xl bg-slate-50 p-3">
            <dt className="text-xs text-slate-400">Размер кадра</dt>
            <dd className="mt-1 font-bold text-slate-800">{model.image_size} пикс.</dd>
          </div>
          <div className="rounded-2xl bg-slate-50 p-3">
            <dt className="text-xs text-slate-400">Порог</dt>
            <dd className="mt-1 font-bold text-emerald-700">{(model.confidence_threshold * 100).toFixed(0)}%</dd>
          </div>
        </dl>
        <details className="mt-4 text-xs text-slate-400">
          <summary className="cursor-pointer font-semibold text-slate-500">Техническая информация</summary>
          <p className="mt-2 break-all font-mono">SHA-256: {model.weights_sha256}</p>
          {model.limitations.map((limitation) => <p className="mt-2" key={limitation}>{limitation}</p>)}
        </details>
      </div>
    </section>
  );
}
