---
run_id: <run-id или null>
revision: <revision или null>
status: complete | partial | blocked
decision_status: N/A
gate: PASS | LIMITED | FAIL
---

# Review synthesis

## Область, версии и полнота
| Роль | Worker terminal status | Отчёт и статус | Выполнено / ограничения |
|---|---|---|---|

## Итоговая оценка
Что известно о качестве продукта; что остаётся неизвестно. Отдельно готовность ревью, отдельно открытые проблемы продукта.

## Must fix
## Should fix
## Can stay
## To verify / отклонённые выводы

| SYN-ID | Оригинальные IDs | Группа | Severity | Layer | Location | Observation / impact | Source | Evidence | Verify | Status / основание |
|---|---|---|---|---|---|---|---|---|---|---|

## Противоречия и продуктовые вопросы
Варианты, последствия, владельцы; что осталось нерешённым.

## Маршрутизация и критерии повторной проверки
| Item IDs | Reason type | Причина / источник или пробел | Ближайший ответственный | Обязательность | Нужное действие | Критерий проверки / reviewers |
|---|---|---|---|---|---|---|

Связывай с SYN-ID, вопросами Q-* и проверками CHECK-*; сохраняй существующие ID. reason_type: PRODUCT_AMBIGUITY / VISUAL_DECISION_MISSING / IMPLEMENTATION_GAP / VISUAL_DRIFT / OTHER / UNKNOWN. necessity: required / recommended / optional / none. Это дополнительная маршрутизация, не замена severity, layer и origins. Укажи подтверждённого владельца или роль без выдуманного имени. Сохрани всех владельцев независимых задач.

## Ближайший следующий шаг

- Что обязательно / рекомендуется / опционально / ещё не проверено:
- Kind: decision / implementation / verification / none:
- Necessity: required / recommended / optional / none:
- Связанные item IDs:
- Один основной ответственный за первый шаг (исполнитель или координатор; участники проверки перечисляются отдельно; никто, если действий нет):
- Почему этот шаг первый: влияние, блокирующая зависимость, доступность:
- Одно короткое поручение со ссылкой на этот synthesis.md и нужные ID:
- Как и кем проверить результат:
- Какие независимые задачи могут продолжаться:

При недостатке evidence требуется проверка, а не исправление недоказанного дефекта. Не назначай автоматически продуктовый разбор раньше независимого Must fix реализации. Отсутствие действий не означает принятия продукта. Не включай технический план ремонта и не запускай следующий скилл.

## Preserve / What works well
Наблюдаемые достоинства и исходные reviewer IDs/evidence.

## Gate: Reviews Ready
| Пункт | Результат | Доказательство / ограничение |
|---|---|---|
PASS / LIMITED / FAIL, scope и причины.

## Данные синтеза
Один блок synthesis-data с JSON: run_id, revision, capture_sha256, status, coverage [{report_type,status,path}], findings [{id,origins,group,severity,layer,source,evidence,verify,status}], questions [], preserve [], limitations [], routing [{item_ids,reason_type,reason,source,evidence,owner,necessity,next_action,verify,reviewers}], next_step {kind,necessity,item_ids,owner,reason,action,verify}. Конкретные значения и файлы, не шаблонные placeholders.

item_ids — массив существующих SYN-ID, Q-ID или CHECK-ID из этого отчёта; source/evidence — массивы ссылок на основания (при UNKNOWN допустим пустой массив с объяснением пробела в reason); reviewers — массив нужных ролей. owner — строка с ролью или подтверждённым владельцем. При полном отсутствии действий routing=[], next_step.kind=none, necessity=none, item_ids=[], owner=null, action=null, verify=null; reason объясняет scope и ограничения. reason_type, kind и necessity выбирай по synthesis-rules.md, а не оставляй перечислением. Не удаляй действующие поля findings и не меняй исходные review-data. Текст, routing и next_step должны совпадать по IDs, причине, владельцу и обязательности.
