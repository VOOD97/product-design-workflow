---
task: <task-slug>
run_id: <run-id>
revision: <actually-served-revision>
status: complete | partial | blocked
decision_status: N/A
gate: PASS | LIMITED | FAIL
---

# Evidence manifest

## Предмет и контракт
Задача, scope, пользователь, canonical sources/brief и подтверждённые ограничения. Нейтральная матрица без author rationale. Путь/SHA-256 исходного test-contract.json; версия и результат сверки capture-config против него; контракт передан без изменения схемы.

## Окружение и воспроизведение
Node, Playwright, browser, axe версии; проверенный URL/порт; command; reset/seed/mock/auth способ без secrets. Связь server revision/source hashes и ограничения.

## Expected / captured coverage
| UI-ID | State | Priority | Viewport | Screenshot | Trace | Axe | Keyboard | Result |
|---|---|---|---|---|---|---|---|---|

## Functional evidence
| S-ID | TEST-ID | Priority | Observable result | Actual status | File / provenance |
|---|---|---|---|---|---|

## Остальные evidence и целостность
Axe-report, keyboard trace, console logs, capture-result SHA, source fingerprints и links. Непроверенные/ошибочные states не скрывать.

## Gate: Evidence Ready
| Пункт | Result | Evidence / блокер |
|---|---|---|
PASS / LIMITED / FAIL и условия продолжения.

## Параллельные reviewers и синтез
| Agent | Terminal status | Output | Coverage / limitation |
|---|---|---|---|
Reviews Ready отдельно; timeline запуска/завершения подтверждает параллельную диспетчеризацию, а не обещание одинакового времени завершения. Ссылка на review-run и synthesis.

## Ограничения и выдача
Что действительно собрано/просмотрено; непроведённые проверки; относительные ссылки на передаваемые файлы. Не утверждать исправленный/готовый продукт.
