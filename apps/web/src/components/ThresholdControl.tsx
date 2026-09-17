import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { updateModelThreshold } from "../api/client";
import type { ModelInfo } from "../api/types";

export function ThresholdControl({
  model,
  onUpdated,
}: {
  model: ModelInfo;
  onUpdated: (model: ModelInfo) => void;
}) {
  const [value, setValue] = useState(model.confidence_threshold);
  useEffect(() => setValue(model.confidence_threshold), [model.confidence_threshold]);
  const update = useMutation({ mutationFn: updateModelThreshold, onSuccess: onUpdated });
  const percent = Math.round(value * 100);

  return (
    <section className="panel p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="eyebrow">Точность подсчёта</p>
          <h2 className="mt-1 text-xl font-bold text-slate-950">Порог уверенности</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Детекции ниже порога останутся оранжевыми подсказками и не попадут в итоговый счёт.
          </p>
        </div>
        <div className="rounded-2xl bg-emerald-50 px-4 py-2 text-2xl font-black text-emerald-700">
          {percent}%
        </div>
      </div>
      <input
        aria-label="Порог уверенности модели"
        type="range"
        min="25"
        max="95"
        step="1"
        value={percent}
        onChange={(event) => setValue(Number(event.target.value) / 100)}
        className="range-premium mt-6 w-full"
      />
      <div className="mt-2 flex justify-between text-xs font-medium text-slate-400">
        <span>Больше объектов · 25%</span>
        <span>Строже · 95%</span>
      </div>
      <button
        className="btn-primary mt-5 w-full"
        disabled={update.isPending || value === model.confidence_threshold}
        onClick={() => update.mutate(value)}
      >
        {update.isPending ? "Применяем…" : "Применить ко всем потокам"}
      </button>
      {update.isSuccess && <p className="mt-3 text-sm text-emerald-700">Новый порог уже применяется.</p>}
      {update.isError && <p className="mt-3 text-sm text-rose-600">Не удалось изменить порог.</p>}
    </section>
  );
}
