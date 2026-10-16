# Визуальная методика и browser probes

## Последовательность

Основная работа и приоритет действия → композиция/группы → компоненты/states → typography/spacing/color → responsive stress. Не заполняй список мелких расстояний, пока не ясно, доступно ли главное действие. Product completeness находку можно описать и передать по layer, не подменяя ею весь visual review.

## Матрица областей

| Область | Вопросы | Playwright probe | Evidence |
|---|---|---|---|
| Иерархия | Где задача/главный результат/CTA? Не конкурируют ли статусы и служебные действия? | Открыть default и busy/data-rich state, сравнить видимый приоритет | Screenshot одинакового viewport с названным нарушением |
| Группировка | Понятна ли связь label/value/action? Не воспринимаются ли несвязанные элементы как одна группа? | Переключить релевантный tab/section/selection, проверить постоянство контекста | Before/after, observed effect, источник layout rule |
| Компоненты | Сохранились ли принятые variants и meanings? Различимы ли disabled/processing/error/selected? | Hover/focus/select/submit на test fixture, осмотреть реальный state | Состояния control и reference из принятой DS |
| Typography | Читаются ли длинные значения/числа? Не скрывается ли критичный текст? | Realistic long fixture, scroll/expand, narrow viewport | Clipping/wrapping и доступность полного значения |
| Spacing/alignment | Нарушение мешает прочитать связь или нарушает конкретный canon? | Сопоставить похожие поля/строки при тех же данных | Пара конкретных фрагментов; при нужде DOM bounding boxes |
| Цвет/акцент | Один смысл выражен последовательно? Акцент не скрывает опасность/ошибку? | Toggle state/theme только если scope, сравнить non-color cues | Значимый semantic distinction, DS rule |
| Responsive | Доступны ли content и actions на заявленной ширине? Overlay/sticky не перекрывает управление? | setViewportSize, scroll, open dialog/dropdown/tooltip | Размер viewport, before/after, overlap screenshot |
| Pressure | Длинный текст, zero/many records, unusual valid values не ломают layout? | Только предусмотренные synthetic fixtures, не random data | Dataset name/seed, screenshot, конкретный потерянный control |

## Контроль сравнения

Одинаковы должны быть UI state, dataset, viewport, theme, scale и browser условия. Сравнение разных states может выявить inconsistency, но не pixel parity. На первом прогоне нет принятого visual baseline: не создавать его автоматически.

Если нужна geometry diagnosis, читать rendered DOM bounding boxes/computed styles разрешено: это наблюдение результата. Читать продуктовый исходный CSS/компоненты вне read-set не нужно; источник нормативного значения — выбранный DS/reference. Не исправлять CSS в DevTools для иллюстрации желаемого решения.

Открой реальные screenshots, увеличь значимый фрагмент и сопоставь с источником. Не выдумывай измерения расстояний/контраста «на глаз»; если измерение не выполнено, описывай только наблюдаемое отличие. Для screenshot diff контролируй OS/fonts/browser; шум rasterization не объявлять дефектом.

## Подтверждение и ложные срабатывания

- Намеренная согласованная плотность не визуальный дефект без конкретного нарушения.
- Урезанный viewport screenshot не доказывает, что content недоступен после scroll; реально прокрути и проверь действие.
- Text overflow может быть допустимым, если существенное значение доступно в принятом interaction; проверь expand/tooltip и input alternatives.
- Отличие от произвольного external reference не нарушает canon нашего продукта.
- CSS pixel-perfect mismatch без принятого источника — наблюдение/вопрос, не Must fix.

Finding связывает реальный screen×state, источник, observed visual effect и пользовательское последствие. Что работает хорошо также имеет конкретный reference/evidence; preserve защищает иерархию и согласованные варианты от случайного редизайна.
