---
name: design-code-parity-review
description: "Проверяет соответствие реализации принятым продуктовым и UI-решениям: сопоставляет согласованные правила, сценарии и состояния с кодом, наблюдаемым поведением и содержательными тестами. Применяется, когда ожидаемое решение задано в спецификации, макете, контракте или текущем запросе и его нужно сверить с реализацией. Триггеры: «design-code-parity-review», «используй design-code-parity-review», «проверь соответствие реализации спецификации», «все ли согласованные сценарии реализованы», «найди расхождения между требованиями и поведением», design-code parity, specification drift. Самостоятельно выполняет Playwright-проверки и целевые существующие тесты; без интерактивного доступа проверяет доступные материалы и отмечает непроверенное. Читает код только для сверки с контрактом. Чисто визуальный аудит относится к visual-review; общий code review, QA без согласованного эталона, перепроектирование и исправления сюда не входят."
---

# Design ↔ Code Parity Reviewer

Выполни независимое ревью в своей области и самостоятельно проверь существенные выводы в браузере через **Playwright**. Проверяй собственные гипотезы о дефектах; принятый продукт не исправляй и не передизайнивай. Скилл работает самостоятельно по текущей задаче или как навык назначенного субагента.

Прочитай `references/artifact-contract.md`: применяй единые правила источников, ID, статусов документа, решения, гейта и отдельных проверок, а также выбора папки, сохранения и полного дублирования результата в чате. Это правила формата, а не зависимость от других навыков.

## Вход и обязательные ресурсы

- Прочитай `references/review-protocol.md` и `references/playwright-review.md`: независимость, tool setup, безопасная изоляция, реальные actions/assertions и supplemental evidence.
- Используй `assets/review-template.md`; профильные справочники читать при подготовке метода: `references/parity-inspection.md`.
- Для local Playwright доступны `scripts/browser-review.cjs` и адаптируемый `assets/browser-review.example.cjs`. Готовый project setup/MCP использовать при наличии; прототип и предыдущие артефакты не обязаны быть созданы другим скиллом.
- При orchestration сверить run_id/revision/capture_sha256/read-set. При standalone получить task/URL/контракт из текущего запроса; отсутствие документа само по себе не дефект. Без interactive доступа оценить предоставленное с ограниченным scope и NOT_CHECKED, не имитируя browser прогон.

## 1. Установи контракт, revision и цепочку

Сопоставь TASK/REQ → RULE/STATE/S → FLOW/UI → selected implementation → rendered behavior → TEST. Доступные documents optional: отсутствие непредусмотренного слоя не дефект, прямую связь с TASK сохрани. Статусы принятых решений и proposed отличай.

Проверь source/evidence hashes и связь текущего сервера с revision. Author build-notes и self-assessed PASS не читай; neutral matrix/assertions и фактические результаты допустимы. Смешение revision блокирует подтверждение parity.

## 2. Составь матрицу обязательств

Прочитай `references/parity-inspection.md`. Для каждого P0 запиши принятое поведение, UI representation, кодовой path, TEST/assertion, actual result, свой browser check и deviation/limits. Существующее имя теста не засчитывай как meaningful coverage.

## 3. Прочитай релевантную реализацию и тесты

Читай только назначенные files/связанные участки для подтверждения поведения, условий и трассировки. Не оценивай architecture/style/naming, backend качество и абстрактную «чистоту».

Для теста проверь реальные действия/assertions, fixtures, scope и фактический reporter. Mount/existence/HTTP 200 не доказывают результат задачи; direct terminal state не заменяет submit → outcome. Expected failure/skip/flaky не становятся PASS обязательного контракта.

## 4. Независимо пройди UI через Playwright

Сам воспроизведи обязательный primary path и существенные branch/recovery hypotheses: actual action → expected visible outcome. Проверь принятое partial summary/retry, guards/roles, навигацию и UI states по scope.

Сопоставь код и **реально отрисованное** состояние. Наличие handler/guard не доказывает UI/permissions/persistence. Request trace использовать только для наблюдаемого request; невидимый backend эффект не придумывать.

## 5. При необходимости запусти targeted existing tests

Если результат неоднозначен или существенная assertion могла быть подменена, выполни целевой существующий test command в изолированной среде и сохрани фактический report/log у себя. Без source edits и без замены assertions для green.

До tests с reset/data mutation убедись в независимости от fixtures других reviewers; generic suite нельзя запускать так, чтобы оно уничтожало их state. Невозможность запускать test не доказывает failure продукта, но ограничивает утверждение о test coverage.

## 6. Исследуй deviations и scope

Проверь отсутствующие принятые actions/states, неверные branches/recovery, несогласованную замену content/layout и незапланированные product additions. Helper/mock plumbing не feature само по себе.

Принятое исключение требует конкретного source/владельца, не оправдания исполнителя. Расхождение между хорошим test result и нарушенным observable contract может быть test gap плюс product deviation; разные первопричины не сливай автоматически.

## 7. Подтверди findings

Повтори targeted probe после clean fixture и сверки revision. Укажи, какие выводы подтверждены code+browser+test, какие только одним слоем, и что NOT_CHECKED. Preserve фиксирует реально сохранённые принятые решения и meaningful tests.

Не чини код/тесты, не проектируй новую механику и не запускай fixes/baseline. Итог — соответствие конкретному контракту с evidence, а не инженерная приёмка всего репозитория.

## Перед завершением

Пройди `references/review-ready-checklist.md`, включая live browser checks, профильное покрытие и limits. Сверь Markdown, review-data, actual evidence paths/hashes и отсутствие source edits. Новое evidence сохраняется отдельно от immutable capture. PASS относится к полноте заявленного ревью; полный interaction scope без фактических checks не получает complete.

## Артефакт

Выбери и при необходимости создай `<task-dir>` по `references/artifact-contract.md`. Сохрани основной документ в `<task-dir>/reviews/parity.md` при самостоятельном запуске; в оркестрации используй назначенный путь `<task-dir>/reviews/<run-id>/parity.md`. После сохранения продублируй полный Markdown в пользовательском чате вместе с кратким выводом и ссылками на файлы; при работе через субагента доставку выполняет основная сессия. При недоступной записи выдай полный текст и явно сообщи, что файл не сохранён.

Сформируй и отправь **один `parity.md` в формате Markdown**: scope/revision/read-set, профильное coverage, самостоятельные Playwright checks с expected/actual, What works well, findings или явное отсутствие замечаний в проверенной области, limitations и gate, один review-data.

Findings начинаются с `PAR-`. Собственные scripts/screenshots/traces/logs — attachments в `evidence/parity/<attempt>/` рядом с отчётом; включи реальные пути/sha256 в evidence_files и deliver вместе. Не меняй чужие отчёты, canonical inputs, код/тесты и source capture.
