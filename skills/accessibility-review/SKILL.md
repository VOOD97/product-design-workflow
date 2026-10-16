---
name: accessibility-review
description: "Независимо проверяет доступность интерфейса: управление клавиатурой, порядок и видимость фокуса, диалоги, формы, сообщения, адаптацию содержимого и альтернативы указателю. Применяется, когда нужно оценить доступность сценария или проверить возможные барьеры взаимодействия. Триггеры: «accessibility-review», «используй accessibility-review», «можно ли пользоваться формой без мыши», «проверь доступность», «фокус теряется», «проверь Tab и Escape», «есть ли ловушка фокуса», a11y-аудит, keyboard testing, WCAG. Самостоятельно выполняет проверки через Playwright и использует доступные результаты axe. Без интерактивного доступа оценивает предоставленные материалы, включая скриншоты, с явными ограничениями. Упоминание WCAG означает оценку доступных критериев, а не сертификацию; автоматические сканы и DOM-проверки не доказывают полную доступность. Не исправляет продукт."
---

# Accessibility Reviewer

Выполни независимое ревью в своей области и самостоятельно проверь существенные выводы в браузере через **Playwright**. Проверяй собственные гипотезы о дефектах; принятый продукт не исправляй и не передизайнивай. Скилл работает самостоятельно по текущей задаче или как навык назначенного субагента.

Прочитай `references/artifact-contract.md`: применяй единые правила источников, ID, статусов документа, решения, гейта и отдельных проверок, а также выбора папки, сохранения и полного дублирования результата в чате. Это правила формата, а не зависимость от других навыков.

## Вход и обязательные ресурсы

- Прочитай `references/review-protocol.md` и `references/playwright-review.md`: независимость, tool setup, безопасная изоляция, реальные actions/assertions и supplemental evidence.
- Используй `assets/review-template.md`; профильные справочники читать при подготовке метода: `references/manual-accessibility.md`.
- Для local Playwright доступны `scripts/browser-review.cjs` и адаптируемый `assets/browser-review.example.cjs`. Готовый project setup/MCP использовать при наличии; прототип и предыдущие артефакты не обязаны быть созданы другим скиллом.
- При orchestration сверить run_id/revision/capture_sha256/read-set. При standalone получить task/URL/контракт из текущего запроса; отсутствие документа само по себе не дефект. Без interactive доступа оценить предоставленное с ограниченным scope и NOT_CHECKED, не имитируя browser прогон.

## 1. Установи scope доступности

Определи роль/задачу, input modes, платформы, заявленный уровень/контракт, UI states и доступные инструменты. Прочитай ui a11y sections, axe-report/settings/exclusions и keyboard trace, если они есть. Отсутствующие файлы не требуют другого скилла; проверяй доступный прототип самостоятельно.

Различай: automated scan, programmatic DOM/ARIA inspection, actual keyboard interaction, визуальный reflow/scale и реальный assistive-technology прогон. Не суммируй их в выдуманную сертификацию.

## 2. Спланируй ручную матрицу

Обязательно прочитай `references/manual-accessibility.md`. Выбери primary/P0 keyboard route, dialog lifecycle, validation/recovery, dynamic feedback, non-color meaning, relevant reflow и pointer alternatives. Для каждого укажи state/fixture, действие, expected result, evidence и предел метода.

## 3. Сам пройди keyboard task через Playwright

В отдельном context стартуй из известного состояния. Выполни Tab/Shift+Tab и нужные Enter/Space/Escape по семантике controls, пройди primary operation и recovery. Проверяй реальное действие, порядок и видимый focus, а не только activeElement.

Для каждой значимой точки сохрани accessible role/name/state, focused target и screenshot. getByRole/getByLabel помогает проверить programmatic доступ, но его успешность не доказывает понятность, focus visibility или опыт screen reader.

## 4. Проверь focus lifecycle и формы

Open dialog → initial focus → внутри-modal Tab/Shift+Tab → close по контракту → возврат focus. Nested modal и исчезнувший trigger рассмотри по применимости, ожидаемый следующий focus выводи из task contract/паттерна, а не личного предпочтения.

Invalid input → видимая и связанная с полем ошибка → переход к исправлению → успешный outcome. Проверь labels/instructions/required/error relationship и retained data. Не объявляй каждое неинтерактивное сообщение обязательным Tab target.

## 5. Проверь feedback, reflow и alternatives

Сам вызови success/error/partial states и осмотри programmatic feedback. Dynamic announcement вывод по DOM/ARIA — ограниченный; факт слышимости/порядка announcements указывай только после реального AT прогона.

Переключи relevant viewport/reduced motion; проверь доступность content/actions и non-color cues. Настоящий zoom выполняй только поддерживаемым инструментом: narrower viewport или CSS transform не выдавай за 400% browser zoom. Hover/drag task имеет применимую keyboard/button/touch альтернативу; эмуляция не равна физическому device test.

## 6. Используй axe без дублирования

Готовый scan прочитай и проверь существенные findings в actual UI. Повтор того же scan не нужен; отсутствующий/новый state можно целево scan в рамках review. Сохрани scope/version/target и отметь, что добавлено. Нарушение axe не определяет severity автоматически, отсутствие violations не доказывает accessible journey.

## 7. Проверь гипотезы и запиши границы

Подозрение в trap/lost focus/unlabeled form воспроизведи после clean reset; исключи временное processing и неверный locator. Отдельно запиши реально выполненные клавиатурные действия, статически проверенные relations и NOT_CHECKED screen-reader/zoom/device areas.

Finding содержит source principle/contract, observation, affected task, evidence и reproduce steps. Не читать продуктовый код и не исправлять ARIA. What works well относится к фактически пройденным взаимодействиям.

## Перед завершением

Пройди `references/review-ready-checklist.md`, включая live browser checks, профильное покрытие и limits. Сверь Markdown, review-data, actual evidence paths/hashes и отсутствие source edits. Новое evidence сохраняется отдельно от immutable capture. PASS относится к полноте заявленного ревью; полный interaction scope без фактических checks не получает complete.

## Артефакт

Выбери и при необходимости создай `<task-dir>` по `references/artifact-contract.md`. Сохрани основной документ в `<task-dir>/reviews/accessibility.md` при самостоятельном запуске; в оркестрации используй назначенный путь `<task-dir>/reviews/<run-id>/accessibility.md`. После сохранения продублируй полный Markdown в пользовательском чате вместе с кратким выводом и ссылками на файлы; при работе через субагента доставку выполняет основная сессия. При недоступной записи выдай полный текст и явно сообщи, что файл не сохранён.

Сформируй и отправь **один `accessibility.md` в формате Markdown**: scope/revision/read-set, профильное coverage, самостоятельные Playwright checks с expected/actual, What works well, findings или явное отсутствие замечаний в проверенной области, limitations и gate, один review-data.

Findings начинаются с `A11Y-`. Собственные scripts/screenshots/traces/logs — attachments в `evidence/accessibility/<attempt>/` рядом с отчётом; включи реальные пути/sha256 в evidence_files и deliver вместе. Не меняй чужие отчёты, canonical inputs, код/тесты и source capture.
