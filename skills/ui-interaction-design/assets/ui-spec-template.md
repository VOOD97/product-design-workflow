# UI Specification — <задача>

> Шаблон, не готовый результат. Замени placeholders; статусы и доказательства заполни фактически. Удали только неприменимые подразделы с явным N/A. Не копируй пример как принятое решение.

## Metadata

- Revision: <стабильная ревизия spec/stand>
- Updated: <дата>
- Status: <complete / partial / blocked>
- Decision status: <accepted / delegated / proposed / unknown>
- Gate: <PASS / LIMITED / FAIL>
- Scope: <in / deferred / out>
- Platforms/viewports: <названия и точные размеры>

## Задача, источники и ограничения

<Пользователь, цель, источник требований; accepted constraints, observations, assumptions, unknowns, conflicts. Необязательные документы используйте только при наличии.>

## Design system и visual references

| Источник/путь | Что переиспользовано | Проверено/доступно | Gap/provisional scope |
| --- | --- | --- | --- |
| <DS/компонент/экран> | <точные tokens/variants/pattern> | <свидетельство или ограничение> | <gap/N/A> |

## Матрица покрытия

| UI-ID | Экран × state | Priority | S-ID / FLOW-ID | Fixture | Decision status | Stand reference |
| --- | --- | --- | --- | --- | --- | --- |
| <UI-ID> | <экран/state> | <P0/P1/P2> | <ID либо task-local источник> | <mock> | <accepted/proposed> | <реальный route/deep link> |

## Спецификация screen × state

### <UI-ID> — <экран / состояние>

- Purpose / наблюдаемый результат:
- Role, inputs, preconditions:
- Linked scenario/flow, source:
- Content hierarchy / layout:
- Components, variants, tokens:
- Exact copy, labels, validation:
- Actions, transitions, feedback, retry/cancel:
- Responsive behavior:
- Semantics, keyboard/focus, announcements:
- Fixture / stand reference:
- Acceptance: <проверяемый результат>

<Повтори для каждого screen × state; shared правила описывай один раз и ссылайся на них.>

## Решения и варианты

| Decision ID | Выбор / источник | Альтернативы, рекомендация и trade-off | Статус | Подтверждение / выбранный reference |
| --- | --- | --- | --- | --- |
| <D-ID> | <материальное решение> | <рассмотренное> | <accepted/proposed> | <источник; отсутствие явно> |

Для существенного выбора кратко укажи: что известно из продукта; что предложено и на каком основании; какой вопрос ещё требует решения. Сохрани итог реакции пользователя или область делегирования и конкретный выбранный reference. Рекомендация остаётся proposed до подтверждения или принятия в пределах делегирования; остальные решения и ID сохраняются. Не создавай искусственный выбор или журнал переписки.

## Design Stand

- Source path / entry:
- Launch command: <реальная команда проекта>
- Actual URL / route: <после проверки; иначе статус незапущенного>
- Revision / registry:
- Covered P0 UI-ID and fixtures:
- Previewed viewports / visual references:
- Interaction demo limits:

## Открытые вопросы и ограничения

| ID | Вопрос/ограничение | Влияние и блокирующий scope | Чьё решение / минимальные данные |
| --- | --- | --- | --- |
| <Q-ID> | <конкретное неизвестное> | <P0/локальное> | <роль/данные> |

## Interface Ready

| Проверка из checklist | Результат | Evidence reference / N/A reason |
| --- | --- | --- |
| <пункт> | <PASS/FAIL/NOT_CHECKED/N/A> | <фактическое свидетельство> |

Итог: <PASS / LIMITED / FAIL>.

<Материальные незавершённые решения, ограничения просмотра и почему итог соответствует фактам.>
