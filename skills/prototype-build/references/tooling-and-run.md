# Настройка и запуск прототипа

## Сначала обнаружение, затем установка

1. Прочитай repo instructions, package manifests, lockfile и existing test config. Определи реальный runtime/package manager: npm/pnpm/yarn/bun либо другой стек проекта. Используй его, не заводи второй lockfile.
2. Найди scripts запуска/build/tests, реальный port/host и состояние server. Если running server принадлежит другой задаче, не останавливай его и не изменяй конфигурацию.
3. Для нового JS/TS browser prototype нужен совместимый Node.js/toolchain выбранной версии, test package `@playwright/test` и установленные browser binaries. Установка требует network и иногда OS dependencies; не объявляй её успешной без запуска browser.

## Playwright

В existing project сначала используй installed version/config. Если runner отсутствует и установка в scope, добавь dev dependency штатной командой package manager и минимальную config. Затем установи нужный browser штатным Playwright CLI. Примеры **только для npm-проекта**, адаптируй к обнаруженному manager:

```bash
npm install -D @playwright/test
npx playwright install chromium
npx playwright test
```

Не вызывай install-all-browsers по умолчанию. Firefox/WebKit нужны только при declared platform scope. Команда `install --with-deps` может требовать системные privileges; если недоступна, запиши точный blocker и используй уже доступный supported browser/runtime, если он проверяет нужный scope.

Предпочти Playwright `webServer` в config для lifecycle локального сервера. В config запиши реальную command и URL после проверки. Не приписывай одному port universal default. В shared runtime проверяй принадлежность сервера, если используешь `reuseExistingServer`.

Existing Python Playwright/test infrastructure допустима; не требуй Node только ради переноса. Для Python нужны соответствующие package, browser binaries и test runner проекта. Если есть внешний helper, сначала прочитай доступную usage/`--help` и используй только фактически присутствующий скрипт. Не ссылайся на пути из чужого reference zip как на установленный helper.

MCP для локальных functional tests не обязателен. Browser interactive tool полезен для self-check, но не заменяет сохранённые воспроизводимые тесты. axe (`@axe-core/playwright` в JS-проекте) — дополнительный automated accessibility check; full accessibility verdict требует manual keyboard/focus/interaction assessment.

## Изоляция и воспроизводимость

- `baseURL` берётся из config/explicit test target. Fixtures/mock responses не направляют запись в production.
- Use isolated contexts, deterministic seed/clock where relevant, reset state per test.
- Env secrets не печатай; пример credentials использует synthetic test account. Реальные login integration допускай только по scope и доступным тестовым данным.
- Оставь documented startup, test, reset and mock switch commands. Если команду не выполнял, отметь «не выполнено».

## Что записать в build-notes

Runtime/browser/test runner версии, package manager, tested code revision, команды и actual result, configured baseURL, fixture names/reset, viewports, known limitations и воспроизводимая failure причина. Build-notes — авторский журнал; он не должен попадать в read-set independent reviewers.

## Первичные инструкции

[Playwright installation](https://playwright.dev/docs/intro), [browser binaries/system dependencies](https://playwright.dev/docs/browsers), [accessibility scans и ограничения](https://playwright.dev/docs/accessibility-testing). Сверены 2026-10-12; команды адаптировать к фактически обнаруженному стеку.
