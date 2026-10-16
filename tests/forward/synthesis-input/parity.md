# Учебный parity report
What works well: сообщение ошибки видно.
```review-data
{"report_type": "parity", "run_id": "synthetic-run", "revision": "synthetic-rev", "capture_sha256": "synthetic-capture", "status": "partial", "findings": [{"id": "PAR-001", "severity": "High", "layer": "implementation", "location": "UI-001 / empty email", "heuristic": "N/A", "observation": "Submit активен при пустом Email.", "impact": "Принятое условие доступности не сохранено.", "evidence": ["observations.md, Submit active"], "source": ["ui-spec.md: отправка недоступна при пустом email"], "verify": "Открыть пустую форму.", "status": "open", "confidence": "medium", "limits": "Код и реальные тесты не предоставлены; parity с кодом не проверена."}], "works_well": ["Ошибка явно показана, по учебному observations."], "checks": ["Статические учебные материалы"], "limitations": ["Нет реального браузерного evidence."]}
```
