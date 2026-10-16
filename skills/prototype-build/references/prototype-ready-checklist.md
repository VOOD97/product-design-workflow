# Prototype Ready — проверяемый чеклист

Отметь выполненные проверки, а в `prototype-build.md` запиши каждой строке `PASS / FAIL / NOT_CHECKED / N/A`, фактическое evidence и N/A reason. Checkbox означает факт проверки. Недоступный tool не равен успешно пройденной проверке.

- [ ] Scope, роли, принятый product/UI contract и material unknowns определены; существующие решения не передизайнены молча.
- [ ] Прототип запускается документированной фактической командой; URL/route проверен.
- [ ] Existing stack, package manager, repository instructions и shared components/tokens соблюдены.
- [ ] Embedded matrix создана из сценариев/criteria; каждое P0 имеет функциональный тест observable result.
- [ ] Primary user flow проходит browser e2e с действиями пользователя, а не только проверкой render.
- [ ] Все P0 screen × state представлены в neutral `screens`, достижимы и реально проверены.
- [ ] Source/scenario/FLOW/UI/TEST traceability проверена; links/test_file существуют.
- [ ] В документе ровно один valid `prototype-test-contract` JSON, имеющий required cases/screens/viewports/version/revision.
- [ ] Все ui_ids и viewport names JSON разрешаются; priority согласован с исходным контрактом; current revision совпадает с кодом.
- [ ] Neutral contract не содержит авторских verdicts/оправданий; build-notes отделены.
- [ ] Fixtures deterministic, reset reproducible, mock switching документирован; нет зависимости от test order.
- [ ] Critical error/retry/partial/permission/cancel branches проверены либо N/A с конкретной причиной.
- [ ] Lint/typecheck/build/unit прошли, либо отсутствие/неприменимость отдельных checks обоснованы.
- [ ] Token rules проверены штатным token-lint либо фактически описанной scoped проверкой; локальные exceptions согласованы.
- [ ] P0-functional tests прошли без скрытых skips; failed check/failure rerun отражены честно.
- [ ] Console/page errors проверены; существенных unexplained errors нет.
- [ ] Responsive layouts, long content и material interaction states просмотрены на documented viewports.
- [ ] Semantic controls, labels, keyboard/focus/dialog lifecycle заложены и проверены в доступном объёме.
- [ ] Deviations, assumptions, open questions и mock limitations записаны; simulated backend не выдан за реальный.
- [ ] Production writes/deployment отсутствуют; synthetic data и local/test targets использованы.
- [ ] Рабочий код, tests и один `prototype-build.md` предоставлены; существующие optional input files сохранены.

## Итог

- **PASS** — обязательные применимые условия подтверждены, существенный контракт принят или выбор делегирован; P0 покрытие и обязательные проверки завершены.
- **LIMITED** — обязательные условия выполнены, остаётся явно неблокирующее ограничение охвата/доставки. Не скрывай обязательную проверку под этим статусом.
- **FAIL** — нарушено обязательство, отсутствует P0 покрытие, обязательное решение остаётся proposed/unknown либо существенная обязательная проверка NOT_CHECKED. Назови причину; непроверенное не выдавай за доказанный дефект.

Статус полноты complete/partial/blocked и decision_status запиши отдельно по artifact-contract.md. При отсутствии браузера обязательная проверка получает NOT_CHECKED; черновик всё равно передай с конкретным условием завершения.

## Доставка результата (отдельно от профильного гейта)

- [ ] Папка задачи выбрана по `artifact-contract.md`; основной документ и приложения действительно сохранены, либо невозможность записи явно сообщена.
- [ ] Пользователю переданы краткий вывод, ссылки и полный Markdown той же версии прямо в чате; сводка/ZIP не заменяют текст. Для субагента основной сессии переданы отчёт и обязанность доставки; пользовательская доставка завершена только после её ответа.
- [ ] Ограничения сохранения, доступа и неполного дублирования названы явно; они не выданы за дефекты продукта. В связке evidence/review основная сессия доставила все реально полученные отчёты и назвала отсутствующие.
