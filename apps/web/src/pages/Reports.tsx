import { useQuery } from "@tanstack/react-query";
import { exportReport, listSessions } from "../api/client";

const kindLabels: Record<string, string> = {
  image: "Фото",
  video: "Видео",
  stream: "Поток",
};

export function Reports() {
  const sessionsQuery = useQuery({ queryKey: ["sessions"], queryFn: listSessions });
  const sessions = sessionsQuery.data ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="eyebrow">История операций</p>
          <h1 className="mt-1 text-3xl font-black text-slate-950">Журнал анализов</h1>
          <p className="mt-2 text-slate-500">История обработки и экспорт отчётов.</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-ghost" onClick={() => exportReport("csv")}>
            Экспорт CSV
          </button>
          <button className="btn-primary" onClick={() => exportReport("pdf")}>
            Экспорт PDF
          </button>
        </div>
      </div>

      <div className="glass overflow-x-auto">
        {sessionsQuery.isLoading ? (
          <p className="p-6 text-slate-500">Загрузка…</p>
        ) : sessions.length === 0 ? (
          <p className="p-8 text-center text-slate-500">
            Пока нет сессий. Загрузите фото или видео, войдя в аккаунт.
          </p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-sky-100/70 text-slate-600">
              <tr>
                <th className="px-4 py-3">Дата</th>
                <th className="px-4 py-3">Тип</th>
                <th className="px-4 py-3">Источник</th>
                <th className="px-4 py-3 text-right">Овец</th>
                <th className="px-4 py-3">Модель</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr key={session.id} className="border-t border-sky-100">
                  <td className="px-4 py-3 text-slate-500">
                    {new Date(session.created_at).toLocaleString("ru-RU")}
                  </td>
                  <td className="px-4 py-3">{kindLabels[session.kind] ?? session.kind}</td>
                  <td className="px-4 py-3">{session.source_name}</td>
                  <td className="px-4 py-3 text-right font-semibold text-meadow-700">
                    {session.sheep_count}
                  </td>
                  <td className="px-4 py-3 text-slate-400">{session.model_version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
