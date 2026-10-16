# Самостоятельная проверка через Playwright

## Содержание

1. Что проверять самостоятельно
2. Подготовка и изоляция
3. Цикл проверки гипотезы
4. Локальный Playwright или MCP
5. Собственное evidence и ограничения

## 1. Что проверять самостоятельно

Полученное evidence — отправная точка. Если работающий прототип доступен, проверь действия, от которых зависит вывод в твоей области: нажатия, ввод, переходы, feedback, ошибки, focus, viewport. Не ограничивайся screenshots для утверждений о поведении. Проверяй собственную гипотезу о проблеме, а не подтверждай её любой ценой.

Пользователь разрешил самостоятельное «тыкание» локального/тестового прототипа в рамках review: повторного разрешения на каждое обычное тестовое действие не нужно. Не меняй продукт, принятые правила, код, tests, DS или immutable исходное evidence. Тестовые данные можно изменять через разрешённый интерфейс fixtures и сбрасывать в своей изолированной области.

Когда только статические материалы: полноценная визуальная оценка возможна в их границах, но interaction/focus/recovery остаются NOT_CHECKED. Не объявляй их отсутствующими или исправными. Если Playwright недоступен, сначала проверь существующую настройку и разрешённый fallback; сохрани доступную работу с явным ограничением.

## 2. Подготовка и изоляция

Перед browser review установи реальный URL, revision и связь сервера с read-set, тестовую роль, fixtures/reset, viewport, допустимые действия и свой output directory. Предоставленные файлы могут быть optional; задача и наблюдаемый контракт должны быть понятны.

У каждого reviewer — отдельный BrowserContext, cookies/localStorage и каталог `reviews/<run-id>/evidence/<role>/<attempt>/`. **Изоляция BrowserContext не изолирует общую базу/API.** Для параллельных меняющих данные действий нужны независимые fixture namespaces/тестовые записи или mock per context. Если сервер поддерживает только общий изменяемый dataset, обозначь conflict и ограничь проверку безопасными действиями, пока main coordinator не предоставит изоляцию. Не сбрасывай данные других reviewers.

Существующий Playwright setup использовать прежде новой установки. Для local JS: Node.js 20+, проектный `playwright` или разрешимый из проекта `@playwright/test`, совместимые Chromium binaries; `@axe-core/playwright` нужен только для дополнительного scan. Python Playwright и Playwright MCP тоже допустимы, если доступны фактические tools и отдельная session/page. MCP не является условием локального запуска.

Пример настройки npm в project cwd: `npm install -D playwright`, `npx playwright install chromium`. Применить штатный manager и lockfile проекта; не запускать глобальные обновления ради reviewer. Non-Parity reviewer может получить от координатора готовый browser setup; чтение package/test-runtime metadata для запуска разрешено, продуктовая логика/код остаются вне его read-set.

Не копируй auth state, пароли, tokens в report/ZIP. Trace и screenshots тоже могут содержать данные; используй выделенные синтетические записи. Авторизация управляется проектной тестовой настройкой, не универсальным login сценария.

## 3. Цикл проверки гипотезы

Для каждого существенного предполагаемого нарушения:

1. Запиши ожидаемое поведение и основание (контракт/эвристика/DS/задача), конкретный UI×state и неизвестные условия.
2. Открой чистый fixture, дождись маркера исходного состояния; проверь locator и реальный доступ к действию. Timeout по неверному selector не является дефектом продукта.
3. Выполни нормальные пользовательские действия через Playwright: click/fill/selectOption/press, navigation, viewport и scroll. Используй role/name/label; test-id допустим для диагностики, но не доказывает обнаружимость.
4. Проверь наблюдаемый результат assertions и собственной визуальной оценкой: state/content/count/navigation/focus/data preservation. Наличие элемента или HTTP 200 не заменяет результат задачи.
5. Сохрани before/after и trace/журнал шагов. Screenshot **открой и посмотри** доступным image/browser инструментом; получение файла не означает его просмотра.
6. При неожиданном исходе проверь контекст, fixtures, ограничения и повтори целевую проверку после собственного reset. Воспроизводится — подтверждённое наблюдение; не воспроизводится — intermittent/inconclusive с частотой/условиями, а не выдуманный PASS.
7. Найди объяснение, которое могло бы опровергнуть гипотезу: выбранный режим, role, viewport, валидное условие контракта. Намеренное согласованное отличие не является drift.
8. Запиши finding только при достаточном evidence; иначе — вопрос/ограничение. Severity относится к влиянию, не к реакции Playwright или уверенности reviewer.

Не использовать `force:true`, DOM injection и ручное выполнение внутренних handlers для доказательства нормальной доступности действия. Диагностические обходы маркировать отдельно. Web-first assertions и конкретное состояние предпочтительнее fixed sleeps/универсального networkidle.

## 4. Локальный Playwright или MCP

Для local runner используй `scripts/browser-review.cjs` и адаптируемый пример `assets/browser-review.example.cjs`. Helper открывает отдельный context и пишет только reviewer-owned evidence; он не знает продуктовых критериев. Reviewer составляет короткий проверочный script с осмысленными действиями/assertions. Новый script — инструмент проверки, не изменение продуктового кода.

Для MCP сначала обнаружь доступные Playwright tools и их аргументы; не выдумывай tool names. Вызовы navigation/click/fill/keyboard/screenshots должны относиться к твоей session. Если MCP делит одну изменяемую page между workers и не даёт изоляции, использовать отдельные local contexts или назвать limitation; параллельное управление одной page запрещено.

Не создавай тест всего продукта. Проверяй основной scope своей роли и целевые неясные/рисковые места. Повторять весь functional suite или тот же axe scan пяти reviewer не нужно. Независимая проверка конкретного важного поведения допустима, даже если общий functional прогон зелёный.

## 5. Собственное evidence и ограничения

Supplemental evidence хранится рядом с отчётом в выделенной папке; исходный capture не перезаписывается. Укажи run/revision, роль/context, fixture, viewport, ожидаемое/actual, реальные шаги, результат и пути. Для simulated response через page.route укажи, что это искусственно заданное состояние: не приписывай такой ответ настоящему API.

В review-data добавь:

- `browser_checks`: id, UI/scenario, expected, actual, method (`playwright`/`provided_evidence`/`static`), result (`passed`/`failed`/`not_checked`/`inconclusive`), evidence, reason/limits;
- `evidence_files`: path относительно report directory, sha256, kind и связанные check/finding IDs;
- `heuristic_coverage` у UX: N1–N10, состояние/flow, статус, checks/evidence или причина N/A/NOT_CHECKED.

Helper result `probe_failed` означает неуспех действия/assertion, а не автоматически дефект продукта. Reviewer проверяет причину и переводит её в соответствующий result. `recorded`/exit code не являются качеством review. Отсутствие trace, browser или нужного доступа отражается в limits; interaction claims без interaction evidence не получают complete/PASS.

Источники: [Playwright best practices](https://playwright.dev/docs/best-practices), [actionability](https://playwright.dev/docs/actionability), [accessibility testing](https://playwright.dev/docs/accessibility-testing). Сверены 2026-10-13; role-specific probes ниже — методика этого пакета.
