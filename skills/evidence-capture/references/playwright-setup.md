# Настройка Playwright и среды evidence

Нужны Node.js 20+, Python 3.9+ для проверок оркестрации, проектный package manager, Playwright, Chromium и `@axe-core/playwright`. Playwright API либо MCP-доступ сам по себе не означает наличие browser binaries. Существующую проектную настройку использовать прежде новой.

Пример для npm из каталога проекта:

```bash
npm install -D playwright @axe-core/playwright
npx playwright install chromium
```

Если уже есть `@playwright/test`, он может предоставлять зависимость Playwright; проверить её разрешение из project cwd и реальный запуск Chromium. Для проектных тестов нужен настроенный runner, например `@playwright/test`; не устанавливать второй конфликтующий стек. На Linux могут требоваться системные библиотеки; установка `npx playwright install --with-deps chromium` допустима только в среде, где это разрешено. Зависимости и lockfile меняются в рамках настройки проекта, не в evidence pack.

Перед сбором проверить:

- сервер действительно запущен и обслуживает текущую revision;
- test/mock dataset, seed/reset и переключатели состояния воспроизводимы;
- state-specific selectors наблюдаются в реальном rendered UI;
- функциональные tests имеют meaningful assertions и S/TEST mapping;
- test credentials/storage state управляются отдельно и не входят в ZIP;
- Chromium smoke запускается, файлы можно записать в новую run-папку;
- host поддерживает пять параллельных subagents и сохранение их отчётов; навыки и agents установлены.

Полный сбор одной командой относится к уже подготовленному серверу/fixture/тестам. Сборщик не запускает сервер и не генерирует продуктовые тесты. Аутентифицированный прототип требует project-specific browser-context adaptation; универсальный login не обещается.

Ни `networkidle`, ни фиксированная задержка не являются универсальным условием готовности. Использовать видимый маркер ожидаемого состояния и assertions. Axe scan выполняется в текущем DOM-состоянии, не сертифицирует весь продукт; ручная проверка focus/reader/reflow остаётся отдельной оценкой.

Первичные источники, проверены 2026-10-12:

- [Playwright: installation](https://playwright.dev/docs/intro)
- [Playwright: browsers](https://playwright.dev/docs/browsers)
- [Playwright: accessibility](https://playwright.dev/docs/accessibility-testing)
- [Claude Code: subagents](https://code.claude.com/docs/en/sub-agents)
