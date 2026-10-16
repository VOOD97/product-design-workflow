# Нейтральный контракт и конфигурация evidence

## Источник

Основной контракт критериев тестирования находится в единственном fenced-блоке `prototype-test-contract` предоставленного prototype-build.md. Матрица Markdown и JSON должны совпадать; перед извлечением проверь это по смыслу. Экстрактор проверяет структуру, а не достаточность продуктовых assertions.

Если этого документа нет, самостоятельно заполни технический test-contract.json по assets/test-contract.example.json из текущего запроса, утверждённых критериев, реальных tests/fixtures и screen states. Не требуй создания prototype-build.md. Технический файл содержит только version/revision/cases/screens/viewports; авторские выводы и PASS в нём запрещены. В manifest укажи происхождение каждого критерия.

## Извлечение и проверяемое преобразование

Примеры ниже используют пути относительно проекта; заменить placeholders фактическими значениями. `--out` должен отсутствовать. Прежние evidence/контракты не перезаписываются.

```bash
python3 <skill-dir>/scripts/test_contract.py extract --document <project>/prototype-build.md --project <project> --out <project>/work/task/test-contract.json
python3 <skill-dir>/scripts/test_contract.py build-config --contract <project>/work/task/test-contract.json --runtime <project>/work/task/capture-runtime.json --project <project> --out <project>/work/task/capture-config.json
python3 <skill-dir>/scripts/test_contract.py verify --contract <project>/work/task/test-contract.json --config <project>/work/task/capture-config.json --project <project>
```

capture-runtime.json по assets/capture-runtime.example.json задаёт task/revision/baseUrl/sourceFiles, реальный argv функционального runner и capture_overrides. Каждый override относится к UI-ID/state/viewport и содержит фактический state-specific wait.selector, при необходимости actions/keyboard. Эти настройки не угадываются по названию состояния. Сервер, reset/namespace/auth подготовить отдельно.

| Нейтральный контракт | Конфигурация collector |
| --- | --- |
| revision | Та же revision |
| cases с type=e2e | functional.cases со всеми исходными полями без изменения |
| cases с type=unit | Сохраняются в нейтральном контракте; не объявляются Playwright e2e. Каждый P0 scenario также обязан иметь P0 e2e case |
| viewports: массив name/width/height | Словарь name → width/height |
| screens[].route | screens[].path |
| screens[].viewports | Одна цель на каждый UI-ID/state/viewport |
| screens[].mock/priority | Сохраняются без изменения |

build-config требует реальных test_file внутри проекта, полное покрытие overrides и testContract в sourceFiles. Verify отвергает потерю/добавление кейсов и targets, изменение критериев/fixtures/priority/route/размеров, duplicate IDs и несовпадение revision. Затем collector --dry-run проверяет формат argv/actions/keyboard/URL; dry-run не запускает тестов.

## Независимое ревью

Перед capture включи нейтральный файл и все нужные read-set источники/код/тесты в sourceFiles. После capture planner повторяет проверку контракта, сверяет source hashes и копирует исходный test-contract.json без изменения bytes/schema в immutable snapshot. UX и Parity получают эту копию; browser targets/viewports передаются отдельно из проверенной конфигурации. Сам prototype-build.md не попадает в read-set.

При ошибке соответствия Ready закрыть нельзя. Исправь конфигурацию по действующему контракту и создай новый capture/run; не сокращай контракт ради зелёного результата. Изменение самого контракта требует явного основания и новой ревизии.
