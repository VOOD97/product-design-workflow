# Контракт сборщика evidence

Это небольшой адаптируемый сборщик, а не готовый набор продуктовых тестов.
`capture-config.example.json` — синтетический пример, не evidence и не основание для Ready.
В проекте нужно самостоятельно настроить сервер, тестовые данные, состояния, селекторы и реальные функциональные тесты.

## Зависимости и запуск

В каталоге проекта должны быть установлены `playwright` и `@axe-core/playwright`, а также Chromium для Playwright.
Пример настройки: `npm install -D playwright @axe-core/playwright`, затем `npx playwright install chromium`.
Используй принятый в проекте package manager и закреплённые версии. Скрипт не устанавливает зависимости и не запускает сервер.
Авторизация, если нужна, требует адаптации контекста браузера под проект; не помещай пароли, токены и реальные клиентские данные в пример конфигурации.

```bash
node skills/evidence-capture/scripts/capture-evidence.cjs --config capture-config.json --project /absolute/project --out evidence/run-001 --dry-run
node skills/evidence-capture/scripts/capture-evidence.cjs --config capture-config.json --project /absolute/project --out evidence/run-001
```

`--dry-run` проверяет конфигурацию без браузера, запуска тестов и создания файлов.
`--out` должен быть новым каталогом; перезапись запрещена. Родительский каталог создаётся при настоящем запуске.
Коды выхода: `0` — сбор выполнен, `2` — сбор заблокирован, `1` — ошибка конфигурации/запуска.
Статус `captured` означает завершение технического сбора, но сам по себе не означает Ready или успешное UX-ревью.

## Конфигурация

| Поле | Смысл |
| --- | --- |
| `task`, `revision` | Идентификаторы задачи и реально обслуживаемой версии. Связь версии с запущенным сервером проверяет оператор. |
| `baseUrl` | HTTP(S) origin без URL credentials, query и fragment. Все цели должны иметь тот же origin. |
| `sourceFiles` | Явно выбранные пути исходников, тестов и канонических документов относительно проекта. Не допускаются выход за каталог и symlink наружу. Хеши до и после сбора обязаны совпадать. Без списка фиксируется ограничение; Ready требует списка и повторного запуска. |
| `testContract` | Project-relative нейтральный test-contract.json, включённый в sourceFiles; обязателен для Ready/planner. До capture выполнить test_contract.py verify. |
| `viewports` | Именованные объекты `width`, `height`. Каждая сторона 240–7680 пикселей. |
| `screens` | Явные цели `{ui_id,state,priority,path OR url,viewport,wait,actions?,keyboard?}`; уникальна комбинация UI/state/viewport. Перечень должен покрывать согласованную матрицу, а не только удобные экраны. |
| `wait` | `{selector,text?}`: видимый маркер ожидаемого состояния перед screenshot. `text`, если указан, сравнивается целиком после trim. Одного существования body недостаточно. |
| `actions` | Последовательность `{type,selector,value?}`. Типы: `click`, `fill`, `press`, `select`. `value` обязателен кроме click. Не использовать реальные секреты. |
| `keyboard` | Реальные клавиши из `Tab`, `Shift+Tab`, `Enter`, `Escape`. По умолчанию все четыре по порядку. Последовательность может изменить состояние; подбери безопасный порядок на синтетических данных. |
| `functional.cases` | Полные e2e cases из нейтрального контракта: scenario/test_id/priority/type/observable_result/mock/ui_ids/test_file. Нужен хотя бы один P0. |
| `functional.command` | Массив executable и argv. Выполняется с `shell:false` в project cwd; stdout обязан быть чистым Playwright JSON reporter output. Timeout 5 минут. Не ставь текст shell-команды в один элемент. |
| `functional.reportFile` | Альтернатива command: существующий JSON reporter относительно проекта. Только анализ: gate остаётся `unavailable`, потому что файл не доказывает актуальность версии. Для Ready нужен свежий runner command. |

Реальный test title должен выглядеть так: `S01 Submit valid form [TEST-001]`.
Исходные совместимые IDs сохраняются, включая S-01 или SCENARIO:checkout; runner сравнивает с явным контрактом. Scenario-ID стоит первым и отделён пробелом; TEST-ID заключён в квадратные скобки. IDs нужны в самом title теста, а не только в describe. Дублированные ID блокируют результат.
Все P0 обязаны пройти во всех объявленных Playwright projects. Failed, missing, skipped, flaky и expected-failure не дают PASS.
Ошибки runner и ненулевой exit code блокируют functional gate даже при отдельных успешных P0.
P1/P2 также отражаются в полном журнале; их неуспех оценивается гейтом и ревью, а не скрывается.

## Результат

`capture-result.json` содержит `schema_version:1`, `task`, `run_id`, `revision`, `config_sha256`, timestamps, `status`,
`expected_targets`, `captures`, `functional`, `source_fingerprints`, `source_fingerprints_after`, `artifacts`, `errors`, `limitations`.
`captures` фиксирует каждый ожидаемый target, в том числе неснятые цели, с `status:'captured'|'failed'`,
`screenshot`, `trace`, `axe_status`, `keyboard_status` и причиной ошибки.
`functional.cases` хранит все ожидаемые кейсы со статусом `passed|failed|skipped|flaky|missing`.
Пути артефактов относительны каталогу run. `artifacts` содержит SHA-256 файлов; сам manifest не хеширует себя.
Нужно проверить manifest и все обязательные файлы; наличие JSON само по себе не доказывает успешный сбор.

Сохраняются screenshots, отдельные `.trace.zip`, `axe-report.json`, `keyboard-trace.md`, `console-log.txt`, `functional-results.json`.
Скан axe с violations считается выполненным сканом: нарушения остаются findings для reviewer.
Keyboard trace содержит фактические нажатия, activeElement, явную/приближённую роль и имя из DOM.
Это приближение accessible name, а не полная реализация Accessible Name Computation; reviewer обязан проверить семантику и клавиатурное поведение.
Console URLs очищаются от query/fragment/credentials, известные поля маскируются, но это не гарантия удаления любых секретов.
Screenshot, trace и DOM-данные axe могут содержать данные: использовать выделенный синтетический dataset.
Без браузера запись честно получает `blocked`, все цели — `failed`; поддельные screenshots или PASS не создаются.
Сборщик не вызывает агентов. Параллельное ревью и синтез запускает оркестратор по инструкциям скилла.
