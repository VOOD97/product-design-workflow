---
name: content-review
description: "Независимо проверяет интерфейсные тексты: терминологию, подписи действий и их последствия, инструкции, валидацию, ошибки, частичные результаты, числа и длинный текст. Применяется, когда нужно оценить понятность и согласованность существующего UX-контента, в том числе динамических сообщений. Триггеры: «content-review», «используй content-review», «понятны ли ошибки и подписи кнопок», «проверь тексты интерфейса», «сверь терминологию», «проверь сообщения об ошибках», UX writing audit, error copy review. Через Playwright вызывает реальные действия и состояния; без интерактивного доступа анализирует доступные тексты, скриншоты и материалы с ограничениями. Использует глоссарий и контракты при наличии. Общая редактура статьи или создание новых текстов не относятся к этому аудиту; скилл возвращает замечания без изменения текста и кода."
---

# Content Reviewer

Выполни независимое ревью в своей области и самостоятельно проверь существенные выводы в браузере через **Playwright**. Проверяй собственные гипотезы о дефектах; принятый продукт не исправляй и не передизайнивай. Скилл работает самостоятельно по текущей задаче или как навык назначенного субагента.

Прочитай `references/artifact-contract.md`: применяй единые правила источников, ID, статусов документа, решения, гейта и отдельных проверок, а также выбора папки, сохранения и полного дублирования результата в чате. Это правила формата, а не зависимость от других навыков.

## Вход и обязательные ресурсы

- Прочитай `references/review-protocol.md` и `references/playwright-review.md`: независимость, tool setup, безопасная изоляция, реальные actions/assertions и supplemental evidence.
- Используй `assets/review-template.md`; профильные справочники читать при подготовке метода: `references/content-inspection.md`.
- Для local Playwright доступны `scripts/browser-review.cjs` и адаптируемый `assets/browser-review.example.cjs`. Готовый project setup/MCP использовать при наличии; прототип и предыдущие артефакты не обязаны быть созданы другим скиллом.
- При orchestration сверить run_id/revision/capture_sha256/read-set. При standalone получить task/URL/контракт из текущего запроса; отсутствие документа само по себе не дефект. Без interactive доступа оценить предоставленное с ограниченным scope и NOT_CHECKED, не имитируя browser прогон.

## 1. Определи язык и контентный контракт

Установи пользователя, задачу, локали, glossary/tone и принятые product/UI decisions. Назови источник каждого нормативного утверждения. Без glossary проверь internal consistency и ясность задачи, не назначая собственный стиль обязательным.

Не читай продуктовый код или author notes; видимый текст/DOM и источники контрактов достаточны для твоей области. Неподдерживаемые языки не превращай в новые requirements.

## 2. Подготовь state/content matrix

Используй `references/content-inspection.md`. Покрой primary и meaningful P0 states: labels/CTA, confirmation, processing, validation, success/error/partial, recovery, empty/long по применимости. Укажи какие строки можно оценить static, а какие должны появиться после действия.

## 3. Сам воспроизведи тексты через Playwright

Пройди safe action: fill/select/click → confirmation/result. Вызови предусмотренные invalid/error/partial fixtures, затем correction/retry. Сравни wording с тем, что система действительно сделала, и сохранностью введённого.

Текст в spec/DOM не доказывает его появление/видимость в нужный момент. Открой screenshot, проверь contextual placement, overflow и возможность получить полный существенный текст.

## 4. Оцени смысл и последовательность

CTA объясняет действие/объект/последствия? Confirmation называет те же сущности и выбранный объём? Loading не выдаётся за success? Error объясняет ограничение и пригодное recovery без false promise? Partial counts/next steps согласованы с test fixture и contract?

Проверь термин в нескольких связанных состояниях. «Другой синоним» без glossary/semantic effect не finding. Сначала неправильное ожидание/действие пользователя, затем редакторская аккуратность.

## 5. Проверь форматы и pressure cases

На synthetic valid datasets проверь 0/1/несколько, большой count, долгие названия, единицы/даты/периоды и заданные локали. На relevant narrow viewport используй scroll/expand и доступную keyboard альтернативу tooltip.

Не придумывай timezone/rounding/plural contract. Если данные/fixture для проверки нет, запиши NOT_CHECKED, а не заявляй выполненную локализацию. Проверка нескольких чисел — targeted coverage, не весь языковой корпус.

## 6. Подтверди существенные content findings

Воспроизведи предполагаемую неверную строку/число при тех же условиях. Отдели bug от stale fixture/другого mode и обоснованного domain term. Expected и actual укажи в browser_checks; для ошибочного обещания проследи реальный outcome, не только название кнопки.

Layer обычно ui; нарушение продуктового правила возможно product/implementation с основанием. Укажи criterion исправности и reproduce steps. Не переписывай copy и не внедряй своё решение. Preserve сохраняет наблюдаемо ясные labels, feedback и термины.

## Перед завершением

Пройди `references/review-ready-checklist.md`, включая live browser checks, профильное покрытие и limits. Сверь Markdown, review-data, actual evidence paths/hashes и отсутствие source edits. Новое evidence сохраняется отдельно от immutable capture. PASS относится к полноте заявленного ревью; полный interaction scope без фактических checks не получает complete.

## Артефакт

Выбери и при необходимости создай `<task-dir>` по `references/artifact-contract.md`. Сохрани основной документ в `<task-dir>/reviews/content.md` при самостоятельном запуске; в оркестрации используй назначенный путь `<task-dir>/reviews/<run-id>/content.md`. После сохранения продублируй полный Markdown в пользовательском чате вместе с кратким выводом и ссылками на файлы; при работе через субагента доставку выполняет основная сессия. При недоступной записи выдай полный текст и явно сообщи, что файл не сохранён.

Сформируй и отправь **один `content.md` в формате Markdown**: scope/revision/read-set, профильное coverage, самостоятельные Playwright checks с expected/actual, What works well, findings или явное отсутствие замечаний в проверенной области, limitations и gate, один review-data.

Findings начинаются с `CNT-`. Собственные scripts/screenshots/traces/logs — attachments в `evidence/content/<attempt>/` рядом с отчётом; включи реальные пути/sha256 в evidence_files и deliver вместе. Не меняй чужие отчёты, canonical inputs, код/тесты и source capture.
