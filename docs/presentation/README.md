# Презентация AgroVision

- `AgroVision_pitch_deck.pptx` — редактируемая презентация 16:9, 15 слайдов со
  встроенным H.264-видео лучшего облёта (пик около 1.2 секунды).
- `speaker_notes.md` — готовый сценарий защиты и ответы на вопросы.
- `assets/screenshots/` — реальные скриншоты локального приложения.
- `assets/generated/` — производные изображения, создаваемые генератором.

Пересборка:

```bash
PYTHONPATH=src:. .venv/bin/python -m scripts.build_presentation
```

Скриншоты обновляются отдельной командой. Учётные данные передаются только через
переменные окружения и не сохраняются в скрипте:

```bash
AGROVISION_SCREENSHOT_EMAIL='…' \
AGROVISION_SCREENSHOT_PASSWORD='…' \
PYTHONPATH=src:. .venv/bin/python -m scripts.capture_presentation_screenshots
```

Презентация не содержит значений `.env`, RTSP URI, паролей, JWT или полного API-ключа
Roboflow. Метрики и SHA модели берутся из проверяемых артефактов проекта.
