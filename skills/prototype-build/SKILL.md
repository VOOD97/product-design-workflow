---
name: prototype-build
description: "Собирает работающий локальный браузерный прототип по принятым или явно делегированным продуктовым и UI-решениям: маршруты, экраны, состояния и действия с воспроизводимыми тестовыми данными, содержательными тестами и отчётом prototype-build.md. Применяется, когда согласованный интерфейс или сценарий нужно превратить в интерактивное поведение в коде. Триггеры: «prototype-build», «используй prototype-build», «собери кликабельный прототип», «реализуй прототип интерфейса», «сделай рабочий сценарий по этим экранам», «преврати UI-спецификацию в прототип», interactive mockup, browser prototype. Работает по брифу или имеющимся материалам. Выбор экранных решений и дизайн-стенд относятся к ui-interaction-design. Не переопределяет утверждённое поведение молча и не развёртывает изменения в production."
---

# Prototype Build

Прочитай `references/artifact-contract.md`: применяй единые правила источников, ID, статусов документа, решения, гейта и отдельных проверок, а также выбора папки, сохранения и полного дублирования результата в чате. Это правила формата, а не зависимость от других навыков.

## Назначение и границы

Создай работоспособный локальный browser experience в согласованном prototype scope: маршруты, screens × states, переходы, interactions и детерминированные данные. Проверяй результат тестами и браузером. Не превращай прототип в production feature автоматически, не делай deployment/production writes и не запускай других скиллов или review-субагентов.

Самостоятельный вызов допустим. Обязательны только понятная задача, доступное окружение и подтверждённое существенное поведение. При наличии используй `requirements.md`, `solution.md`, `flow.md`, `ui-spec.md`, Design Stand, `DESIGN.md`, `design-components.md`, макеты, контракты и текущий codebase. Документы не являются обязательной цепочкой входов; не требуй вызова других скиллов.

Если задача задана только словами, зафиксируй минимальный локальный контракт в `prototype-build.md`, сохранив источник и статус. Незначительные implementation details решай самостоятельно. При существенном неизвестном продуктового/UI-решения задай конкретный вопрос и реализуй независимые части; спорную часть оставь `draft`, не называй её принятым поведением.

Если доступен `solution.md`, используй его раздел «Сценарии» вместе с правилами и состояниями, сохраняя ID. Отдельный файл сценариев не ожидается. Другие предоставленные документы допустимы как внешние источники: проверь версию, полномочность и область; конфликт с текущим контрактом зафиксируй, не разрешай по одному имени файла. При отсутствии документов восстанови только нужный текущей задаче контракт внутри основного результата.

## Как читать пакет

- Начни с `assets/prototype-build-template.md`: один документ содержит matrix, neutral test contract и build-notes.
- До настройки браузера прочитай `references/tooling-and-run.md`.
- Для mocks и сценарных тестов прочитай `references/deterministic-testing.md`.
- Перед выдачей прочитай `references/prototype-ready-checklist.md`.

## 1. Установи scope и техническую опору

Прочитай действующие инструкции репозитория, доступные scripts/config, lockfile, relevant routes/components/tests и DS. Используй стек, package manager и test runner проекта. Не меняй зависимости/архитектуру всего приложения ради отдельного прототипа; не создавай соседний стек без необходимости.

Сверь product/UI contracts и реализации: accepted decision не переоткрывается; proposed decision не становится approved из-за того, что его легко реализовать. При конфликте источников запиши конкретное расхождение и affected scope. Не считай screenshot достаточной спецификацией поведения, прав или бизнес-правил.

При доступной DS переиспользуй tokens/components/variants и responsive patterns. Пробел обозначь явно и предложи минимальную реализацию в рамках подтверждённого решения. Без DS standalone-прототип может использовать локальный provisional слой с ограниченной областью действия; не объявляй его каноном существующего продукта.

Зафиксируй маршруты, роли, P0-сценарии, P0 screen × state и viewports. Сохрани исходные REQ/S/FLOW/UI-ID. Если ID отсутствуют, создай устойчивые task-local ID и source mapping внутри документа. Не выдумывай внешние сценарии ради полноты.

## 2. Построй test matrix до экранов

Из accepted criteria и сценариев сформируй embedded таблицу в `prototype-build.md`: scenario ID, priority, TEST-ID, e2e/unit, observable result, fixture, UI-ID, test file. Каждый P0-сценарий должен иметь минимум один **содержательный функциональный тест**. Для пользовательского primary flow нужен browser e2e; unit assertions внутренних функций не заменяют прохождение пути.

Включи применимые critical branches: invalid input, error/retry, cancellation, permissions, partial outcome, back navigation. Тест должен проверять результат, а не только render, HTTP 200, existence locator или отсутствие exception. Не подгоняй expected result под уже написанный код.

Если пользователь предоставил отдельную внешнюю матрицу тестов, импортируй актуальные обязательства с происхождением/ID и разбором конфликтов. Основная матрица находится внутри prototype-build.md; отдельный обязательный Markdown для неё не создавай.

Добавь в `prototype-build.md` **один** fenced-блок `prototype-test-contract` с JSON по asset-шаблону. Это нейтральный machine-readable контракт наблюдаемых условий: cases, screens, viewports, version/revision. Он предназначен для извлечения без авторских build-notes. В нём не должно быть self-assessed PASS, намерений автора, оправданий deviations или выводов «всё работает».

Все P0 UI-ID должны быть описаны в `screens` и иметь достижимый route/fixture. Каждый P0 scenario присутствует в `cases`; проверяй ссылки UI-ID и viewport names. `mock` — устойчивое имя fixtures, `test_file` — фактически существующий test path. Для новой конвенции используй `S01`, `UI-001`, `TEST-001`; title теста — `S01 — observable result [TEST-001]`. Существующие совместимые ID сохраняй: runner сопоставляет явные scenario/test_id с title. Для несовместимого синтаксиса используй проверяемую таблицу alias → source ID, без молчаливой перенумерации. Имена тестов содержат S-ID и TEST-ID; экран/state root получает `data-ui="UI-ID"` либо документированный эквивалент, не заменяющий accessible semantics.

## 3. Создай scaffold

До экранов установи shell/router, shared layout, token layer, component integration, локальный mock/data contract, reset/seed mechanism и browser test infrastructure. Сначала переиспользуй существующий фундамент. Изолируй dev-only fixtures и controls от production routes и реальных операций.

Для Playwright требуется совместимый runtime (обычно Node.js), пакет/test runner, browser binaries и доступная среда запуска. Подробности в `references/tooling-and-run.md`. Установка Browser/MCP для функциональных тестов не обязательна: локальный Playwright runner достаточен. axe подключай отдельно только для нужных automated scans; scan не является сертификацией доступности.

Не используй живые платежи, production writes или реальные персональные данные. Рабочие URL бери из проверенной конфигурации/запущенного сервера, а не произвольного localhost example. Удерживай тесты на local/test targets и mocks; реальные интеграции допускаются только в явно согласованном безопасном scope.

## 4. Реализуй screens и поведение

Реализуй routing, states, actions, validation, navigation, async feedback, responsive layout и keyboard/focus behavior по принятому контракту. Сохрани существующую visual language и выбранные состояния. Не заменяй summary с partial outcome одним toast или предусмотренный сценарий другим удобным вариантом.

При техническом препятствии различай:

- implementation detail — реши внутри согласованного behavior;
- наблюдаемое UI/product изменение — зафиксируй proposed deviation и спроси о материальном выборе;
- недоступный источник/tool — зафиксируй ограничение, без выдуманного дефекта.

Пример минимального допустимого решения — локальный state store вместо backend, если backend вне scope и пользовательское поведение сохраняется. Это simulation, а не подтверждение server security, persistence или integration readiness.

## 5. Обеспечь deterministic mocks

Сделай воспроизводимыми normal/empty/long/large/extreme/mixed/error/partial fixtures по применимости. Каждый P0 state доступен через фиксированную query, dev panel или test seed; terminal state должен также достигаться через соответствующий пользовательский путь, если это часть сценария. Прямая загрузка success-состояния не заменяет проверку submit → result.

Контролируй clock, IDs, randomness, latency и response ordering, если они влияют на тест. Reset fixtures на каждый тест; изоляция browser context, storage и mock server исключает зависимость от порядка запусков. Не используй unseeded random data и blanket sleeps. Жди ожидаемый DOM/URL/response web-first assertions; `networkidle` не универсальное подтверждение готовности приложения.

Для UI error/retry mock возвращает ошибку на определённый запрос и success на повтор только по договорённому сценарию. Для partial response фиксируй список успешных/неуспешных элементов и assert retry только failed IDs. Отдельно проверяй client validation до запроса и user-visible feedback.

## 6. Запусти проверки и проверь браузером

Запусти существующие applicable lint, typecheck, build, token-lint, unit и Playwright smoke/сценарные tests. Если команда отсутствует или не относится к стеку, объясни N/A; для P0-functional e2e отсутствие runner не является N/A и не даёт Prototype Ready PASS. При отсутствии token-lint можно провести targeted проверку changed UI на forbidden local token values по правилам проекта; опиши фактический объём, не объявляй несуществующий script выполненным.

Проверь primary journey, P0 states, relevant viewports, long content, error recovery, focus/dialog keyboard и console/page errors. Фильтруй known external diagnostic только с конкретным объяснением; не глуши общий канал ошибок. Приложение, работающее только при выключенных проверках, не считается готовым.

Чини ошибки своей реализации, не меняя asserted contract. После значимой правки повтори affected tests и primary smoke; не скрывай failures retries-only результатом. Оставь regression-причину и итог в документе. Если среда не позволяет запустить браузер, сохрани код/тесты, укажи `NOT_CHECKED` и точный missing prerequisite.

## 7. Запиши фактический результат

Обнови neutral JSON и человеческую matrix с одной ревизией кода и реальными путями. Укажи commit/hash, если доступен, плюс timestamp/state identifier для uncommitted изменений. В build-notes запиши команды, выполненные checks, mock controls, known limits, deviations и open questions.

Раздел build-notes содержит позицию автора и **не является независимым review evidence**. Для независимой проверки может извлекаться только `prototype-test-contract` в нейтральный `test-contract.json`, alongside исходные contracts, tests и наблюдаемые screenshots/logs. Нельзя использовать author's PASS для заключения reviewer.

Не создавай `review.md` и не запускай ревью здесь. В ответе различай technical checks, визуальный self-check и независимую приёмку. Прототип может быть технически working и при этом draft из-за неподтверждённого material decision.

## Перед завершением

Пройди `references/prototype-ready-checklist.md`. Запиши для каждого пункта `PASS / FAIL / NOT_CHECKED / N/A`, evidence path/command и причину N/A в `prototype-build.md`. Итог PASS требует выполненных P0-functional tests и реально работоспособного прототипа; failures не превращай в ограничения, отсутствие проверки не выдавай за failure или PASS. При существенном unresolved contract оставь decision_status proposed/unknown и gate FAIL; документ выдай как partial. Сохрани готовые независимые части даже при частичном результате.

## Артефакт

Выбери и при необходимости создай `<task-dir>` по `references/artifact-contract.md`. Сохрани основной документ в `<task-dir>/prototype-build.md`. После сохранения продублируй полный Markdown в пользовательском чате вместе с кратким выводом и ссылками на файлы; при работе через субагента доставку выполняет основная сессия. При недоступной записи выдай полный текст и явно сообщи, что файл не сохранён.

Выдай **код работающего локального прототипа и тесты**, а также **один Markdown-документ `prototype-build.md`** по `assets/prototype-build-template.md`: scope/источники, embedded test matrix, neutral JSON test contract, commands/build-notes, deviations, actual checks и gate. Отдельные аналитические `test-matrix.md` / `build-notes.md` по умолчанию не создавай. Дай реальный entry/source path и запуск, назови технический статус и непроверенное; не объявляй production/deployment readiness или независимую приёмку.
