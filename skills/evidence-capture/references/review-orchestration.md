# Параллельное ревью: диспетчеризация, барьер и синтез

## Содержание

1. Формат и границы автоматизации
2. Подготовка нейтральных входов
3. Fan-out пяти reviewers
4. Барьер и синтез
5. Отказы, ограничения и доставка

## 1. Формат и границы автоматизации

Пакет agents/*.md рассчитан на Claude Code: `skills:` предварительно загружает соответствующий навык. Skills должны быть доступны по имени в `.claude/skills/<name>/`, agents — в `.claude/agents/`. Проверить реальное обнаружение и загрузку; файл YAML сам по себе не запускает worker.

Выполнением управляет основной агент, выполняющий evidence-capture. Python-планировщик создаёт проверенный launch plan, но не обращается к LLM и не запускает модели. Основной агент обязан выполнить fan-out и barrier средствами host subagents. Это автоматическое продолжение текущего вызова, а не фоновый cron, hook или самостоятельный daemon.

Пять agents имеют тонкую роль; методы находятся в пяти прикреплённых review skills. Синтез выполняет основной агент через отдельный review-synthesis, без шестой оболочки. `model: inherit` сохраняет выбор основной сессии. Tools наследуются для поддержки динамических browser/MCP средств. Read-set и запрет изменений — инструкции роли, не техническая файловая песочница; реальные permissions ограничивает host. Не использовать bypassPermissions и не выдавать недоступный запуск за завершённый.

В Codex/Cursor процедуру skills можно переносить, но именно Claude-style `agents/*.md` и поле skills нельзя считать универсальной конфигурацией. Нужна адаптация native agent definitions текущего клиента и механизм параллельной диспетчеризации. При их отсутствии сохранить evidence и честно сообщить blocked orchestration.

## 2. Подготовка нейтральных входов

Создай `review-inputs.json` — mapping только явно выбранных project-relative files: brief, requirements, solution, flow, ui, design, components, glossary, visual_references, tests, code, external_sources. Значение — путь или массив путей. Отсутствующий optional документ можно опустить; хотя бы один brief/requirements/solution/ui обязателен для определения задачи.

Не включать авторские build-notes, prototype-build.md целиком, IMPLEMENTATION_REPORT, прежние reviewers или чат автора. Используй нейтральный test-contract.json по references/test-contract-handoff.md: это извлечённый без изменения схемы prototype-test-contract либо самостоятельно подготовленный наблюдаемый контракт. Capture-config — отдельная техническая производная. Полные поля cases сохраняются, targets разворачиваются на UI×state×viewport; selectors/waits/actions задаются по реальному интерфейсу. Planner проверяет revision, полное соответствие cases/screens/viewports и source hash нейтрального файла, затем копирует его исходные bytes в read-set UX/Parity. Не восстанавливай контракт из сокращённой capture-конфигурации. External_sources — только явно выбранные внешние нормативные материалы, без author notes; отдельный документ сценариев не ожидается.

В sourceFiles перед capture должны быть все передаваемые документы/код/тесты. Перед планом source hashes сверяются ещё раз; только label revision не доказывает актуальность. Относительные пути evidence проверяются внутри capture-directory, symlink наружу запрещён.

```bash
python3 <skill-dir>/scripts/prepare_review.py \
  --capture <task-dir>/evidence/<run-id>/capture-result.json \
  --config <task-dir>/capture-config.json --project <project-dir> \
  --inputs <task-dir>/review-inputs.json \
  --out <task-dir>/reviews/<run-id>/review-run.json
```

Config checksum соответствует семантическому JSON.stringify исходного конфига, не форматированию его файла. Planner создаёт immutable copies выбранных inputs и нейтральный test-contract; не меняет продукт. Exit 0 означает plan ready; 1 — gate blocked; 2 — invalid input/IO. Уже существующий plan/snapshot не перезаписывать, новый capture требует нового run-id.

Read-set:

| Worker | Источники | Evidence | Не читает |
|---|---|---|---|
| UX | TASK/requirements/solution/flow/ui, нейтральная matrix | screenshots, traces, actual functional results, console | код, author notes, чужие reviews |
| Visual | TASK/ui/DS/components/выбранные references | screenshots | код, author notes, чужие reviews |
| Accessibility | TASK/ui a11y | axe, keyboard, screenshots/traces | код, author notes, чужие reviews |
| Content | TASK/ui copy/glossary | screenshots | код, author notes, чужие reviews |
| Parity | все выбранные canonical inputs, matrix, relevant code/tests | весь относящийся evidence | author notes, чужие reviews |

Работающий прототип передаётся каждому reviewer для самостоятельной Playwright-проверки существенных выводов своей роли. Plan содержит browser URL/project/revision/targets/viewports и отдельный evidence_dir; координатор добавляет доступ/fixtures/reset и независимый backend namespace. Worker получает собственный context; запись новых evidence только в свой каталог, не в immutable capture. Main coordinator передаёт supplemental evidence синтезатору с paths/hashes/provenance. Не отдавать всем один изменяемый page/session. Изолировать backend dataset также обязательно: разные contexts не предотвращают гонку в общей базе; без отдельного fixture namespace ограничить изменяющие данные probes и отметить неполноту, не уничтожать чужой state.

## 3. Fan-out пяти reviewers

При plan ready основной агент:

1. Прочитать plan и вручную подтвердить Evidence Ready, включая просмотр screenshot и правильность scope; planner не проверяет смысл картинки.
2. Одной параллельной диспетчеризацией создать пять custom workers по `agent` из plan. В Claude Code использовать доступный Agent-инструмент; в другом host — его native механизм. Не ждать первого завершения перед отправкой остальных. Снять launch times и task IDs; сравнение времени относится к диспетчеризации, не гарантирует одинаковую скорость моделей.
3. Передать каждому только prompt задачи + run_id/revision/capture_sha256 + его read_set + единственный output + безопасный URL, Playwright context/fixtures и свой evidence directory. Шаблон: «Используй свой предзагруженный навык, независимо проверь <task> по этим входам. Сохрани отчёт <output>. Исходные файлы/evidence не изменяй. Верни путь, полный Markdown отчёта, краткий вывод, complete/partial/blocked и limitations».
4. Обновить в review-run status reviewing, а у workers running с реальными host task IDs/started_at. Не записывать completed на основании существования старого файла.
5. Дождаться terminal результата каждого. Для completed проверить сохранение назначенного файла; failed/cancelled тоже terminal, но не успешное ревью. Записать реальный статус и завершение в plan. Не подставлять invented IDs/timestamps.

Ограничение одновременных workers/permissions обнаруживается до fan-out. Если пяти слотов нет, явно blocked parallel orchestration: не имитировать параллельное ревью последовательными вызовами. Позже можно продолжить по отдельной доступной возможности/согласованному scope, сохранив статус ограничения.

## 4. Барьер и синтез

После всех terminal workers:

```bash
python3 <skill-dir>/scripts/verify_reports.py --plan <task-dir>/reviews/<run-id>/review-run.json
```

Проверяются происхождение, неизменность snapshot/capture, пять ролей, terminal statuses и основные поля review-data. Проверка структуры не подтверждает истинность evidence/source или смысл дубликатов. Такие проверки выполняет синтезатор.

При успешном barrier автоматически загрузить скилл `review-synthesis` и выполнить его в основной сессии: plan, пять отчётов, capture manifest/источники, output synthesis.md. Сохранить результат. Записать synthesis running/completed/failed и окончательный статус; только после завершения выдать весь пакет.

Если barrier не прошёл из-за terminal failed/missing reviewer, всё равно после всех terminal workers выполнить скилл синтеза в основной сессии для честного неполного отчёта. Передать errors барьера; Reviews Ready = FAIL/ограниченный scope, не полноценный PASS. Если один worker ещё running, ожидание продолжается; нельзя объявить barrier завершённым по timeout. Невозможность ожидания — явный незавершённый процесс.

## 5. Отказы, ограничения и доставка

- P0 failed/skipped/flaky/missing или неправильный screenshot: reviewers не запускать. Вернуть evidence и причины; этот навык не чинит прототип.
- Недоступны host subagents/навыки/permissions: evidence выдаётся с blocked orchestration; пять ролей не имитировать в одной сессии.
- Worker failed: сохранить partial/missing, синтезировать неполноту после всех terminal results. Не удалять неуспешный запуск.
- Скилл синтеза failed: выдать реальные reports и условие завершения, не выдуманный synthesis.
- Изменились исходники/evidence: этот run stale; требуется новый capture. Старый PASS нельзя приклеить к новой revision.
- После synthesis не выполнять fixes, baseline approval, commit/deploy. Готовность ревью и готовность продукта различаются.
- Финальная выдача: manifest + raw evidence + пять reviews + synthesis в одном ZIP или доступной папке с корректными относительными ссылками. Основная сессия читает сохранённые отчёты и полностью дублирует `manifest.md`, каждый фактически полученный review и `synthesis.md` в пользовательском чате вместе с общим выводом и ссылками. Ответы workers и ссылка на ZIP не заменяют эту доставку. При ограничении длины используй последовательные части и явно обозначь недоставленное; отсутствующие отчёты не выдумывай. Соблюдай правила сохранения и доставки из `artifact-contract.md`. Не включать storageState/secrets или личные данные.

Первичный источник: [Claude Code subagents](https://code.claude.com/docs/en/sub-agents), проверено 2026-10-12. Указанная пользователем статья ZeroCoder не открылась через доступный reader (с параметром и без него); её содержание не объявляется изученным. Точный `skills:` и host semantics сверены по первичной документации.
