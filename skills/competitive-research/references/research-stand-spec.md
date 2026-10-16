# Research Stand: контракт и сборка

Применяй этот контракт только при выбранном формате `document+stand`. Для `document` стенд имеет статус `not-required`; stand-data, сборка и просмотр стенда не обязательны и не ограничивают PASS исследования. Если стенд уже входит в согласованный результат, недоступность средств его создания не разрешает молча сменить формат.

## Содержание

1. Источник и физические файлы
2. Схема данных
3. Сборка и ограничения проверок
4. Доставка и изменения

## 1. Источник и физические файлы

`competitive-research.md` — один аналитический отчёт. В конце него ровно один fenced-блок `stand-data` с валидным JSON. Тексты блока должны соответствовать аналитическим разделам; вручную сверяй ответы RQ, observation/interpretation, сравнение, выводы и ограничения.

Сборщик извлекает JSON из Markdown, создаёт `research-stand/stand-data.json` и `index.html`, копирует полный Markdown. Evidence находится в `research-stand/evidence/`. Стенд не требует сети для интерфейса, но изображения/документы — отдельные файлы рядом, а внешние ссылки могут требовать сеть. Отдельный JSON — производный кэш; его не редактируют.

Вкладки: Overview, Research Questions, References, Patterns, Comparison, Gaps & Opportunities, Sources. Overview показывает статус/гейт, ограничения и ссылку на полный отчёт. Предложения по изменению вводных и подробный чеклист доступны в полном Markdown.

## 2. Схема данных

Поиск по умолчанию выходит за пределы прямых конкурентов. Категории `direct`, `analogous`, `adjacent`, `unexpected` описывают направления поиска и происхождение систем, а не обязательные квоты на находки. `unexpected` включает целенаправленно найденные неочевидные паттерны из других областей. В `research_questions[].levels` укажи фактически исследованные направления; в `systems[].level` — основной тип включённой системы. Не добавляй вымышленные системы для заполнения категорий. В `overview.summary` кратко отрази фактический охват, а обоснованные ограничения — в `limitations` и полном отчёте. Нулевые находки не означают, что направление не исследовалось: фактические запросы и результаты поиска фиксируются в Markdown.

Схема ниже — описание, не готовый JSON для отчёта. Значения с вариантами заменить конкретными. Коллекции без находок — `[]`, ограничения — явный текст; причины отсутствия evidence писать по существу. Для реальной задачи не копировать вымышленные данные assets/example.

```json
{
  "meta": { "task": "slug", "title": "Название", "date": "YYYY-MM-DD",
            "status": "complete | partial | blocked", "gate": "PASS | LIMITED | FAIL", "requirements_version": 1 },

  "overview": {
    "summary": ["абзац", "абзац"],
    "key_findings": [ { "text": "...", "refs": ["PAT-01", "REF-01"] } ],
    "implications_top": ["IMP-01"]
  },

  "research_questions": [ {
    "id": "RQ-01", "question": "...", "why": "...",
    "links": ["REQ-003", "ASM-02", "OQ-04"],
    "levels": ["direct", "analogous", "adjacent", "unexpected"],
    "status": "answered | partial | open",
    "answer": "...", "patterns": ["PAT-01"]
  } ],

  "systems": [ {
    "id": "SYS-01", "name": "...", "level": "direct | analogous | adjacent | unexpected",
    "url": "https://...", "why": "почему включена",
    "access": "full | partial | docs-only | not-accessible",
    "accessed": "YYYY-MM-DD", "notes": "..."
  } ],

  "references": [ {
    "id": "REF-01", "system": "SYS-01", "title": "краткое название",
    "source": { "url": "https://...", "note": "точное место, версия/план/роль/платформа, тип источника", "accessed": "YYYY-MM-DD" },
    "evidence": [ { "type": "screenshot | doc | video", "path": "evidence/ref-01-....png", "caption": "что показано" } ],
    "evidence_missing_reason": "обязательно, если evidence пуст",
    "confidence": "high | medium | low", "confidence_reason": "что источник действительно подтверждает",
    "observation": "что наблюдается, без оценки",
    "pattern": "PAT-01",
    "interpretation": "что это может значить",
    "relevance": { "level": "high | medium | low", "rqs": ["RQ-01"], "note": "почему важно" }
  } ],

  "patterns": [ {
    "id": "PAT-01", "name": "...",
    "prevalence": "observed | common | divergent | standard | rare | emerging",
    "prevalence_basis": "n/N и границы выборки; отдельное основание для standard/rare/emerging",
    "how_it_works": "...", "advantages": "...", "tradeoffs": "...",
    "constraints": "...", "applicable": "...",
    "counterexamples": "контрпримеры или запись, что поиск их не дал",
    "refs": ["REF-01"]
  } ],

  "comparison": {
    "note": "как читать сравнение",
    "feature_matrix": {
      "systems": ["SYS-01", "SYS-02"],
      "rows": [ { "feature": "...", "req": "REQ-003", "cells": { "SYS-01": "yes", "SYS-02": "partial" } } ],
      "coverage_notes": "сопоставление с requirements.md"
    }
  },

  "gaps": [ { "id": "GAP-01", "text": "...", "evidence": ["REF-01"] } ],
  "opportunities": [ { "id": "OPP-01", "text": "...", "label": "HYPOTHESIS", "evidence": ["GAP-01"] } ],
  "risks": [ { "id": "RSK-01", "text": "...", "type": "constraint | risk", "evidence": ["PAT-01"] } ],
  "implications": [ { "id": "IMP-01", "text": "...", "strength": "strong | moderate | info",
                      "links": ["REQ-003", "OQ-02"], "evidence": ["PAT-01"] } ],
  "limitations": ["..."]
}
```

Все IDs: PREFIX-NN или PREFIX-NNN. Поддерживаются RQ, SYS, REF, PAT, GAP, OPP, RSK, IMP. У REF может быть один основной PAT; если обобщение пока невозможно, pattern можно опустить, а причину описать в interpretation. Дополнительные связи опиши там же. Предварительный паттерн обозначай observed, а не рыночной закономерностью.

Обязательные верхние поля: meta, overview, research_questions, systems, references, patterns. Остальные коллекции могут быть пусты. Каждый IMP имеет links (TASK или внешний ID) и evidence; GAP/OPP — evidence. Ссылки между PAT и REF должны совпадать. Уверенность high/medium/low сопровождается confidence_reason.

- `observed`: есть пример, распространённость не установлена.
- `common`: повторяется минимум в двух независимых системах выбранной выборки; это не стандарт рынка.
- `divergent`: наблюдались разные подходы.
- `standard`, `rare`, `emerging`: требуется prevalence_basis с соответствующим внешним/временным/выборочным основанием. Сам сборщик не проверяет истинность основания.

Для каждого паттерна добавь `sample`: например `2 из 4 доступных релевантных независимых систем`. Число REF не заменяет число систем.

У REF `source.url` — абсолютный HTTP(S) URL либо `source.note` — точный локальный источник. `source.accessed` — реальная дата YYYY-MM-DD. Условия, версия и место могут быть в source.note. У evidence допустим относительный POSIX-путь только внутри `evidence/`; абсолютные пути, `..` и выход через symlink запрещены. У screenshot обязательна caption. Учебные SVG допустимы только в демо, не как доказательство реального продукта.

Матрица необязательна. Ячейки yes / partial / no / unknown; если её нет — comparison `{}`. Для значимых ячеек добавь текстовые `cell_notes` с основанием и ограничениями; общий coverage_notes не заменяет доказательство отрицательного значения. Факт наличия только в части планов — partial с пояснением, не глобальное yes/no.

Если входного requirements.md нет, links = ["TASK"], а requirements_version не указывается. При наличии укажи версию и путь в метаданных/отчёте; не связывай ID с документом другой задачи. meta.status — complete/partial/blocked (завершение работы), meta.gate — результат качества. Это не автоматическое продуктовое согласование.

## 3. Сборка и ограничения проверок

Python 3.8+, стандартная библиотека. Основной способ:

```bash
python3 <skill-dir>/scripts/build_stand.py \
  --md work/<task-slug>/competitive-research.md \
  --out work/<task-slug>/research-stand
```

Evidence должен уже находиться в `research-stand/evidence/` рядом с исходным отчётом. --out может копировать стенд и evidence в другую папку. Не направлять туда файлы другой задачи.

Необязательный `--requirements <путь>` проверяет внешние ссылки REQ/ASM/OQ на присутствие в явно переданном Markdown. Без него проверка внешнего контракта ручная, это не препятствие самостоятельному запуску.

Сборщик проверяет типы основных полей, формат и уникальность ID, внутренние ссылки, даты/URL/пути, наличие evidence, основные поля карточек и паттернов, согласованность связей REF/PAT. Требует отдельное основание для standard/rare/emerging. Если одновременно передан --data, содержимое должно точно совпасть с каноническим блоком Markdown.

Сверка ID с Markdown не доказывает смысловую идентичность видимого текста и JSON-блока. Сборщик также не подтверждает достоверность наблюдений, полноту выборки, эффективность паттерна, истинность prevalence_basis или качество гейта: это проверки автора.

Коды: 0 — сборка выполнена; 1 — ошибки валидации или предупреждения при --strict; 2 — некорректный вход/ошибка файлов/сборки. --strict пригоден для контрольной сборки; предупреждения не устранять выдуманными данными.

Учебная сборка без Markdown:

```bash
python3 <skill-dir>/scripts/build_stand.py \
  --data <skill-dir>/assets/example/stand-data.json \
  --out <рабочая-папка>/stand-demo
```

Здесь системы и SVG вымышлены, meta.synthetic=true. Это проверка интерфейса и схемы, не образец исследования рынка.

## 4. Доставка и изменения

Открыть index.html локально или запустить из папки стенда `python3 -m http.server 8000 --bind 127.0.0.1`; назвать адрес только после фактического запуска. Для выдачи через чат/другой компьютер упаковать всю папку с evidence и полный Markdown, а не ссылку на чужой localhost.

После правки Markdown обновить его stand-data-блок, сверить смысл и пересобрать. Перед финальной сборкой обновить гейт/ограничения. Не править JSON/HTML вручную. Проверить вкладки, изображения, фильтры, переходы по ID, сравнение и клавиатуру; отсутствие браузерной проверки обозначить.
