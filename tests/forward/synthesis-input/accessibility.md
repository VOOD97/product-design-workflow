# Учебный accessibility report
What works well: сообщение ошибки видно.
```review-data
{"report_type": "accessibility", "run_id": "synthetic-run", "revision": "synthetic-rev", "capture_sha256": "synthetic-capture", "status": "partial", "findings": [{"id": "A11Y-001", "severity": "High", "layer": "ui", "location": "UI-001 / invalid email", "heuristic": "N/A", "observation": "Фокус после ошибки остаётся на Submit.", "impact": "Пользователь должен самостоятельно искать ошибочное поле.", "evidence": ["observations.md, строка UI-001"], "source": ["ui-spec.md: фокус на Email после validation error"], "verify": "Пустая отправка, проверить active element.", "status": "open", "confidence": "medium", "limits": "Учебное наблюдение; browser не запускался."}], "works_well": ["Ошибка явно показана, по учебному observations."], "checks": ["Статические учебные материалы"], "limitations": ["Нет реального браузерного evidence."]}
```
