# Design Stand — контракт визуальной поверхности

## Цель

Показать реальные screen × state до полной реализации поведения. Стенд — визуальная поверхность `ui-spec.md` той же revision, а не самостоятельный источник продуктовых решений.

## Выбор реализации

1. В кодовом проекте предпочти изолированный dev route или Storybook stories с существующими компонентами/tokens. Сохрани production routing и основную навигацию.
2. Без проекта допустим небольшой локальный HTML/CSS/JS либо минимальный browser app, который отображает реальные макеты. Для provisional tokens обозначь область действия.
3. Не требуй Figma, FigJam MCP или отдельный фреймворк. Если текущая среда не позволяет создать/просмотреть поверхность, запиши ограничение; это не выполненный стенд.

## Обязательные возможности

- Реальная отрисовка каждого P0 UI-ID; например, таблица пользователей с пустыми данными и действием приглашения, а не надпись «Users / Empty».
- Selector screen, state и viewport. Комбинации, не существующие в модели, не показываются как реальные.
- Стабильная ссылка вида route/query на конкретный UI-ID и fixture; используй фактическую схему проекта.
- Подпись UI-ID, related scenario/flow IDs, priority и decision status вне продуктового canvas.
- Выбор релевантных широкого/узкого размеров; viewport name связан с точными width/height. Frame resizing полезен, но критичные проверки делаются и на реальном browser viewport.
- Нужные interaction states: открытый dialog, focused/invalid field, expanded details, feedback async action. Бизнес-поведение может быть локальной демонстрацией с явной подписью.
- Переключение mock fixtures: normal, empty, error, partial, long-content, если применимо.

## Данные и синхронизация

Храни screen/state registry в одном месте кода стенда. Для каждой записи: UI-ID, state, title, priority, scenario IDs, flow IDs, fixture, renderer, decision status. Значения и контент должны соответствовать `ui-spec.md`; placeholder не считается реализованным состоянием.

Запиши revision спецификации в metadata стенда. Сверь P0 UI-ID из spec с registry. Удалённое состояние не оставляй в selector как принятое. Не допускай «accepted» у одного и «proposed» у другого. При изменении material decision обнови spec и render вместе.

## Изоляция

Используй synthetic fixtures и заблокируй production writes. Не имитируй неподтверждённое бизнес-правило без статуса assumption. Стенд доступен отдельно от основного UI; dev-only controls не должны выглядеть как продуктовые действия.

## Просмотр

Открой каждое P0 состояние, сделай relevant keyboard interactions и просмотри responsive layout/long content. Сравни с точными визуальными опорами продукта, записанными в spec. Дай конкретные ссылки и фактическую команду запуска. Не выдавай произвольный localhost port за уже работающий сервер.

При невозможности browser preview сохрани исходники и назови ограничение. Не ставь Interface Ready PASS на основании генерации HTML или compilation alone.
