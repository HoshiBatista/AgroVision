import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import {
  dashboardWsUrl,
  disconnectRtspStream,
  fetchModelInfo,
  listStreams,
} from "../api/client";
import type { DashboardSnapshot, ModelInfo, StreamMetrics } from "../api/types";
import { ModelInfoCard } from "../components/ModelInfoCard";
import { RtspConnectPanel } from "../components/RtspConnectPanel";
import { StreamTile } from "../components/StreamTile";
import { ThresholdControl } from "../components/ThresholdControl";

interface HistoryPoint {
  time: string;
  total: number;
}

function StatCard(props: { icon: string; label: string; value: string; note: string }) {
  return (
    <div className="panel group relative overflow-hidden p-5 transition duration-300 hover:-translate-y-1 hover:shadow-2xl">
      <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-emerald-100 blur-2xl transition group-hover:bg-lime-200" />
      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-500">{props.label}</p>
          <p className="mt-2 text-4xl font-black tracking-tight text-slate-950">{props.value}</p>
          <p className="mt-2 text-xs text-slate-400">{props.note}</p>
        </div>
        <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-950 text-xl text-white shadow-lg">
          {props.icon}
        </span>
      </div>
    </div>
  );
}

export function Dashboard() {
  const queryClient = useQueryClient();
  const streamsQuery = useQuery({
    queryKey: ["streams"],
    queryFn: listStreams,
    refetchInterval: 3000,
  });
  const modelQuery = useQuery({ queryKey: ["model-info"], queryFn: fetchModelInfo });
  const disconnect = useMutation({
    mutationFn: disconnectRtspStream,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["streams"] }),
  });
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let timer: number | undefined;
    let active = true;
    const connect = () => {
      socket = new WebSocket(dashboardWsUrl());
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data) as DashboardSnapshot;
        setSnapshot(data);
        setHistory((previous) => [
          ...previous.slice(-39),
          { time: new Date().toLocaleTimeString("ru-RU"), total: data.total_sheep },
        ]);
      };
      socket.onclose = () => {
        if (active) timer = window.setTimeout(connect, 1500);
      };
    };
    connect();
    return () => {
      active = false;
      if (timer) window.clearTimeout(timer);
      socket?.close();
    };
  }, []);

  const streams = streamsQuery.data ?? [];
  const metricsById = new Map<string, StreamMetrics>(
    (snapshot?.streams ?? []).map((metric) => [metric.stream_id, metric]),
  );
  const latency = snapshot?.streams.length
    ? snapshot.streams.reduce((sum, metric) => sum + metric.latency_ms, 0) /
      snapshot.streams.length
    : 0;

  return (
    <div className="space-y-8 pb-10">
      <section className="hero-grid relative overflow-hidden rounded-[2rem] bg-slate-950 px-6 py-9 text-white shadow-2xl sm:px-9">
        <div className="absolute -right-20 -top-28 h-80 w-80 rounded-full bg-emerald-500/25 blur-3xl" />
        <div className="relative flex flex-wrap items-end justify-between gap-6">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-bold text-emerald-300">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              Система наблюдения работает
            </div>
            <h1 className="max-w-3xl text-3xl font-black tracking-tight sm:text-5xl">
              Пастбище под контролем <span className="text-lime-300">в реальном времени</span>
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
              Настоящие облёты с дрона, интеллектуальный подсчёт стада и камеры RTSP в
              одном центре управления.
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 backdrop-blur">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Ускоритель</p>
            <p className="mt-1 text-2xl font-black text-emerald-300">
              {modelQuery.data?.device.toUpperCase() ?? "—"}
            </p>
          </div>
        </div>
      </section>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard icon="🐑" label="Овец в кадре" value={String(snapshot?.total_sheep ?? 0)} note="Сумма по активным потокам" />
        <StatCard icon="◉" label="Потоки в эфире" value={`${snapshot?.active_streams ?? 0} / ${streams.length}`} note="Видеозаписи и RTSP-камеры" />
        <StatCard icon="⚡" label="Задержка модели" value={latency ? `${latency.toFixed(0)} мс` : "—"} note="Среднее время одного кадра" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        {modelQuery.data && <ModelInfoCard model={modelQuery.data} />}
        {modelQuery.data && (
          <ThresholdControl
            model={modelQuery.data}
            onUpdated={(model: ModelInfo) => queryClient.setQueryData(["model-info"], model)}
          />
        )}
      </div>

      <RtspConnectPanel onConnected={() => queryClient.invalidateQueries({ queryKey: ["streams"] })} />

      <section className="space-y-4">
        <div className="flex items-end justify-between gap-3">
          <div>
            <p className="eyebrow">Видеонаблюдение</p>
            <h2 className="mt-1 text-2xl font-black text-slate-950">Потоки с детекцией</h2>
          </div>
          <span className="rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-bold text-emerald-700">
            Источников: {streams.length}
          </span>
        </div>
        {streamsQuery.isLoading ? (
          <div className="panel p-10 text-center text-slate-500">Загружаем видеопотоки…</div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-2">
            {streams.map((stream) => (
              <StreamTile
                key={stream.id}
                stream={stream}
                metrics={metricsById.get(stream.id)}
                onDisconnect={stream.kind === "rtsp" ? () => disconnect.mutate(stream.id) : undefined}
              />
            ))}
          </div>
        )}
      </section>

      <section className="panel p-6">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <p className="eyebrow">Аналитика</p>
            <h2 className="mt-1 text-xl font-bold text-slate-950">Динамика поголовья</h2>
          </div>
          <span className="text-xs text-slate-400">Последние 40 измерений</span>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history}>
              <XAxis dataKey="time" tick={{ fontSize: 11 }} minTickGap={35} axisLine={false} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} axisLine={false} />
              <Tooltip labelStyle={{ color: "#0f172a" }} />
              <Line name="Овец" type="monotone" dataKey="total" stroke="#10b981" strokeWidth={4} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
