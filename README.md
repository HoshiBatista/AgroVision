# AgroVision — детекция и подсчёт овец с дронов

End-to-end продукт для агро-хакатона: детекция и подсчёт овец на аэрофото и видео
с дронов на базе **YOLO26n**. Один и тот же application use-case обслуживает
версионированный API и веб-интерфейс.

Возможности:

- 🖼️ загрузка **фото** → аннотированный результат и счётчик овец;
- 🎬 загрузка **видео** → покадровый инференс, временной ряд поголовья, ключевые кадры;
- 🛰️ два локальных **дрон-облёта** и подключаемые RTSP-камеры с MJPEG-плитками;
- 📊 дашборд по WebSocket: поголовье, активные потоки, задержка модели;
- 🎚️ изменение порога уверенного подсчёта сразу для всех источников;
- 🔐 регистрация/вход (**JWT**, SQLite/PostgreSQL) и журнал сессий с экспортом **CSV/PDF**;
- 🧪 готовая галерея результатов на 6 тестовых кадрах и всех локальных видео;
- 🌤️ красивый лендинг с анимацией облаков и овечек.

Продуктовое решение зафиксировано в
[docs/adr/0002-product-scope.md](docs/adr/0002-product-scope.md); ML-baseline —
в [docs/adr/0001-aerial-sheep-baseline.md](docs/adr/0001-aerial-sheep-baseline.md).

## Архитектура

Модульный монолит с гексагональными слоями (зависимости направлены внутрь):

```text
apps/api/            # FastAPI: роуты, DI, обработка ошибок (тонкие)
apps/web/            # React (Vite + TS + Tailwind) SPA
src/agrovision/
  domain/            # сущности и value-objects, без фреймворков
  application/       # use-cases и порты (Protocols)
  infrastructure/    # YOLO, SQLAlchemy, стриминг, безопасность, хранилище
  presentation/      # Pydantic-схемы и presenters
ml/                  # data / training / evaluation
configs/  scripts/  alembic/
```

Ключевое: модель грузится **один раз** на старте; веб и API вызывают один
use-case; источник потока абстрагирован (`StreamSourcePort`), поэтому файл-симуляцию
можно заменить на реальный RTSP без изменения домена.

## Стек

Python 3.12 · FastAPI · Pydantic v2 · SQLAlchemy async · SQLite/PostgreSQL · Alembic ·
Argon2 · PyJWT · Ultralytics YOLO · OpenCV · ReportLab · React 18 · Vite ·
TailwindCSS · Framer Motion · Recharts. Управление — `uv` и `npm`.

## Быстрый старт

Требуются только `uv`, `npm` и локальный файл выбранной модели.

```bash
# Первый запуск: зависимости, безопасный .env, SQLite, пользователь и примеры
make local-init

# API и веб-интерфейс одной командой
make local
```

Откройте http://localhost:5173 — лендинг, затем вход демо-аккаунтом.

Локальная база хранится в `artifacts/agrovision.db`; отдельный сервер базы не нужен.
Демо-пользователь: `operator@farm.com` / `sheep12345`.

API использует выбранный `best.pt` эпохи 10 и до загрузки проверяет его SHA-256 по
`configs/model_yolo26n_aerial_sheep_v1.toml`. Автоматический переход на обычный
COCO-checkpoint запрещён: отсутствие или подмена весов завершает запуск понятной
ошибкой. На Apple Silicon `MODEL_DEVICE=auto` выбирает MPS; локальный `.env` можно
явно настроить командой `uv run python -m scripts.configure_local_env --device mps`.
Основной дашборд показывает два исходных видео с дрона из корня проекта. RTSP-камеру
можно подключить прямо в русскоязычном интерфейсе; адрес не возвращается клиенту и
не попадает в список потоков. Сервер автоматически пытается восстановить соединение.

## Команды

| Команда | Назначение |
|---|---|
| `make local-init` / `make local` | полная подготовка / совместный запуск API и UI |
| `make configure` | безопасный `.env`: MPS и локальная SQLite без вывода секретов |
| `make setup` / `make web-setup` | зависимости Python / фронтенда |
| `make db-up` / `make db-down` | PostgreSQL в Docker |
| `make migrate` / `make seed` | миграции / демо-пользователь |
| `make prepare` / `make demo-data` | датасет / демо-видео потоков |
| `make demo-predictions` | MPS-инференс 6 изображений и всех локальных видео для галереи |
| `make train` / `make evaluate` | обучение / отчёт по метрикам |
| `make lint` / `make typecheck` / `make test` | ruff / mypy / pytest |
| `make api` / `make web` | dev-серверы API / фронтенда |
| `make docker-build` / `make docker-up` | сборка / запуск полного Docker-стека |

## Docker

При наличии локального `best.pt` полный стек запускается одной командой:

```bash
make configure
make docker-up
```

Веб-интерфейс будет доступен на http://localhost:8080, API — на
http://localhost:8000. Контейнер API использует CPU, поскольку Apple MPS недоступен
в Linux-контейнере. PostgreSQL и uploads хранятся в именованных volumes, а выбранные
веса и демо-видео подключаются read-only с хоста.

## API

`GET /health` · `GET /ready` · `GET /v1/model-info` ·
`POST /v1/predictions` (фото) · `POST /v1/predictions/video` ·
`POST /v1/auth/{register,login,refresh}` · `GET /v1/auth/me` ·
`GET/POST /v1/streams` · `DELETE /v1/streams/{id}` ·
`GET /v1/streams/{id}/mjpeg` · `PATCH /v1/model-threshold` ·
`GET /v1/dashboard` · `WS /v1/dashboard/ws` ·
`GET /v1/reports/sessions` · `GET /v1/reports/export.{csv,pdf}`.

Все ответы несут request-id (заголовок `X-Request-ID`), стабильные тела ошибок,
версию модели и время обработки. `/v1/model-info` также возвращает SHA-256, устройство,
порог и ограничения модели. Аплоады ограничены по типу, размеру и числу пикселей.

Синхронный PyTorch-инференс выполняется вне asyncio event loop. Все вызовы из API и
симулируемых потоков проходят через одну ограниченную очередь, поэтому один экземпляр
модели не используется конкурентно несколькими потоками.

## Оффлайн-демо

После `make local-init` весь happy-path работает без Docker: модель, веса, SQLite и
демо-материалы локальны, фронтенд собирается статикой
(`cd apps/web && npm run build`).

## Ограничения

- Подсчёт — **визуальная оценка**; перекрытия, плотность стада и высота съёмки дают
  пропуски/двойной счёт. UI показывает версию модели и помечает неуверенные детекции.
- Baseline-сплит содержит утечку соседних кадров DJI-видео (см. ADR 0001), поэтому
  метрики оптимистичны до пересборки сплита по исходному видео/полёту. Это
  ограничение отражено в `/v1/model-info` и отчёте `make evaluate`.

Инструкции для координирующих агентов — в [AGENTS.md](AGENTS.md).
