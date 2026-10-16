# Ручная доступность с Playwright

## Граница метода

Playwright воспроизводит клавиши, фокус, pointer и DOM/ARIA состояния. Axe выявляет часть автоматических нарушений. Ни один из них не доказывает реальный screen-reader опыт и соответствие всему WCAG. Целевой уровень/платформы берутся из task contract, а не из предположения reviewer.

Сначала прочитай готовый axe scan, его версию, scope/states/exclusions и keyboard trace. Не повторяй тот же scan в той же конфигурации без причины. При отсутствии scan или новом существенном состоянии можно выполнить целевой axe scan самостоятельно в scope review, без отдельного согласования обычной проверки; запиши, что именно добавлено.

## Матрица ручных probes

| Область | Самостоятельная проверка | Наблюдаемое доказательство | Ограничение |
|---|---|---|---|
| Keyboard route | Tab/Shift+Tab по primary task, Enter/Space на подходящих controls, Escape по контракту | Последовательность действий/focus и результат операции | Поведение одного клавишного пути не охватывает все controls |
| Focus order/visibility | Контролировать реально focused element, логический порядок и visible indicator; scroll into view | Active element + screenshot после шага | activeElement не доказывает видимость и смысл порядка |
| Dialog lifecycle | Open → initial focus → движение внутри modal → close → return focus; вложенный dialog если scope | Focus/role/name, screenshots и trace | Не требовать конкретную кнопку initial focus без учёта задачи/опасности |
| Формы | Labels, instructions, required/state, errors и доступность recovery клавиатурой | getByRole/getByLabel, aria state/relationship и реальная correction | Accessible locator успех не означает понятность человеку |
| Dynamic feedback | Success/error/partial messages имеют пригодный announced context | DOM/ARIA changes и sequence после действия | Слышимость/порядок announcements требует реального AT прогона |
| Не только цвет | Selected/error/status имеют текст/иконку/semantic state и различимы | Screenshot + наблюдаемый state | Contrast не выводить из названия токена |
| Reflow/scale | Narrow width по scope, overflow/content/action; настоящий browser zoom если доступен | Viewport/zoom setting, screenshot, reachable actions | Узкий viewport не выдавать за настоящий 400% browser zoom |
| Pointer/touch alternatives | Keyboard/button alternative для hover/drag-only task; touch mode при declared platform | Реально выполненный альтернативный путь | Эмуляция touch не доказывает весь опыт физического устройства |
| Motion/time | Reduced motion setting, таймеры/таймауты и сохранность context по scope | Условия настройки и before/after | Не добавлять неподтверждённые compliance thresholds |

## Порядок действий

1. Определи role/task/scope и controls primary path; не запускай случайный Tab loop без цели.
2. Используй новый context/test fixture. Запиши фактический keyboard path, accessible role/name/state и observed result.
3. Проверяй и programmatic relationships, и видимый результат: label/error association, modal state, focus visibility/return.
4. Подозрение воспроизведи повторно с reset. Отличай focus trap от временной загрузки, ошибочный selector — от отсутствующего accessible name.
5. Для ограничения screen reader явно назови NOT_CHECKED, даже если ARIA выглядит правильно. Если имеется реальный AT-инструмент/прогон, запиши platform/browser/AT и реальные действия отдельно.
6. Axe findings сверяй с actual UI и влиянием, не переписывай весь JSON в findings. Manual finding может отсутствовать в axe — это нормально.

## Что не считать дефектом автоматически

Не всякий неинтерактивный текст должен получать Tab focus. У правильного modal может быть сфокусирован заголовок/контейнер для понимания контекста, а не обязательно first input. Не каждый live region должен говорить каждое промежуточное число; оцени смысл и частоту. Весь row нельзя требовать как button, если семантика/управление иначе приняты и доступны.

Возврат focus после close имеет исходный trigger либо логичный next target, если trigger исчез по сценарию. Выбранный паттерн фиксируется источником, а не произвольным ожиданием reviewer.

Связь с первичными источниками: [WAI-ARIA APG modal dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) и [Playwright accessibility limits](https://playwright.dev/docs/accessibility-testing). APG guidance не объявлять юридической сертификацией продукта.
