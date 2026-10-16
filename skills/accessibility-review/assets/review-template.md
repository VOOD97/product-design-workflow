---
report_type: <ux | visual | accessibility | content | parity>
run_id: <run-id или null>
revision: <revision или null>
status: complete | partial | blocked
decision_status: N/A
gate: PASS | LIMITED | FAIL
---

# <Название> review

## Область и источники
Read-set, версии, условия, capture_sha256. Что реально открыто и проверено.

## Проверки
| Проверка / screen-state | выполнено / N/A / не проверено | Наблюдение и evidence / причина |
|---|---|---|

## Browser checks / собственная проверка
| Check ID | Контракт / гипотеза | Fixture / UI / viewport | Действия | Expected / Actual | Result | Evidence / limits |
|---|---|---|---|---|---|---|
Указать, что реально воспроизведено через Playwright, что взято из provided evidence, что осталось static/NOT_CHECKED. Непроверенное не становится passed.

## What works well
Наблюдаемые сильные стороны с источником/evidence; если оценить нельзя, честно указать.

## Findings
Одна запись на проблему: ID, severity, layer, location, heuristic, observation, impact, source, evidence, verify, status, confidence, limits.
Если findings пусты — «В проверенной области замечаний не выявлено», не «продукт идеален».

## Ограничения и открытые вопросы
Неизвестное, недоступное, границы оценки, что нужно для проверки.

## Статус проверки отчёта
Таблица чеклиста: пункт, PASS / FAIL / NOT_CHECKED / N/A, доказательство. Итог гейта: PASS / LIMITED / FAIL.

## Данные отчёта
Ровно один блок review-data. Схема:

```review-data
{"report_type":"accessibility","run_id":null,"revision":null,"capture_sha256":null,"status":"partial","findings":[],"works_well":[],"checks":[],"browser_checks":[],"evidence_files":[],"limitations":["Шаблон: заполнить реальными результатами; это не проведённое ревью."]}
```

Browser evidence paths относительны папке отчёта: evidence/<role>/<attempt>/file. evidence_files содержит path/sha256/kind/check_ids. UX дополнительно включает heuristic_coverage для N1–N10, с status и evidence/reason.
