# Паритет: контракт → код → rendered behavior → meaningful test

## Матрица трассировки

Для каждого обязательного P0: REQ/TASK, правило/сценарий, flow/UI если предусмотрены, источник реализации, test/assertion, actual result на текущей revision, live probe, deviation/limitation. Отсутствующий необязательный документ не является потерянным звеном: можно связать TASK прямо с UI/TEST, сохранив источник.

## Что читать и воспроизводить

| Область | Чтение в пределах read-set | Самостоятельный Playwright probe |
|---|---|---|
| Обязательное действие | Handler/route/state и accepted behavior | Пройти вход → действие → outcome обычным UI |
| Branch/guard | Условие роли/eligibility/validation | Данные/роль допустимы и недопустимы, observed feedback |
| Partial/retry | Как выбирается набор объектов и сохраняется success | Пройти partial → retry; сопоставить submitted test IDs при доступном trace |
| Error/recovery | State transitions, preservation и recovery target | Вызвать declared fixture, исправить/retry, проверить retained data/outcome |
| UI decision | Компонент/variant/content, accepted source | Отрисовать нужный UI×state и viewport, сравнить реально показанное |
| Тест | Assertions, fixtures, setup, проекты/retries/skips | Целевой existing test command или независимый probe того же observable result |
| Scope | Что добавлено/исчезло в пользовательском behavior | Проверить реально доступные features/paths; technical helpers не считать scope additions |

## Meaningful test review

Test name, наличие файла и green exit code — недостаточны. Прочитай, что именно assert:

- пользовательские действия действительно ведут к результату;
- assert не ограничен mount/button existence/HTTP 200;
- expected result следует принятому контракту, а не fixture текущей реализации;
- partial/retry проверяет правильные объекты, если они существенны;
- direct terminal-state loading не засчитан как happy path;
- mocks не убрали условие, которое тест якобы проверяет;
- actual reporter относится к этой revision и не содержит hidden skip/flaky/expected failure.

При доступном runner можно самостоятельно выполнить targeted существующий тест в изолированной тестовой среде и сохранить stdout/report в свой supplemental directory. Не менять assertions или продуктовый код, чтобы сделать green. Если тест запускает shared reset/data mutation, согласуй техническую изоляцию с координатором; не ломай параллельные fixtures.

Независимый probe может показать, что тестовый PASS не защищает контракт. Опиши отдельно test gap и observed product deviation; не склеивай разные первопричины без основания.

## Пределы вывода

Код проверяет tracing/guard — это не доказательство фактического пользовательского опыта или server security. Rendered UI показывает feedback — это не доказательство persistence. Request trace подтверждает только наблюдаемый request, не hidden backend behavior.

Технически неидеальная архитектура/название переменной вне scope. Несогласованная смена принятого summary на generic toast — паритетное отклонение, даже если код чистый и тесты проходят.

Не читай author build-notes/оправдания. Источник accepted exception должен быть отдельным подтверждённым решением, не заявлением исполнителя. Source/code hashes и revision сверяются до и после; изменение источника делает сравнение stale.
