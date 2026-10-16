---
run_id: synthetic-run
revision: synthetic-rev
status: partial
---

# Review synthesis

## Область, версии и полнота

Самостоятельный синтез пяти назначенных учебных отчётов о UI-001: пустой Email, доступность Submit, сообщение ошибки и положение фокуса после ошибки. Источники: `../synthesis-input/{ux,visual,accessibility,content,parity}.md`, нейтральный контракт `../synthesis-input/ui-spec.md` и учебные наблюдения `../synthesis-input/observations.md`. Ссылки ниже относительны к этому файлу, если не указано иное.

Все пять workers завершены **по явному сообщению пользователя**; отдельные журналы terminal status не предоставлены. Завершение worker не означает `complete` для его отчёта. Все пять `review-data` имеют `status: partial`, `run_id: synthetic-run`, `revision: synthetic-rev`, `capture_sha256: synthetic-capture`. Последнее значение — учебный идентификатор, а не проверенный SHA-256 реального capture. Отдельный evidence manifest не предоставлен; наблюдения доступны непосредственно в `observations.md`.

| Роль | Worker terminal status | Отчёт и статус | Выполнено / ограничения |
|---|---|---|---|
| UX | completed — сообщение пользователя | `../synthesis-input/ux.md`, partial | Статические учебные материалы; finding по N9. Полный walkthrough и набор Nielsen не выполнены/не подтверждены. |
| Visual | completed — сообщение пользователя | `../synthesis-input/visual.md`, partial | Статические учебные материалы; findings нет. Нет визуального capture, оценки композиции, размеров или состояний. |
| Accessibility | completed — сообщение пользователя | `../synthesis-input/accessibility.md`, partial | Учебное наблюдение о фокусе; нет браузера, assistive technology или полного аудита доступности. |
| Content | completed — сообщение пользователя | `../synthesis-input/content.md`, partial | Статические учебные материалы; findings нет. Сам текст ошибки и оценка его качества не предоставлены. |
| Parity | completed — сообщение пользователя | `../synthesis-input/parity.md`, partial | Сопоставление учебного наблюдения с контрактом; код и реальные тесты не предоставлены, design-code parity не проверена. |

**Coverage:** получены 5/5 назначенных отчётов, отсутствующих или failed workers по сообщению пользователя — 0/5; complete отчётов — 0/5, partial — 5/5. Все пять ролей участвовали только в заявленном статическом учебном scope. Реальные браузерные проверки не выполнены во всех пяти профилях. Точный процент покрытия отдельных проверок неизвестен: перечни требуемых проверок и полный журнал не предоставлены.

## Итоговая оценка

В учебных данных подтверждаются два несоответствия принятому контракту UI-001: фокус после ошибки остаётся на Submit, а Submit активен при пустом Email. Три исходных findings сведены в две группы без потери ID. Видимость сообщения ошибки — общая положительная сторона всех пяти отчётов, поддержанная учебным наблюдением.

**Reviews Ready: LIMITED** для синтеза предоставленного учебного пакета. Все назначенные отчёты получены и совместимы, их выводы можно проследить до учебного контракта и наблюдений. PASS невозможен: все отчёты partial, полноценный UX walkthrough/Nielsen и профильные проверки не подтверждены. Оснований объявлять реальный продукт готовым, дефектным по фактическому браузерному прогону или соответствующим WCAG нет. Отсутствие findings в visual/content не доказывает качество непроверенных областей.

## Must fix

Это приоритет подтверждённых **учебных** несоответствий, если предоставленные наблюдения описывают целевое поведение. Статусы остаются open; исправление и принятие риска не назначены. Для вывода о реальном продукте требуется отдельная проверка.

| SYN-ID | Оригинальные IDs | Группа | Severity | Layer | Location | Observation / impact | Source | Evidence | Verify | Status / основание |
|---|---|---|---|---|---|---|---|---|---|---|
| SYN-001 | UX-001, A11Y-001 | Фокус после ошибки | High | ui | UI-001 / ошибка после пустой отправки | Фокус остаётся на Submit, поэтому пользователь должен найти ошибочное поле. Tab переводит фокус на Email: учебные данные не подтверждают ловушку фокуса или полную невозможность продолжить. | `../synthesis-input/ui-spec.md`: после validation error фокус на Email | `../synthesis-input/observations.md`, строка 2; `ux.md` → UX-001; `accessibility.md` → A11Y-001 | В безопасном браузерном окружении воспроизвести доступную validation error, проверить active element сразу после ошибки и путь Tab. Ошибка должна переводить фокус на Email; видимость ошибки должна сохраняться. | open; confirmed_synthetic. Оба ID описывают одно состояние и одно нарушение контракта. High сохранён из accessibility как консервативный приоритет, не как подтверждённая блокировка или результат WCAG-аудита. |
| SYN-002 | PAR-001 | Доступность отправки при пустом Email | High | implementation | UI-001 / пустой Email до отправки | Submit активен при пустом Email; учебное наблюдение о пустой отправке также показывает достижимость состояния ошибки. Принятое условие недоступности отправки не соблюдено в учебных данных. | `../synthesis-input/ui-spec.md`: при пустом email отправка недоступна | `../synthesis-input/observations.md`, строки 2–3; `parity.md` → PAR-001 | Открыть пустую форму в безопасном браузерном окружении; проверить состояние Submit и возможность отправки доступными способами. При пустом Email отправка должна быть недоступна. Сопоставление с реализацией требует доступа к коду. | open; confirmed_synthetic. High сохранён: прямое нарушение явно принятого условия отправки. Implementation — маршрут из parity report; причина в коде не установлена. |

## Should fix

Подтверждённых отдельных findings этой категории в назначенном учебном scope нет.

## Can stay

Подтверждённых нарушений с документированным принятием риска нет. Синтезатор не принимает риск за владельца продукта. Положительные наблюдения приведены в Preserve.

## To verify / отклонённые выводы

Исходные findings не отклонены: контракт и учебные наблюдения доступны, факты прослеживаются. Они подтверждены исключительно внутри synthetic scope. Ни одному finding не присвоен статус fixed или accepted.

| Ссылка | Что требует проверки | Причина / граница вывода |
|---|---|---|
| SYN-001; UX-001, A11Y-001 | Фактический фокус после validation error и влияние на пользователя в реальном UI | Browser не запускался. Исходная location «invalid email» не подтверждена отдельным наблюдением: evidence описывает **пустую** отправку. Location синтеза уточнена по первичному наблюдению; поведение для непустого невалидного адреса неизвестно. |
| SYN-001; UX-001, A11Y-001 | Исходный reproduce «пустая отправка» после приведения доступности Submit к контракту | Согласно контракту пустая отправка должна быть недоступна. Эти две проверки нельзя использовать как один обязательный последовательный сценарий: для фокуса нужна доступная validation error. Проверка непустого невалидного Email возможна только если этот сценарий определён целевым продуктом. |
| SYN-002; PAR-001 | Реальная доступность отправки и соответствие коду | Код, тесты и browser evidence отсутствуют. Подтверждено сравнение учебных наблюдений с контрактом, не проверка реализации. |
| Все пять отчётов | Полный UX walkthrough/Nielsen и профильные visual, accessibility, content, parity проверки | В checks каждого отчёта только «Статические учебные материалы». Недостаток покрытия не превращается в новые findings или отсутствие дефектов. |

## Противоречия и продуктовые вопросы

UX-001 (Medium) и A11Y-001 (High) совпадают по месту, факту, evidence и нарушенному контракту. Они объединены в SYN-001. Разницу severity разрешаем консервативным High из accessibility с явной оговоркой: указанное влияние одинаково, а наблюдение о Tab ограничивает утверждения о тяжести. Приоритет не основан на голосовании и не означает подтверждённую блокировку.

SYN-001 и SYN-002 входят в общий сценарий ошибки формы, но **не объединены**: первое нарушение относится к фокусу после ошибки, второе — к доступности отправки до ошибки. Исправность одного не подтверждает исправность другого; общей первопричины источники не устанавливают.

Контракт однозначно требует недоступную пустую отправку и фокус на Email после validation error. Нерешённой продуктовой развилки между этими требованиями не обнаружено; открытых продуктовых вопросов — 0. Уточнение сценария реальной validation error и сбор реального evidence остаются задачами верификации, а не разрешением синтезатора менять контракт. Владелец продуктового контракта отвечает за уточнение сценария, если существующих условий недостаточно для воспроизведения.

## Маршрутизация и критерии повторной проверки

| Группа / область | Ответственность | Критерий будущей проверки | Нужные reviewers |
|---|---|---|---|
| SYN-001, ui | Владелец интерфейса; реализация участвует в проверке фактического фокуса | Сразу после доступной validation error active element — Email; сообщение ошибки видно; клавиатурный путь проверен. | UX и accessibility |
| SYN-002, implementation | Владелец реализации; владелец продуктового контракта уточняет условия отправки при необходимости | В пустой форме отправка недоступна согласно контракту; состояние проверено в UI и сопоставлено с кодом. | Parity; accessibility для доступности управляющего элемента |
| Непроверенные части пяти профилей | Владельцы соответствующих областей ревью | Подтверждены реальные сценарии, версия и evidence; полный назначенный scope каждого отчёта явно завершён либо ограничен. | UX, visual, accessibility, content, parity |

Маршрутизация обозначает ответственность и критерии проверки, а не план изменения кода. Исправления, повторное ревью и принятие baseline этим синтезом не запускаются.

## Preserve / What works well

**Сохранять явное сообщение ошибки после неуспешной отправки.** Происхождение: `works_well` и What works well всех пяти отчётов (`ux.md`, `visual.md`, `accessibility.md`, `content.md`, `parity.md`); первичный источник — `../synthesis-input/observations.md`, строка 2: после пустой отправки показана ошибка. У положительных наблюдений в отчётах нет отдельных ID; новые reviewer IDs не выдуманы.

Это подтверждение видимости в учебном описании. Оно не доказывает контраст, ясность текста, программную связь с Email или объявление ошибки screen reader. Учебное наблюдение о переходе Tab на Email ограничивает вывод об отсутствии доступа к полю, но не отменяет требование автоматического фокуса и не считается принятием риска.

## Gate: Reviews Ready

| Пункт обязательного чеклиста | Результат | Доказательство / ограничение |
|---|---|---|
| Все назначенные workers terminal и все пять отчётов получены | Выполнено по входным данным | Завершение пяти workers явно сообщил пользователь; 5/5 файлов прочитаны. Отдельные журналы workers отсутствуют. |
| Run/revision/capture совпадают, смешение версий исключено | Выполнено в synthetic scope | Все пять review-data: synthetic-run / synthetic-rev / synthetic-capture. Реальный capture и его хеш не проверены. |
| UX walkthrough и Nielsen выполнены либо непроведённое ограничивает итог; каждый отчёт содержит Preserve и findings/их отсутствие | Ограничено | Во всех пяти отчётах есть works_well и findings; visual/content явно имеют пустые findings. UX содержит один finding N9, полный walkthrough/Nielsen не подтверждён. Это ограничивает итог. |
| Каждый подтверждённый finding имеет layer/source/evidence/verify; недоказанное отделено | Выполнено в synthetic scope | SYN-001/SYN-002 содержат все поля, первичные источники прочитаны. Утверждения о реальном UI и коде выделены в To verify. |
| Дубли объединены без потери origins; противоречия рассмотрены; продуктовые развилки не выбраны молча | Выполнено | UX-001 + A11Y-001 → SYN-001; PAR-001 → SYN-002. Разница severity, location и сценарий проверки разобраны. Продуктовый контракт не изменён. |
| Must fix / Should fix / Can stay / To verify различены; принятие риска не выдумано | Выполнено | Две учебные группы Must fix; остальные категории явно описаны, реальные проверки отделены; fixed/accepted не назначены. |
| Маршрутизация, критерии проверки и reviewers указаны без реализации исправлений | Выполнено | Таблица ответственности и критериев выше; исходные материалы и реализация не менялись. |
| Preserve имеет evidence и защищает хорошие части | Выполнено в synthetic scope | Видимость ошибки прослеживается до пяти works_well и строки 2 observations.md. Ограничения утверждения сохранены. |
| Один synthesis-data согласован с Markdown; гейт и полнота доступны без чата | Выполнено | Один блок ниже: 5 partial reports, 3 origins, 2 synthetic findings, gate LIMITED. |

**Результат: LIMITED.** Назначенный пакет синтезирован полностью как учебный статический набор; сама проверка продукта ограничена во всех пяти профилях. Все отчёты partial, поэтому PASS не заявляется. Missing/blocked профилей и несовместимости версий не выявлено; основные учебные выводы проверяемы по доступным источникам, поэтому FAIL для этого самостоятельного учебного scope не требуется. Независимость процесса получения отчётов отдельно не аудировалась; пакет используется как пять предоставленных reviewer reports. Готовность продукта к публикации не установлена.

## Данные синтеза

```synthesis-data
{
  "run_id": "synthetic-run",
  "revision": "synthetic-rev",
  "capture_sha256": "synthetic-capture",
  "status": "partial",
  "gate": "LIMITED",
  "scope": "Standalone synthesis of five supplied static educational reports for UI-001; not a real browser capture",
  "coverage": [
    {"report_type": "ux", "status": "partial", "path": "../synthesis-input/ux.md", "worker_status": "completed", "worker_status_source": "Explicit user statement"},
    {"report_type": "visual", "status": "partial", "path": "../synthesis-input/visual.md", "worker_status": "completed", "worker_status_source": "Explicit user statement"},
    {"report_type": "accessibility", "status": "partial", "path": "../synthesis-input/accessibility.md", "worker_status": "completed", "worker_status_source": "Explicit user statement"},
    {"report_type": "content", "status": "partial", "path": "../synthesis-input/content.md", "worker_status": "completed", "worker_status_source": "Explicit user statement"},
    {"report_type": "parity", "status": "partial", "path": "../synthesis-input/parity.md", "worker_status": "completed", "worker_status_source": "Explicit user statement"}
  ],
  "coverage_summary": {"reports_received": 5, "reports_assigned": 5, "reports_complete": 0, "reports_partial": 5, "reports_missing": 0, "workers_failed_reported": 0, "profiles_without_real_browser_evidence": 5, "raw_findings": 3, "synthetic_findings_after_deduplication": 2, "rejected_findings": 0},
  "findings": [
    {
      "id": "SYN-001",
      "origins": [{"report_type": "ux", "id": "UX-001", "path": "../synthesis-input/ux.md", "severity": "Medium"}, {"report_type": "accessibility", "id": "A11Y-001", "path": "../synthesis-input/accessibility.md", "severity": "High"}],
      "group": "Must fix",
      "severity": "High",
      "severity_reason": "Conservative priority retained from accessibility; Tab reaches Email, so no complete keyboard blockage is established",
      "layer": "ui",
      "location": "UI-001 / validation error after empty submission in synthetic observations",
      "observation": "Focus remains on Submit after an error",
      "impact": "User must locate the erroneous Email field",
      "source": ["../synthesis-input/ui-spec.md: focus on Email after validation error"],
      "evidence": ["../synthesis-input/observations.md:2", "../synthesis-input/ux.md:UX-001", "../synthesis-input/accessibility.md:A11Y-001"],
      "verify": "In a safe browser environment trigger an available validation error and inspect active element immediately afterwards and the Tab path; expected focus is Email and the error remains visible. Empty submission must separately remain unavailable per the contract.",
      "reviewers": ["ux", "accessibility"],
      "status": "open",
      "validation": "confirmed_synthetic",
      "limitations": ["No real browser run", "Nonempty invalid email state is not independently observed", "Original empty-submission reproduction conflicts with the required unavailable empty submission once that contract is met"]
    },
    {
      "id": "SYN-002",
      "origins": [{"report_type": "parity", "id": "PAR-001", "path": "../synthesis-input/parity.md", "severity": "High"}],
      "group": "Must fix",
      "severity": "High",
      "severity_reason": "Explicit accepted submission condition is violated in the synthetic observations",
      "layer": "implementation",
      "location": "UI-001 / empty Email before submission",
      "observation": "Submit is active with empty Email",
      "impact": "Accepted condition that empty-email submission is unavailable is not preserved",
      "source": ["../synthesis-input/ui-spec.md: submission unavailable when email is empty"],
      "evidence": ["../synthesis-input/observations.md:2-3", "../synthesis-input/parity.md:PAR-001"],
      "verify": "Open an empty form in a safe browser environment and inspect Submit availability and submission through available interaction methods; submission must be unavailable. Code parity requires code access.",
      "reviewers": ["parity", "accessibility"],
      "status": "open",
      "validation": "confirmed_synthetic",
      "limitations": ["No code or real tests supplied", "Implementation layer is the review routing, not a demonstrated code root cause"]
    }
  ],
  "questions": [],
  "preserve": [
    {
      "observation": "Error message is visibly shown after unsuccessful submission in the synthetic observations",
      "origins": ["../synthesis-input/ux.md:works_well", "../synthesis-input/visual.md:works_well", "../synthesis-input/accessibility.md:works_well", "../synthesis-input/content.md:works_well", "../synthesis-input/parity.md:works_well"],
      "evidence": ["../synthesis-input/observations.md:2"],
      "limitations": ["No individual positive-observation IDs supplied", "Visibility does not establish contrast, wording quality, programmatic association or screen-reader announcement"]
    }
  ],
  "limitations": [
    "All five reports are partial and based on static educational materials",
    "All five workers are completed according to the explicit user statement; terminal logs were not supplied",
    "synthetic-capture is a supplied synthetic identifier, not a verified SHA-256 of a real capture; no separate evidence manifest supplied",
    "Full UX walkthrough and Nielsen coverage are not demonstrated",
    "Visual and content empty findings do not establish absence of defects in unreviewed areas",
    "No real browser capture, assistive-technology run, code or real tests supplied",
    "The independent report-production process was not separately audited",
    "Actual product behavior, product readiness and WCAG conformance are not established",
    "No fixes, rerun, baseline acceptance, risk acceptance or implementation changes performed"
  ]
}
```
