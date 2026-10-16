# Prototype Build — <задача>

> Шаблон. Замени все placeholders фактическими данными; JSON ниже — пример структуры, а не реальные тесты. Не выдавай команду/результат за выполненный без проверки.

## Metadata и контракт

- Status: <complete / partial / blocked>
- Decision status: <accepted / delegated / proposed / unknown>
- Gate: <PASS / LIMITED / FAIL>
- Revision: <code revision/hash + uncommitted state identifier при необходимости>
- Updated: <дата>
- Scope: <in / deferred / out>
- Sources: <actual contracts/requests and IDs>
- Accepted behavior/UI: <подтверждённое существенное; source>
- Proposed/unknown: <только реальные неизвестные>
- DS/components: <источники и reuse / provisional scope>

## Test matrix

| Scenario | Priority | TEST-ID | Type | Observable result | Mock | UI-ID / FLOW-ID | Test file |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <S-ID> | <P0/P1/P2> | <TEST-ID> | <e2e/unit> | <проверяемый эффект> | <fixture> | <IDs> | <существующий путь> |

<Импорт предоставленной внешней матрицы тестов, provenance, сохранённые обязательства/конфликты; если отсутствует — N/A.>

## Нейтральный test contract

Этот блок содержит только наблюдаемые условия. Он может быть извлечён отдельно для независимых проверок; авторские build-notes и выводы ниже в reviewer read-set не входят. В финальном документе ровно один блок такого типа, с актуальной ревизией и фактическими values.

```prototype-test-contract
{
  "version": 1,
  "revision": "<actual-code-revision>",
  "cases": [
    {
      "scenario": "<S-ID>",
      "priority": "P0",
      "test_id": "<TEST-ID>",
      "type": "e2e",
      "observable_result": "<expected user-observable effect from accepted contract>",
      "mock": "<fixture-name>",
      "ui_ids": ["<UI-ID>"],
      "test_file": "<actual-test-path>"
    }
  ],
  "screens": [
    {
      "ui_id": "<UI-ID>",
      "state": "<state-name>",
      "priority": "P0",
      "route": "<actual-route-including-fixture-selection>",
      "mock": "<fixture-name>",
      "viewports": ["<viewport-name>"]
    }
  ],
  "viewports": [
    {
      "name": "<viewport-name>",
      "width": 1280,
      "height": 800
    }
  ]
}
```

## Build-notes — авторский журнал

### Окружение и команды

- Runtime / package manager / browser / test runner versions:
- Install prerequisites:
- Launch command / verified URL:
- Tests / build / lint / typecheck commands:
- Fixture switch / reset / seed commands:
- Entry/source paths:

### Mock scope и ограничения

<Синтетические данные, mock clock/latency, реальные и simulated интеграции, persistence/security boundaries; чего прототип не подтверждает.>

### Отклонения и вопросы

| ID | Source/contract | Наблюдаемое отклонение/вопрос | Proposed resolution / статус | Влияние |
| --- | --- | --- | --- | --- |
| <ID> | <source> | <конкретное> | <материальное принятие или открытый вопрос> | <scope> |

### Фактические проверки

| Check / TEST-ID | Command / target / viewport | Result | Evidence path / N/A reason |
| --- | --- | --- | --- |
| <проверка> | <реально выполненное> | <PASS/FAIL/NOT_CHECKED/N/A> | <log/screenshot/test-result> |

<При failed run и повторном запуске укажи причину и итог; не скрывай skips и untested branches.>

## Prototype Ready

| Checklist item | Result | Evidence / блокер |
| --- | --- | --- |
| <пункт> | <PASS/FAIL/NOT_CHECKED/N/A> | <фактическое> |

Итог: <PASS / LIMITED / FAIL>.

<Технический итог, статус material contract, просмотренное/непроверенное, реальные ограничения. Это self-check, а не независимая приёмка.>
