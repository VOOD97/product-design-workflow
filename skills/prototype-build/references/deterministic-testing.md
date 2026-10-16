# Детерминированные сценарные проверки

## Observable result

Плохой тест: после клика существует heading «Result».

Хороший тест: выбраны три записи, submit вызывает согласованную операцию; partial fixture возвращает две success и одну failure; пользователь видит 2/1 summary, failures list содержит только третью; retry request содержит только failed ID; после retry сводка и доступные действия обновляются согласно контракту.

Проверка root `data-ui` обеспечивает traceability, но не доказывает правильность состояния. Добавляй asserts на смысл контента, действия и эффект. Название теста включает `S-ID` и `TEST-ID`. Используй реальные expected criteria, а не текст из текущего render без независимого источника.

## Селекторы и ожидания

Сначала `getByRole` + accessible name, затем `getByLabel`, точный текст, затем test ID при необходимости. Playwright locators auto-wait, assertions web-first. Жди agreed heading/state/URL/response. Избегай fixed sleeps и universal `networkidle`: polling/streams могут никогда не стать idle, а network quiet не гарантирует нужный UI state.

Локальные data-ui/test-id не заменяют semantic button/input. Не строй тест на brittle nth-child либо случайном class name, если есть стабильный пользовательский selector.

## Fixtures

| Fixture | Что задаётся | Что важно проверить |
| --- | --- | --- |
| normal | Стабильные records, роли, IDs | Полный user journey и meaningful result |
| empty | Нет records | Empty explanation и доступный следующий action |
| error-then-success | Определённая ошибка первой операции | Input сохранён, error понятен, retry восстанавливает |
| partial | Фиксированные success/failure IDs | Summary и retry только failures |
| permission-denied | Определённая роль/право | Действие отсутствует/ограничено по контракту; причина понятна |
| long-content | Long names/messages | Reflow, читабельность, actions доступны |

Выбирай только применимые fixtures; huge dataset и extreme values добавляй для реального риска. Безусловный набор «всего на свете» не заменяет P0 покрытие.

## Reset и safety

Изолируй contexts/storage, держи stable seed и controllable clock. Mock failures и latency выбираются явно; random delay не нужен для screenshots/tests. Тест не должен зависеть от предыдущего, запускаться на live production write API или оставлять реальные records.

Если fixture позволяет прямую загрузку terminal state, это полезно для screen evidence. Functional scenario test всё равно должен выполнить действия, ведущие к результату. Screenshots и snapshot diff не заменяют functional asserts.

## Accessibility и visual self-check

Проверь Tab/Shift+Tab, focus visibility, semantic labels, Enter/Space и applicable Escape, modal focus return. Axe scan добавляет автоматическое обнаружение части дефектов; ноль violations не означает certification. Для adopted visual spec проведи целевой browser comparison, сохрани viewport и source revision.

## JSON contract consistency

В `prototype-test-contract` должны быть:

- `version` и `revision`: версия схемы и точный identifier фактически проверяемого кода;
- `cases`: scenario, priority, test_id, type (`e2e` или `unit`), observable_result, mock, ui_ids, test_file;
- `screens`: ui_id, state, priority, route, mock, viewports;
- `viewports`: name, width, height.

priority имеет одно из `P0/P1/P2`; ui_ids разрешаются в screens; viewport names — в viewports. route ведёт к реальному screen/fixture, test_file существует. Не вводи self-assessed verdict или build-notes в этот блок. Матрица и JSON описывают одинаковые обязательства; neutral extract для reviewers не включает авторские объяснения.
