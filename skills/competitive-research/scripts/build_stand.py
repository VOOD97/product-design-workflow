#!/usr/bin/env python3
"""Сборка Research Stand из блока stand-data в Markdown (JSON для учебного примера).

Что делает:
1. Проверяет структуру и ссылочную целостность stand-data.json.
2. Извлекает канонический JSON из stand-data в Markdown; сверяет наборы ID.
   Смысловая сверка текста отчёта и блока остаётся обязанностью автора.
3. Проверяет, что файлы evidence существуют (или указана причина их отсутствия).
4. Встраивает данные в research-stand-template.html и пишет index.html.

Только стандартная библиотека Python 3.8+.

Пример:
    python3 build_stand.py \
        --data work/my-task/research-stand/stand-data.json \
        --md work/my-task/competitive-research.md

Код возврата: 0 если ошибок нет, 1 если есть ошибки валидации, 2 при проблемах с аргументами.
"""
import argparse
import datetime
from urllib.parse import urlsplit
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = HERE.parent / "assets" / "research-stand-template.html"

COLLECTIONS = {
    "research_questions": "RQ",
    "systems": "SYS",
    "references": "REF",
    "patterns": "PAT",
    "gaps": "GAP",
    "opportunities": "OPP",
    "risks": "RSK",
    "implications": "IMP",
}
ID_RE = re.compile(r"^(RQ|SYS|REF|PAT|GAP|OPP|RSK|IMP)-\d{2,3}$")
MD_ID_RE = re.compile(r"\b(RQ|SYS|REF|PAT|GAP|OPP|RSK|IMP)-\d{2,3}\b")
PREVALENCE = {"observed", "standard", "common", "divergent", "rare", "emerging"}
LEVELS = {"direct", "analogous", "adjacent", "unexpected"}
ACCESS = {"full", "partial", "docs-only", "not-accessible"}
RQ_STATUS = {"answered", "partial", "open"}
REL_LEVEL = {"high", "medium", "low"}
STRENGTH = {"strong", "moderate", "info"}
CELL_VALUES = {"yes", "partial", "no", "unknown"}
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")


def nonempty(value):
    return isinstance(value, str) and value.strip() != ""


def safe_evidence(base_dir, value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("evidence.path должен быть относительным POSIX-путём")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "evidence":
        raise ValueError("evidence.path должен находиться внутри evidence/")
    resolved = (base_dir / path).resolve()
    try:
        resolved.relative_to(base_dir.resolve())
    except ValueError:
        raise ValueError("evidence.path выходит за папку стенда, включая symlink")
    return resolved


def validate_shape(data, base_dir):
    errors = []
    if not isinstance(data, dict):
        return ["Корень JSON должен быть объектом"]
    for key in ("meta", "overview", "comparison"):
        if key in data and not isinstance(data[key], dict):
            errors.append(f"{key} должен быть объектом")
    for key in COLLECTIONS:
        if not isinstance(data.get(key, []), list):
            errors.append(f"{key} должен быть массивом")
        elif any(not isinstance(x, dict) for x in data.get(key, [])):
            errors.append(f"{key}: элементы должны быть объектами")
    if errors:
        return errors

    array_fields = {"links", "levels", "patterns", "refs", "rqs", "implications_top", "summary", "limitations", "systems"}
    scalar_fields = {"id", "title", "name", "question", "answer", "why", "status", "level", "access", "url", "note", "notes", "accessed", "date", "observation", "interpretation", "pattern", "confidence", "confidence_reason", "path", "caption", "type", "prevalence", "prevalence_basis", "sample", "how_it_works", "advantages", "tradeoffs", "constraints", "applicable", "counterexamples", "text", "strength", "label", "feature", "req", "coverage_notes", "evidence_missing_reason"}
    def walk(obj, where="root"):
        if isinstance(obj, dict):
            for key, value in obj.items():
                loc = where + "." + key
                if key in scalar_fields and not isinstance(value, str):
                    errors.append(f"{loc}: ожидается строка")
                if key in array_fields and (not isinstance(value, list) or any(not isinstance(x, str) for x in value)):
                    errors.append(f"{loc}: ожидается массив строк")
                if key in {"source", "relevance", "feature_matrix", "cells"} and not isinstance(value, dict):
                    errors.append(f"{loc}: ожидается объект")
                if key in {"evidence", "key_findings", "rows"} and not isinstance(value, list):
                    errors.append(f"{loc}: ожидается массив")
                if key in {"accessed", "date"} and value:
                    try:
                        datetime.date.fromisoformat(value)
                    except (TypeError, ValueError):
                        errors.append(f"{loc}: ожидается реальная дата YYYY-MM-DD")
                if key == "url" and value:
                    if not isinstance(value, str) or urlsplit(value).scheme not in {"https", "http"} or not urlsplit(value).netloc:
                        errors.append(f"{loc}: допустим только абсолютный HTTP(S) URL")
                if key == "path":
                    try:
                        safe_evidence(base_dir, value)
                    except ValueError as exc:
                        errors.append(f"{loc}: {exc}")
                walk(value, loc)
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, f"{where}[{index}]")
    # collections.systems содержит объекты, не строки.
    for key, value in data.items():
        if key in COLLECTIONS:
            for index, item in enumerate(value):
                walk(item, f"{key}[{index}]")
        elif key == "limitations":
            if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
                errors.append("limitations должен быть массивом строк")
        else:
            walk(value, key)
    for r in data.get("references", []):
        for e in r.get("evidence", []) if isinstance(r.get("evidence", []), list) else []:
            if not isinstance(e, dict):
                errors.append(f"{r.get('id')}: evidence должен содержать объекты")
    for key in ("gaps", "opportunities", "risks", "implications"):
        for item in data.get(key, []):
            if any(not isinstance(x, str) for x in item.get("evidence", []) if isinstance(item.get("evidence", []), list)):
                errors.append(f"{item.get('id')}: evidence должен содержать ID-строки")
    return errors


def validate(data, base_dir):
    """Возвращает (errors, warnings)."""
    errors, warnings = validate_shape(data, base_dir), []
    if errors:
        return errors, warnings

    def err(msg):
        errors.append(msg)

    def warn(msg):
        warnings.append(msg)

    for key in ("meta", "overview", "research_questions", "systems", "references", "patterns"):
        if key not in data:
            err(f"Нет обязательного ключа верхнего уровня: {key}")
    if errors:
        return errors, warnings

    meta = data["meta"]
    if meta.get("status") not in {"complete", "partial", "blocked"}:
        err("meta.status должен быть complete, partial или blocked")
    gates = {"PASS", "LIMITED", "FAIL"}
    if meta.get("synthetic") is True:
        gates.add("DEMO")
    if meta.get("gate") not in gates:
        err("meta.gate должен содержать явный результат гейта")

    ids = {}
    for coll, prefix in COLLECTIONS.items():
        for i, item in enumerate(data.get(coll, [])):
            item_id = item.get("id", "")
            where = f"{coll}[{i}]"
            if not ID_RE.match(item_id or ""):
                err(f"{where}: некорректный id '{item_id}' (ожидается {prefix}-NN)")
                continue
            if not item_id.startswith(prefix + "-"):
                err(f"{where}: id '{item_id}' должен начинаться с {prefix}-")
            if item_id in ids:
                err(f"Дубликат id: {item_id}")
            ids[item_id] = coll

    def exists(ref_id, prefixes, where):
        if ref_id not in ids:
            err(f"{where}: ссылка на несуществующий id {ref_id}")
        elif prefixes and ref_id.split("-")[0] not in prefixes:
            err(f"{where}: {ref_id} должен быть одним из типов {sorted(prefixes)}")

    # Research questions
    for q in data["research_questions"]:
        w = q.get("id", "RQ?")
        if not nonempty(q.get("question")):
            err(f"{w}: пустой question")
        if q.get("status") not in RQ_STATUS:
            err(f"{w}: status должен быть одним из {sorted(RQ_STATUS)}")
        if not q.get("links"):
            warn(f"{w}: нет связи с требованиями или с задачей (links; без requirements.md укажите TASK)")
        for lv in q.get("levels", []):
            if lv not in LEVELS:
                err(f"{w}: неизвестный уровень поиска '{lv}'")
        for p in q.get("patterns", []):
            exists(p, {"PAT"}, w)
        if q.get("status") in ("answered", "partial") and not (q.get("patterns") or nonempty(q.get("answer"))):
            err(f"{w}: отвечен или частично отвечен, но нет ни answer, ни patterns")
        if q.get("status") == "open" and not nonempty(q.get("answer")):
            warn(f"{w}: открытый вопрос без пояснения, почему он остался открытым (поле answer)")

    # Systems
    for s in data["systems"]:
        w = s.get("id", "SYS?")
        if not nonempty(s.get("name")):
            err(f"{w}: пустой name")
        if s.get("level") not in LEVELS:
            err(f"{w}: level должен быть одним из {sorted(LEVELS)}")
        if s.get("access") not in ACCESS:
            err(f"{w}: access должен быть одним из {sorted(ACCESS)}")
        if not nonempty(s.get("why")):
            err(f"{w}: не указано, почему система включена (why)")

    # References
    ref_by_pattern = {}
    for r in data["references"]:
        w = r.get("id", "REF?")
        exists(r.get("system", ""), {"SYS"}, w)
        src = r.get("source") or {}
        if not (nonempty(src.get("url")) or nonempty(src.get("note"))):
            err(f"{w}: нет source (url или note)")
        if not nonempty(src.get("accessed")):
            err(f"{w}: нет даты просмотра source.accessed")
        for field in ("observation", "interpretation"):
            if not nonempty(r.get(field)):
                err(f"{w}: пустое поле {field}")
        if nonempty(r.get("observation")) and nonempty(r.get("interpretation")) \
                and r["observation"].strip() == r["interpretation"].strip():
            err(f"{w}: observation и interpretation совпадают, их нужно разделить")
        if r.get("pattern"):
            exists(r["pattern"], {"PAT"}, w)
        ref_by_pattern.setdefault(r.get("pattern"), []).append(w)
        if r.get("confidence") not in {"high", "medium", "low"} or not nonempty(r.get("confidence_reason")):
            err(f"{w}: confidence high/medium/low и confidence_reason обязательны")
        rel = r.get("relevance") or {}
        if rel.get("level") not in REL_LEVEL:
            err(f"{w}: relevance.level должен быть одним из {sorted(REL_LEVEL)}")
        if not nonempty(rel.get("note")):
            err(f"{w}: relevance.note пустой")
        for q in rel.get("rqs", []):
            exists(q, {"RQ"}, w)
        evidence = r.get("evidence") or []
        if not evidence and not nonempty(r.get("evidence_missing_reason")):
            err(f"{w}: нет evidence и не указана evidence_missing_reason")
        for e in evidence:
            path = e.get("path", "")
            if not path:
                err(f"{w}: у evidence нет path")
                continue
            if not safe_evidence(base_dir, path).is_file():
                err(f"{w}: файл evidence не найден: {path}")
            if path.lower().endswith(IMAGE_EXT) and not nonempty(e.get("caption")):
                err(f"{w}: у скриншота {path} нет caption (он нужен как alt-текст)")

    # Patterns
    for p in data["patterns"]:
        w = p.get("id", "PAT?")
        if p.get("prevalence") not in PREVALENCE:
            err(f"{w}: prevalence должен быть одним из {sorted(PREVALENCE)}")
        for field in ("name", "how_it_works", "tradeoffs", "constraints", "sample"):
            if not nonempty(p.get(field)):
                err(f"{w}: пустое поле {field}")
        if not p.get("refs"):
            err(f"{w}: паттерн без ссылок на references")
        for r in p.get("refs", []):
            exists(r, {"REF"}, w)
        systems = {r.get("system") for r in data["references"] if r.get("id") in p.get("refs", [])}
        if p.get("prevalence") == "common" and len(systems) < 2:
            err(f"{w}: common требует минимум двух независимых систем в выборке")
        if p.get("prevalence") in {"standard", "emerging", "rare"} and not nonempty(p.get("prevalence_basis")):
            err(f"{w}: {p.get('prevalence')} требует отдельного prevalence_basis")
        if p.get("prevalence") in {"standard", "common"} and not nonempty(p.get("counterexamples")):
            warn(f"{w}: нет контрпримеров или описания их поиска")

    for p in data["patterns"]:
        for r in p.get("refs", []):
            ref = next((x for x in data["references"] if x.get("id") == r), None)
            if ref and ref.get("pattern") != p.get("id"):
                err(f"{p['id']}: ссылается на {r}, но у {r} указан другой pattern ({ref.get('pattern')})")

    # Gaps / opportunities / risks / implications
    for g in data.get("gaps", []):
        if not g.get("evidence"):
            err(f"{g.get('id')}: gap без evidence")
        for e in g.get("evidence", []):
            exists(e, {"REF", "PAT", "SYS"}, g.get("id", "GAP?"))
    for o in data.get("opportunities", []):
        if o.get("label", "HYPOTHESIS") != "HYPOTHESIS":
            err(f"{o.get('id')}: opportunity должна иметь метку HYPOTHESIS")
        if not o.get("evidence"):
            err(f"{o.get('id')}: opportunity без evidence")
        for e in o.get("evidence", []):
            exists(e, {"REF", "PAT", "GAP"}, o.get("id", "OPP?"))
    for r in data.get("risks", []):
        for e in r.get("evidence", []):
            exists(e, {"REF", "PAT", "SYS"}, r.get("id", "RSK?"))
    for i in data.get("implications", []):
        w = i.get("id", "IMP?")
        if i.get("strength") not in STRENGTH:
            err(f"{w}: strength должен быть одним из {sorted(STRENGTH)}")
        if not (i.get("links") and i.get("evidence")):
            err(f"{w}: вывод не привязан к задаче (links: TASK или внешний ID) и находкам (evidence) одновременно")
        for e in i.get("evidence", []):
            exists(e, {"REF", "PAT", "GAP", "OPP", "RSK"}, w)

    overview = data.get("overview", {})
    for f in overview.get("key_findings", []):
        for r in f.get("refs", []):
            exists(r, None, "overview.key_findings")
    for i in overview.get("implications_top", []):
        exists(i, {"IMP"}, "overview.implications_top")

    # Feature matrix
    fm = (data.get("comparison") or {}).get("feature_matrix")
    if fm:
        for s in fm.get("systems", []):
            exists(s, {"SYS"}, "feature_matrix")
        for row in fm.get("rows", []):
            for sid, val in (row.get("cells") or {}).items():
                if sid not in fm.get("systems", []):
                    err(f"feature_matrix: колонка {sid} не объявлена в systems")
                if not isinstance(val, str) or val not in CELL_VALUES:
                    err(f"feature_matrix: значение '{val}' не из {sorted(CELL_VALUES)}")

    # Покрытие уровней
    used_levels = {s.get("level") for s in data["systems"]}
    if used_levels == {"direct"}:
        warn("В исследовании только прямые конкуренты. Если аналоги не нужны, объясните это в limitations")
    unreferenced = [s["id"] for s in data["systems"]
                    if s["id"] not in {r.get("system") for r in data["references"]}
                    and s.get("access") != "not-accessible"]
    if unreferenced:
        warn("Системы без единого reference: " + ", ".join(unreferenced))
    return errors, warnings


def extract_markdown(md_path):
    text = md_path.read_text(encoding="utf-8")
    blocks = re.findall(r"^```stand-data\s*\n(.*?)^```\s*$", text, re.M | re.S)
    if len(blocks) != 1:
        raise ValueError("Markdown должен содержать ровно один fenced-блок stand-data")
    return json.loads(blocks[0])


def check_markdown(data, md_path):
    """Сверка ID между competitive-research.md и stand-data.json."""
    errors = []
    text = md_path.read_text(encoding="utf-8")
    md_ids = {m.group(0) for m in MD_ID_RE.finditer(text)}
    json_ids = set()
    for coll in COLLECTIONS:
        for item in data.get(coll, []):
            if item.get("id"):
                json_ids.add(item["id"])
    only_json = sorted(json_ids - md_ids)
    only_md = sorted(md_ids - json_ids)
    if only_json:
        errors.append("ID есть в stand-data.json, но нет в competitive-research.md: " + ", ".join(only_json))
    if only_md:
        errors.append("ID есть в competitive-research.md, но нет в stand-data.json: " + ", ".join(only_md))
    return errors


def build(data, template_path, out_dir):
    template = template_path.read_text(encoding="utf-8")
    if "__STAND_DATA__" not in template:
        raise SystemExit(f"В шаблоне нет плейсхолдера __STAND_DATA__: {template_path}")
    payload = json.dumps(data, ensure_ascii=False)
    # защита от преждевременного закрытия тега script и от U+2028/2029
    payload = (payload.replace("</", "<\\/").replace("<!--", "<\\!--")
               .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
    html = template.replace("__STAND_DATA__", payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Сборка Research Stand из stand-data.json")
    ap.add_argument("--data", help="JSON для учебного примера; вместе с --md должен точно совпадать с блоком")
    ap.add_argument("--md", help="источник: competitive-research.md с блоком stand-data")
    ap.add_argument("--requirements", help="необязательный исходный Markdown для проверки внешних REQ/ASM/OQ ссылок")
    ap.add_argument("--out", help="папка стенда (по умолчанию папка с stand-data.json)")
    ap.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="путь к HTML-шаблону")
    ap.add_argument("--strict", action="store_true", help="считать предупреждения ошибками")
    args = ap.parse_args(argv)

    if not args.md and not args.data:
        ap.error("нужен --md (реальный отчёт) или --data (учебный пример)")
    try:
        md_path = Path(args.md).resolve() if args.md else None
        data_path = Path(args.data).resolve() if args.data else None
        if md_path:
            data = extract_markdown(md_path)
            if data_path and json.loads(data_path.read_text(encoding="utf-8")) != data:
                raise ValueError("--data отличается от канонического stand-data в Markdown")
            base_dir = md_path.parent / "research-stand"
        else:
            data = json.loads(data_path.read_text(encoding="utf-8"))
            base_dir = data_path.parent
        out_dir = Path(args.out).resolve() if args.out else base_dir.resolve()
        errors, warnings = validate(data, base_dir)
        if md_path and not errors:
            errors += check_markdown(data, md_path)
        if args.requirements and not errors:
            req_text = Path(args.requirements).read_text(encoding="utf-8")
            req_ids = set(re.findall(r"\b(?:REQ|ASM|OQ)-\d+\b", req_text))
            for coll in ("research_questions", "implications"):
                for item in data.get(coll, []):
                    for link in item.get("links", []):
                        if link != "TASK" and link not in req_ids:
                            errors.append(f"{item.get('id')}: внешний ID {link} отсутствует во входном документе")
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
        print(f"Ошибка входных данных: {exc}", file=sys.stderr)
        return 2

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors or (args.strict and warnings):
        print(f"\nСтенд не собран: ошибок {len(errors)}, предупреждений {len(warnings)}.")
        return 1

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        if out_dir != base_dir.resolve():
            for r in data["references"]:
                for e in r.get("evidence", []):
                    src = safe_evidence(base_dir, e["path"])
                    dst = safe_evidence(out_dir, e["path"])
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
        (out_dir / "stand-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if md_path:
            target_md = out_dir / "competitive-research.md"
            if target_md.resolve() != md_path.resolve():
                shutil.copy2(md_path, target_md)
        out = build(data, Path(args.template), out_dir)
    except (OSError, ValueError) as exc:
        print(f"Ошибка сборки: {exc}", file=sys.stderr)
        return 2

    print(f"Готово: {out}")
    print(f"Предупреждений: {len(warnings)}. Открыть: файл index.html в браузере "
          f"или `python3 -m http.server --bind 127.0.0.1` в папке {out_dir}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
