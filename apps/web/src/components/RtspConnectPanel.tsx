import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { connectRtspStream } from "../api/client";

export function RtspConnectPanel({ onConnected }: { onConnected: () => void }) {
  const [name, setName] = useState("Камера фермы");
  const [location, setLocation] = useState("Основное пастбище");
  const [uri, setUri] = useState("");
  const connection = useMutation({
    mutationFn: connectRtspStream,
    onSuccess: () => {
      setUri("");
      onConnected();
    },
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    connection.mutate({ name, location, uri });
  }

  return (
    <section className="panel-dark relative overflow-hidden p-6">
      <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-emerald-400/20 blur-3xl" />
      <div className="relative">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10 text-xl">◉</span>
          <div>
            <p className="eyebrow text-emerald-300">Прямое подключение</p>
            <h2 className="text-xl font-bold text-white">Добавить RTSP-камеру</h2>
          </div>
        </div>
        <p className="mt-3 max-w-xl text-sm leading-6 text-slate-300">
          Подключите дрон, IP-камеру или видеорегистратор. Адрес и учётные данные не
          отображаются в интерфейсе после подключения.
        </p>

        <form onSubmit={submit} className="mt-5 grid gap-3 sm:grid-cols-2">
          <label className="space-y-1.5">
            <span className="text-xs font-semibold text-slate-300">Название камеры</span>
            <input className="field-dark" value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label className="space-y-1.5">
            <span className="text-xs font-semibold text-slate-300">Расположение</span>
            <input
              className="field-dark"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              required
            />
          </label>
          <label className="space-y-1.5 sm:col-span-2">
            <span className="text-xs font-semibold text-slate-300">Адрес RTSP-потока</span>
            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                type="url"
                className="field-dark flex-1 font-mono text-sm"
                value={uri}
                onChange={(e) => setUri(e.target.value)}
                placeholder="rtsp://пользователь:пароль@192.168.1.20:554/stream"
                required
              />
              <button className="btn-lime min-w-44" disabled={connection.isPending}>
                {connection.isPending ? "Подключаем…" : "Подключить поток"}
              </button>
            </div>
          </label>
        </form>
        {connection.isSuccess && (
          <p className="mt-3 text-sm font-medium text-emerald-300">Поток добавлен в мониторинг.</p>
        )}
        {connection.isError && (
          <p className="mt-3 text-sm font-medium text-rose-300">
            Не удалось подключить поток. Проверьте RTSP-адрес и доступность камеры.
          </p>
        )}
      </div>
    </section>
  );
}
