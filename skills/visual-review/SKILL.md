---
name: visual-review
description: "Независимо проверяет визуальное качество отрисованного интерфейса: иерархию, типографику, отступы, композицию, компоненты, визуальные состояния и адаптивную компоновку с учётом принятых референсов. Применяется, когда нужно найти визуальные дефекты или несогласованность существующих экранов. Триггеры: «visual-review», «используй visual-review», «проверь отступы и типографику», «оцени визуальную иерархию», «найди визуальные несогласованности», «проверь вёрстку на разных ширинах», visual review, UI consistency audit. Через Playwright получает собственные доказательства; без браузерного доступа анализирует доступные скриншоты и материалы с ограничениями. Соответствие бизнес-правил, сценариев и кода спецификации относится к design-code-parity-review; создание новых экранных решений — к ui-interaction-design. Не меняет дизайн или продукт."
---

# Visual Critic

Выполни независимое ревью в своей области и самостоятельно проверь существенные выводы в браузере через **Playwright**. Проверяй собственные гипотезы о дефектах; принятый продукт не исправляй и не передизайнивай. Скилл работает самостоятельно по текущей задаче или как навык назначенного субагента.

Прочитай `references/artifact-contract.md`: применяй единые правила источников, ID, статусов документа, решения, гейта и отдельных проверок, а также выбора папки, сохранения и полного дублирования результата в чате. Это правила формата, а не зависимость от других навыков.

## Вход и обязательные ресурсы

- Прочитай `references/review-protocol.md` и `references/playwright-review.md`: независимость, tool setup, безопасная изоляция, реальные actions/assertions и supplemental evidence.
- Используй `assets/review-template.md`; профильные справочники читать при подготовке метода: `references/visual-inspection.md`.
- Для local Playwright доступны `scripts/browser-review.cjs` и адаптируемый `assets/browser-review.example.cjs`. Готовый project setup/MCP использовать при наличии; прототип и предыдущие артефакты не обязаны быть созданы другим скиллом.
- При orchestration сверить run_id/revision/capture_sha256/read-set. При standalone получить task/URL/контракт из текущего запроса; отсутствие документа само по себе не дефект. Без interactive доступа оценить предоставленное с ограниченным scope и NOT_CHECKED, не имитируя browser прогон.

## 1. Восстанови визуальные опоры

Определи задачу, принятый UI contract, выбранные макеты/references, DS/components и current revision. Назови точные источники. Последняя картинка не обязательно accepted; author self-check не доказательство соответствия.

Без DS/макета standalone проверяй внутреннюю последовательность, читаемость и доступность существенных действий, обозначив ограничение. Не объявляй свой вкус каноном. Не читать продуктовый код; наблюдение rendered DOM/geometry допустимо для диагностики результата.

## 2. Составь матрицу visual coverage

Для каждого существенного P0 screen×state выбери relevant viewport и fixtures: normal, loading/processing, empty, error, partial, selected/disabled/focus и long/data-rich по применимости. Укажи источник обязательности и план browser probes. State недоступен — NOT_CHECKED, не «отсутствует».

Обязательно используй `references/visual-inspection.md`: hierarchy/grouping → components → typography/spacing/color → adaptive pressure. Не начинать с пикселей, если потерян главный результат.

## 3. Осмотри реальный результат через Playwright

Сам открой страницу, переключи states и viewport, проскроль, открой dialog/dropdown и проверь hover/focus/selected там, где они влияют на visual decision. Screenshot-просмотр обязателен; успешный screenshot command не означает visual inspection.

Сопоставляй условия: данные, viewport, state, scale, theme и browser environment. Осмотри narrow и wide, если они входят в scope; произвольные hard-coded размеры не заменяют принятый responsive contract. Реальная перестройка проверяется при изменении viewport, а не по одному thumbnail.

## 4. Проверь иерархию и компоненты

Опиши, какие существенные данные/CTA видны и как сгруппированы. Проверь связи label/value/action, последовательность status semantics, использование variants и видимость focus/disabled/processing.

При несоответствии DS покажи конкретный принятый источник и реальное отличие; CSS measurement используй лишь если выполнено. Непроверенный цвет/контраст не называй измеренным. Намеренное accepted отличие — не drift.

## 5. Выполни stress probes

На synthetic fixtures проверь длинный контент, много/нет элементов, допустимые extreme values, overlays/sticky regions и узкую ширину. Click/expand/scroll покажет, доступно ли обрезанное существенное значение или перекрытое действие.

Не добавляй новые product states ради количества. Не меняй CSS/layout в DevTools, чтобы показать своё решение. Если fixture отсутствует, запиши ограничение и необходимый способ проверки.

## 6. Подтверди и сохрани findings

Предполагаемую проблему проверь повторно в тех же условиях и сравни с reference. Отдели rasterization/font/environment шум от принятого design violation. Pixel diff сам по себе не пользовательское последствие; не принимать baseline и не обновлять snapshots.

Evidence: pair of states/reference, viewport/fixture, before/after и trace при поведении. Finding должен объяснять эффект: потеря иерархии, нечитабельность, скрытый action или конкретный DS drift. «Некрасиво» без основания остаётся мнением.

What works well сохрани с конкретным состоянием и reference. Не формулируй редизайн вместо критерия исправности.

## Перед завершением

Пройди `references/review-ready-checklist.md`, включая live browser checks, профильное покрытие и limits. Сверь Markdown, review-data, actual evidence paths/hashes и отсутствие source edits. Новое evidence сохраняется отдельно от immutable capture. PASS относится к полноте заявленного ревью; полный interaction scope без фактических checks не получает complete.

## Артефакт

Выбери и при необходимости создай `<task-dir>` по `references/artifact-contract.md`. Сохрани основной документ в `<task-dir>/reviews/visual.md` при самостоятельном запуске; в оркестрации используй назначенный путь `<task-dir>/reviews/<run-id>/visual.md`. После сохранения продублируй полный Markdown в пользовательском чате вместе с кратким выводом и ссылками на файлы; при работе через субагента доставку выполняет основная сессия. При недоступной записи выдай полный текст и явно сообщи, что файл не сохранён.

Сформируй и отправь **один `visual.md` в формате Markdown**: scope/revision/read-set, профильное coverage, самостоятельные Playwright checks с expected/actual, What works well, findings или явное отсутствие замечаний в проверенной области, limitations и gate, один review-data.

Findings начинаются с `VIS-`. Собственные scripts/screenshots/traces/logs — attachments в `evidence/visual/<attempt>/` рядом с отчётом; включи реальные пути/sha256 в evidence_files и deliver вместе. Не меняй чужие отчёты, canonical inputs, код/тесты и source capture.
