#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_pack.py — собирает «упаковку» проекта для передачи в чат с ИИ.

Запуск:  python service/docs/ai_pack.py   (из любой папки проекта)
Выход:   project_info/ai_pack/ в корне проекта (корень ищется по .git)

Что создаётся:
  OVERVIEW.md          — карта проекта:
                         • структура + сигнатуры функций и классов
                         • ВСТРОЕННЫЕ документы (AI_BRIEF, DIGEST, QWEN,
                           ARCHITECTURE, TODO) — содержимым целиком
                         • список документов, которые «попроси отдельно»
                           (README, README_en, CHANGELOG, DEVLOG, USER_MANUAL)
                         • manifest упаковки и состояние git
  CODE_part1.md        — код (сквозная нарезка по 500 КБ)
  CODE_part2.md        — продолжение
  ...
  CONFIG_TEMPLATES.md  — только конфиги (без шаблонов/справочников/генераторов)

Игнорируются целиком: .git, __pycache__, venv, data/, uploads/, exports/,
personal/, transfer/, _old_v2/, ai_pack/, dist*/, SonologData/,
Резервные копии_SonologData/ и т.п.; списки имён ограничены.

Из CONFIG_TEMPLATES.md исключаются:
  • templates/*.txt, references/*.json, assets/* — это данные, не конфиги;
  • make_docs.py, create_project_docs.py, create_user_manual.py — их содержимое
    дублирует уже сгенерированные *.md, а код и так есть в CODE_partN.md.
"""
from __future__ import annotations

import ast
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Iterable

# ================================================================
# НАСТРОЙКИ
# ================================================================
def _find_root(start: Path) -> Path:
    """Корень проекта: ближайший предок с .git; иначе папка скрипта."""
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return start.parent


BASE_DIR = _find_root(Path(__file__).resolve())
OUT_DIR = BASE_DIR / "project_info" / "ai_pack"

# Папки, которые не трогаем целиком
IGNORE_DIRS = {
    ".git", ".github", "__pycache__", ".pytest_cache", ".mypy_cache",
    "dist", "build", "venv", ".venv", "env", ".env",
    ".idea", ".vscode", "node_modules",
    "data", "var", "uploads", "exports", "qr_static", "personal",
    "transfer", "_old_v2", "ai_pack", "_project_dump",
    "SonologData",
    "Резервные копии_SonologData",
    "backup_SonologData",
}
IGNORE_GLOB_DIRS = [
    "templates_backup_*", "backup_*", "restore_my",
    "dist_до_*", "dist_*",               # старые сборки
]
IGNORE_FILES = {
    ".DS_Store", "Thumbs.db",
}
IGNORE_GLOBS = ["*.pyc", "*.pyo", "*.log", "*.tmp",
                "*.db", "*.sqlite", "*.sqlite3",
                "*legacy_dump*", "*legacy_backup*", "*.gz"]

# Файлы, которые не включаем в CONFIG_TEMPLATES.md (шум/дубли/данные).
# В CODE_partN.md они остаются — это код.
CONFIG_SKIP_NAMES = {
    "make_docs.py",           # генератор документации — дублирует *.md
    "create_project_docs.py",
    "create_user_manual.py",
    "research_reference.json",  # данные, а не конфиг
    "USER_MANUAL.pdf",
    "USER_MANUAL.docx",
    "Sonolog_Manual.docx",
    "Sonolog_Manual.pdf",
}
# Папки, содержимое которых не идёт в CONFIG_TEMPLATES.md (данные, не конфиги).
CONFIG_SKIP_DIRS = {"templates", "references", "assets"}

# Документы, которые ВСТРАИВАЮТСЯ в OVERVIEW.md целиком (содержимым).
# Порядок важен: сначала правила игры, потом суть, потом архитектура и задачи.
EMBED_IN_OVERVIEW = [
    ("AI_BRIEF.md", "правила игры и табу"),
    ("DIGEST.md", "короткая выжимка"),
    ("QWEN.md", "стиль работы с проектом"),
    ("ARCHITECTURE.md", "схема БД, потоки данных, роли"),
    ("TODO.md", "открытые задачи"),
]

# Документы, которые только упоминаются в OVERVIEW.md как «попроси отдельно».
# Их содержимое в OVERVIEW.md НЕ встраивается.
REFER_IN_OVERVIEW = [
    ("README.md", "общее описание проекта"),
    ("README_en.md", "общее описание (en)"),
    ("CHANGELOG.md", "история версий"),
    ("DEVLOG.md", "журнал сессий (что пробовали и откатили)"),
    ("project_info/manuals/USER_MANUAL.md", "инструкция пользователя"),
]

# Расширения, которые включаем в CODE_*.md (текстовые исходники)
CODE_EXTS = {".py"}
CODE_SPECIAL = {".bat", ".sh", ".spec", ".html", ".css", ".js"}
# Расширения, которые включаем в CONFIG_TEMPLATES.md
CONFIG_EXTS = {".json", ".ini", ".cfg", ".toml", ".yaml", ".yml", ".bat", ".spec", ".sql", ".env"}
# Отдельно — файлы вида .env.example, .env.local
CONFIG_NAME_PREFIXES = (".env",)
TEMPLATE_EXTS = {".txt", ".md"}
# Бинарные — только имена, без содержимого, и с лимитом списка
BINARY_EXTS = {".docx", ".doc", ".xlsx", ".xls", ".xlsm", ".pdf", ".png", ".jpg",
               ".jpeg", ".ico", ".gif", ".webp", ".svg", ".zip", ".7z", ".rar",
               ".exe", ".dll", ".so", ".pptx"}

# Лимиты
MAX_OUTPUT_FILE_BYTES = 500 * 1024       # 500 КБ — дробить на части
MAX_SOURCE_FILE_BYTES = 200 * 1024       # 200 КБ — обрезать один файл
MAX_FILES_PER_TREE_DIR = 15              # в дереве больше — «... ещё N ...»
TREE_PREVIEW_HEAD = 5                    # показываем столько первых
TREE_PREVIEW_TAIL = 2                    # и столько последних
TEMPLATE_SAMPLES_PER_GROUP = 3           # образцов содержимого на семейство .txt/.md
MAX_LISTED_NAMES = 30                    # максимум имён в любом списке-перечислении
MAX_CLASS_METHODS = 40                   # максимум методов класса в OVERVIEW.md
MAX_SIG_LEN = 120                        # максимум длины сигнатуры функции

# Секреты, которые вырезаем из конфигов
SECRET_KEY_PATTERNS = [
    # JSON: "password": "value"
    re.compile(
        r'("(?:password|passwd|pwd|token|secret|api_key|apikey)"\s*:\s*")([^"]+)(")',
        re.I,
    ),
    # KEY=value — только в начале строки, значение непустое и не пересекает \n
    re.compile(
        r'^([ \t]*(?:password|passwd|pwd|token|secret|api_key|apikey)\s*=\s*)(\S[^\n]*)',
        re.I | re.M,
    ),
]

LANG_MAP = {"py": "python", "html": "html", "css": "css", "js": "javascript",
            "bat": "bat", "sh": "bash", "spec": "python",
            "json": "json", "ini": "ini", "toml": "toml",
            "yaml": "yaml", "yml": "yaml", "cfg": "ini", "sql": "sql",
            "env": "ini"}


# ================================================================
# УТИЛИТЫ
# ================================================================
def is_ignored_dir(path: Path) -> bool:
    name = path.name
    if name in IGNORE_DIRS:
        return True
    for pat in IGNORE_GLOB_DIRS:
        if path.match(pat):
            return True
    return False


def is_ignored_file(path: Path) -> bool:
    if path.name in IGNORE_FILES:
        return True
    for pat in IGNORE_GLOBS:
        if path.match(pat):
            return True
    return False


def _under_ignored(path: Path, root: Path) -> bool:
    """Лежит ли файл внутри игнорируемой подпапки."""
    parts = path.relative_to(root).parts
    for i in range(1, len(parts)):
        if is_ignored_dir(root / Path(*parts[:i])):
            return True
    return False


def iter_project_files(root: Path) -> Iterable[Path]:
    """Все файлы проекта, кроме игнорируемых."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(root).parts
        skip = False
        for i in range(1, len(parts)):
            if is_ignored_dir(root / Path(*parts[:i])):
                skip = True
                break
        if skip:
            continue
        if is_ignored_file(path):
            continue
        yield path


def human_size(n: int) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "Б" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} ТБ"


def read_text_safe(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="cp1251")
        except Exception:
            return None
    except Exception:
        return None


def mask_secrets(text: str) -> str:
    for pat in SECRET_KEY_PATTERNS:
        text = pat.sub(
            lambda m: m.group(1) + "***" + (m.group(3) if m.lastindex >= 3 else ""),
            text,
        )
    return text


def _short(s: str, limit: int = 60) -> str:
    s = " ".join(s.split())
    return s if len(s) <= limit else s[: limit - 1] + "…"


# ================================================================
# AST: сигнатуры функций и классов
# ================================================================
def _annotation(node) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _func_info(node) -> dict:
    """Собирает сигнатуру и docstring функции/метода."""
    a = node.args
    args: list[str] = []
    posonly = getattr(a, "posonlyargs", [])
    all_pos = list(posonly) + list(a.args)
    defaults = list(a.defaults)
    offset = len(all_pos) - len(defaults)
    for i, arg in enumerate(all_pos):
        s = arg.arg
        ann = _annotation(arg.annotation)
        if ann:
            s += f": {ann}"
        if i >= offset:
            d = _annotation(defaults[i - offset])
            if d:
                s += f" = {d}"
        args.append(s)
    if a.vararg:
        args.append("*" + a.vararg.arg)
    if a.kwonlyargs:
        if not a.vararg:
            args.append("*")
        for arg in a.kwonlyargs:
            s = arg.arg
            ann = _annotation(arg.annotation)
            if ann:
                s += f": {ann}"
            args.append(s)
    if a.kwarg:
        args.append("**" + a.kwarg.arg)

    ret = _annotation(node.returns)
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    sig = f"{prefix}{node.name}({', '.join(args)})"
    if ret:
        sig += f" -> {ret}"
    return {
        "name": node.name,
        "signature": _short(sig, MAX_SIG_LEN),
        "doc": (ast.get_docstring(node) or "").split("\n")[0].strip(),
    }


def parse_python_file(path: Path) -> dict:
    result = {"module_doc": "", "classes": [], "functions": [], "error": None}
    text = read_text_safe(path)
    if text is None:
        result["error"] = "не читается как текст"
        return result
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        result["error"] = f"SyntaxError: {e}"
        return result
    result["module_doc"] = ast.get_docstring(tree) or ""
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [b for b in (_annotation(x) for x in node.bases) if b]
            methods = [
                _func_info(n) for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            result["classes"].append({
                "name": node.name,
                "bases": bases,
                "doc": (ast.get_docstring(node) or "").split("\n")[0].strip(),
                "methods": methods,
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append(_func_info(node))
    return result


# ================================================================
# 1. PROJECT_TREE — секция в OVERVIEW.md
# ================================================================
def build_tree(root: Path) -> str:
    lines = [f"{root.name}/"]

    def walk(d: Path, prefix: str = ""):
        try:
            entries = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return
        dirs = [e for e in entries if e.is_dir() and not is_ignored_dir(e)]
        files = [e for e in entries if e.is_file() and not is_ignored_file(e)]
        for i, sub in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and not files
            sub_files = [f for f in sub.rglob("*")
                         if f.is_file() and not is_ignored_file(f)
                         and not _under_ignored(f, root)]
            total_kb = sum(f.stat().st_size for f in sub_files) / 1024
            count = len(sub_files)
            marker = "└──" if is_last_dir else "├──"
            lines.append(f"{prefix}{marker} {sub.name}/"
                         f"{' ' * max(1, 30 - len(sub.name))}"
                         f"({count} файлов, {total_kb:.1f} КБ)")
            walk(sub, prefix + ("    " if is_last_dir else "│   "))
        if len(files) > MAX_FILES_PER_TREE_DIR:
            head = files[:TREE_PREVIEW_HEAD]
            tail = files[-TREE_PREVIEW_TAIL:]
            middle_count = len(files) - TREE_PREVIEW_HEAD - TREE_PREVIEW_TAIL
            shown = head + [None] + tail
        else:
            shown = files
            middle_count = 0
        for j, f in enumerate(shown):
            is_last = (j == len(shown) - 1)
            marker = "└──" if is_last else "├──"
            if f is None:
                lines.append(f"{prefix}├── ... ещё {middle_count} однотипных (имена опущены) ...")
                continue
            size = human_size(f.stat().st_size)
            lines.append(f"{prefix}{marker} {f.name}"
                         f"{' ' * max(1, 34 - len(f.name))}({size})")

    walk(root)
    return "\n".join(lines)


# ================================================================
# 2. CODE_partN.md — сквозная нарезка по 500 КБ
# ================================================================
def collect_code_files(root: Path) -> list[Path]:
    """Все текстовые исходники в стабильном порядке: root → папки → файлы."""
    files: list[Path] = []
    for path in iter_project_files(root):
        ext = path.suffix.lower()
        if ext in CODE_EXTS or ext in CODE_SPECIAL:
            files.append(path)
    # Сортировка: сначала корневые, потом по пути
    def _key(p: Path):
        rel = p.relative_to(root)
        depth = len(rel.parts)
        return (depth, rel.as_posix().lower())
    files.sort(key=_key)
    return files


def render_code_file(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    size = path.stat().st_size
    text = read_text_safe(path)
    if text is None:
        return (f"## Файл: {rel}\n"
                f"Размер: {human_size(size)}\n"
                f"(не удалось прочитать как текст)\n")
    truncated = ""
    if size > MAX_SOURCE_FILE_BYTES:
        # Обрезка по границе строки, а не по байтам
        text = text[:MAX_SOURCE_FILE_BYTES]
        cut = text.rfind("\n")
        if cut > 0:
            text = text[:cut]
        truncated = f"\n# ... обрезано по границе строки, всего {size} байт ..."
    lang = LANG_MAP.get(path.suffix.lstrip(".").lower(), "text")
    lines_count = text.count("\n") + 1
    return (f"## Файл: {rel}\n"
            f"Размер: {human_size(size)}, строк: ~{lines_count}\n"
            f"```{lang}\n{text}{truncated}\n```\n")


def build_code_parts(files: list[Path], root: Path) -> list[tuple[str, str]]:
    """Режет весь код на части по MAX_OUTPUT_FILE_BYTES, без группировки по папкам."""
    if not files:
        return []
    header = ("# Код проекта\n"
              f"Файлов: {len(files)}\n"
              f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
              "---\n")
    parts: list[str] = [header]
    current_size = len(header.encode("utf-8"))
    part_num = 1
    results: list[tuple[str, str]] = []
    for path in files:
        chunk = render_code_file(path, root)
        chunk_size = len(chunk.encode("utf-8"))
        if current_size + chunk_size > MAX_OUTPUT_FILE_BYTES and len(parts) > 1:
            if part_num == 1:
                name = "CODE_part1.md"
            else:
                name = f"CODE_part{part_num}.md"
            results.append((name, "\n".join(parts)))
            part_num += 1
            parts = [header]
            current_size = len(header.encode("utf-8"))
        parts.append(chunk)
        current_size += chunk_size
    if len(parts) > 1:
        if part_num == 1:
            name = "CODE_part1.md"
        else:
            name = f"CODE_part{part_num}.md"
        results.append((name, "\n".join(parts)))
    return results


# ================================================================
# 3. CONFIG_TEMPLATES.md
# ================================================================
def _append_template_block(lines: list[str], path: Path, root: Path):
    rel = path.relative_to(root).as_posix()
    size = human_size(path.stat().st_size)
    text = read_text_safe(path)
    lines.append(f"#### {rel}  ({size})")
    lines.append("")
    if text is None:
        lines.append("(не читается как текст)")
    else:
        lines.append("```")
        lines.append(text.rstrip())
        lines.append("```")
    lines.append("")


def build_config_templates(root: Path) -> str:
    lines = [
        "# Конфиги и шаблоны",
        "",
        f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "> Без пользовательских данных (templates/, references/, assets/).",
        "> Без генераторов документации (make_docs.py и т.п.) — их код в CODE_partN.md.",
        "",
        "---",
        "",
    ]
    configs: list[Path] = []
    templates: list[Path] = []
    binaries: list[Path] = []
    for path in iter_project_files(root):
        name = path.name.lower()
        rel_parts = path.relative_to(root).parts
        top = rel_parts[0] if rel_parts else ""
        ext = path.suffix.lower()

        # Пропускаем данные и генераторы — они не конфиги
        if top in CONFIG_SKIP_DIRS:
            if ext in BINARY_EXTS:
                binaries.append(path)
            continue
        if path.name in CONFIG_SKIP_NAMES:
            continue

        is_env_like = name.startswith(".env") or ext == ".env"
        if ext in CONFIG_EXTS or is_env_like:
            configs.append(path)
        elif ext in TEMPLATE_EXTS:
            templates.append(path)
        elif ext in BINARY_EXTS:
            binaries.append(path)

    lines.append("## Конфиги")
    lines.append("")
    if not configs:
        lines.append("(нет)")
    for path in configs:
        rel = path.relative_to(root).as_posix()
        text = read_text_safe(path)
        if text is None:
            lines.append(f"### {rel}\n(не читается как текст)\n")
            continue
        text = mask_secrets(text)
        size = human_size(path.stat().st_size)
        lang = LANG_MAP.get(path.suffix.lstrip(".").lower(), "text")
        lines.append(f"### {rel}  ({size})")
        lines.append("")
        lines.append(f"```{lang}")
        lines.append(text.rstrip())
        lines.append("```")
        lines.append("")

    lines.append("## Шаблоны и текст")
    lines.append("")
    if not templates:
        lines.append("(нет)")
    else:
        groups: dict[str, list[Path]] = {}
        for t in templates:
            base = re.sub(r'[_\-\s]*\d{4,}.*$', '', t.stem)
            base = re.sub(r'[_\-\s]*(copy|backup).*$', '', base, flags=re.I)
            groups.setdefault(base, []).append(t)
        for base, files in sorted(groups.items()):
            files_sorted = sorted(files)
            if len(files_sorted) > MAX_FILES_PER_TREE_DIR:
                sample = files_sorted[:TEMPLATE_SAMPLES_PER_GROUP]
                lines.append(f"### {base}.* — {len(files_sorted)} файлов "
                             f"(содержимое показано у {len(sample)})")
                lines.append("")
                for f in sample:
                    _append_template_block(lines, f, root)
                others = [f.name for f in files_sorted[TEMPLATE_SAMPLES_PER_GROUP:]]
                shown = others[:MAX_LISTED_NAMES]
                tail = (f" … и ещё {len(others) - len(shown)} (имена опущены)"
                        if len(others) > len(shown) else "")
                lines.append(f"*Остальные ({len(others)}):* {', '.join(shown)}{tail}")
                lines.append("")
            else:
                lines.append(f"### {base}.* — {len(files_sorted)} файлов")
                lines.append("")
                for f in files_sorted:
                    _append_template_block(lines, f, root)

    if binaries:
        lines.append("## Бинарные файлы (не включены, только имена)")
        lines.append("")
        shown = binaries[:MAX_LISTED_NAMES]
        for b in shown:
            rel = b.relative_to(root).as_posix()
            lines.append(f"- `{rel}` ({human_size(b.stat().st_size)})")
        if len(binaries) > len(shown):
            lines.append(f"- *… и ещё {len(binaries) - len(shown)} файлов — "
                         f"имена опущены, чтобы не раздувать пакет.*")
        lines.append("")
    return "\n".join(lines)


# ================================================================
# 4. OVERVIEW.md — слитая сводка
#    (структура + сигнатуры + встроенные документы + manifest + git state)
# ================================================================
def _build_embedded_docs(root: Path) -> tuple[str, set[str]]:
    """Секция с ВСТРОЕННЫМИ документами (содержимым целиком).

    Возвращает (markdown-текст, множество реально встроенных путей).
    Если ни одного документа нет — вернёт ("", set()).
    """
    order = EMBED_IN_OVERVIEW
    present: list[tuple[str, str]] = []
    for rel, _desc in order:
        p = root / rel
        if not p.exists():
            continue
        text = read_text_safe(p)
        if not text or not text.strip():
            continue
        present.append((rel, text.rstrip()))

    if not present:
        return "", set()

    lines = [
        "## Встроенные документы",
        "",
        "> Это смысловой слой проекта: правила игры, суть, стиль работы,",
        "> архитектура и текущие задачи. Встроены сюда, чтобы OVERVIEW.md",
        "> был самодостаточным для ИИ-ассистента.",
        "",
    ]
    for rel, text in present:
        lines.append(f"### `{rel}`")
        lines.append("")
        # Четыре бэктика — чтобы не конфликтовать с тройными внутри документов.
        lines.append("````markdown")
        lines.append(text)
        lines.append("````")
        lines.append("")
    embedded = {rel for rel, _ in present}
    return "\n".join(lines), embedded


def _build_docs_section(root: Path, embedded: set[str]) -> str:
    """Секция со списком документов, которые НЕ встроены.

    Показывает только те, что реально лежат в корне / project_info/manuals
    и не попали в embedded.
    Если таких нет — вернёт пустую строку.
    """
    known = EMBED_IN_OVERVIEW + REFER_IN_OVERVIEW
    present: list[tuple[str, str, bool]] = []
    for rel, desc in known:
        if not (root / rel).exists():
            continue
        present.append((rel, desc, rel in embedded))

    not_embedded = [(rel, desc) for rel, desc, is_emb in present if not is_emb]
    if not not_embedded:
        return ""

    lines = [
        "## Документы проекта (генерируются `make_docs.py`)",
        "",
        "Эти файлы лежат в корне проекта, но **не встроены** в OVERVIEW.md.",
        "Их содержимое может быть большим или устаревающим — поэтому",
        "запрашивай их отдельно, когда задача этого требует.",
        "",
    ]
    for rel, desc in not_embedded:
        lines.append(f"- `{rel}` — {desc}.")

    lines += [
        "",
        "> **Когда просить эти файлы:**",
        "> - `README*.md` — общее описание проекта для людей.",
        "> - `CHANGELOG.md` — история версий (что и когда менялось).",
        "> - `DEVLOG.md` — журнал сессий, включая неудачные ветки.",
        "> - `USER_MANUAL.md` — инструкция пользователя (UI, сценарии).",
        "",
    ]
    return "\n".join(lines)


def _build_git_state_section(root: Path) -> str:
    if not (root / ".git").exists():
        return "_git-репозиторий не найден._"
    out: list[str] = []
    for args in (["log", "--oneline", "-15"], ["status", "--short"], ["tag", "-l"]):
        try:
            r = subprocess.run(
                ["git"] + args, cwd=root,
                capture_output=True, text=True, timeout=15,
                encoding="utf-8", errors="replace",
            )
            out.append(f"```\n$ git {' '.join(args)}\n{r.stdout.strip()}\n```\n")
        except Exception:
            return "_не удалось получить состояние git._"
    return "\n".join(out)


def build_overview(root: Path, created: list[tuple[str, int]]) -> str:
    lines: list[str] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- Заголовок и навигация ---
    lines += [
        "# OVERVIEW — карта проекта для ИИ",
        "",
        f"Сгенерировано: {now}",
        f"Корень проекта: `{root.name}`",
        "",
        "> **Как грузить в чат:**",
        "> 1. Сначала этот файл (`OVERVIEW.md`) — карта, сигнатуры,",
        ">    встроенные документы и состояние git.",
        "> 2. По необходимости — `CODE_partN.md` (код нарезан по 500 КБ).",
        "> 3. Конфиги и схемы — `CONFIG_TEMPLATES.md`.",
        "",
        "---",
        "",
    ]

    # --- Оглавление ---
    py_files: list[tuple[Path, str, dict]] = []
    other_code: list[tuple[Path, str]] = []
    for path in iter_project_files(root):
        ext = path.suffix.lower()
        rel = path.relative_to(root).as_posix()
        if ext == ".py":
            py_files.append((path, rel, parse_python_file(path)))
        elif ext in CODE_SPECIAL:
            other_code.append((path, rel))

    lines += [
        "## Оглавление",
        "",
        "### Python-файлы",
        "",
    ]
    for _, rel, _info in py_files:
        size = human_size((root / rel).stat().st_size)
        lines.append(f"- `{rel}` ({size})")
    lines.append("")
    if other_code:
        lines.append("### Прочий код и разметка")
        lines.append("")
        for _, rel in other_code:
            size = human_size((root / rel).stat().st_size)
            lines.append(f"- `{rel}` ({size})")
        lines.append("")
    lines += ["---", ""]

    # --- Секция: файлы с описанием (сигнатуры!) ---
    lines += [
        "## Файлы с описанием (сигнатуры функций и классов)",
        "",
    ]
    for path, rel, info in py_files:
        size = human_size(path.stat().st_size)
        lines.append(f"### `{rel}`  ({size})")
        lines.append("")
        if info["error"]:
            lines.append(f"⚠️ {info['error']}")
            lines.append("")
            continue
        doc = info["module_doc"].strip().split("\n")[0] if info["module_doc"] else ""
        if doc:
            lines.append(f"**Назначение:** {doc}")
            lines.append("")
        if info["classes"]:
            lines.append("**Классы:**")
            lines.append("")
            for cls in info["classes"]:
                base = f"({', '.join(cls['bases'])})" if cls.get("bases") else ""
                doc_c = f" — {cls['doc']}" if cls["doc"] else ""
                lines.append(f"- `{cls['name']}{base}`{doc_c}")
                methods = cls["methods"]
                for m in methods[:MAX_CLASS_METHODS]:
                    doc_m = f" — {m['doc']}" if m["doc"] else ""
                    lines.append(f"  - `{m['signature']}`{doc_m}")
                if len(methods) > MAX_CLASS_METHODS:
                    lines.append(f"  - … ещё {len(methods) - MAX_CLASS_METHODS} методов")
            lines.append("")
        if info["functions"]:
            lines.append("**Функции верхнего уровня:**")
            lines.append("")
            for fn in info["functions"]:
                doc_f = f" — {fn['doc']}" if fn["doc"] else ""
                lines.append(f"- `{fn['signature']}`{doc_f}")
            lines.append("")
        lines += ["---", ""]

    # --- Секция: структура проекта ---
    lines += [
        "## Структура проекта",
        "",
        "```",
        build_tree(root),
        "```",
        "",
        f"_Игнорируются: {', '.join(sorted(IGNORE_DIRS))}_",
        "",
        "---",
        "",
    ]

    # --- Секция: что в упаковке (бывший MANIFEST) ---
    lines += [
        "## Что лежит в project_info/ai_pack/",
        "",
        "| Файл | Размер |",
        "|------|--------|",
    ]
    for name, size in sorted(created):
        lines.append(f"| `{name}` | {human_size(size)} |")
    lines += [
        "",
        "**Порядок загрузки в чат:**",
        "1. `OVERVIEW.md` — всегда первым. Содержит:",
        "   структуру, сигнатуры, встроенные документы (`AI_BRIEF.md`,",
        "   `DIGEST.md`, `QWEN.md`, `ARCHITECTURE.md`, `TODO.md`),",
        "   manifest и состояние git.",
        "2. `CODE_partN.md` — по необходимости (код нарезан по 500 КБ).",
        "3. `CONFIG_TEMPLATES.md` — для настроек и схем.",
        "4. Прочие документы (`README.md`, `README_en.md`, `CHANGELOG.md`,",
        "   `DEVLOG.md`, `USER_MANUAL.md`) — по запросу отдельно.",
        "",
        "**Что НЕ включено (специально):**",
        "- Каталоги данных: `data/`, `SonologData/`, `Резервные копии_*`, `uploads/`,",
        "  `exports/`, `personal/`, `transfer/`, `_old_v2/`.",
        "- Старые сборки: `dist_*`, `build/`.",
        "- Списки имён длиннее 30 позиций урезаны.",
        "- Бинарные файлы — только имена (до 30 штук).",
        "- В `CONFIG_TEMPLATES.md` не входят: `templates/`, `references/`, `assets/`,",
        "  `make_docs.py`, `create_project_docs.py`, `create_user_manual.py`.",
        "- Секреты в конфигах заменены на `***`.",
        "",
        "---",
        "",
    ]

    # --- Секция: встроенные документы ---
    embedded_md, embedded_set = _build_embedded_docs(root)
    if embedded_md:
        lines += [embedded_md, "---", ""]

    # --- Секция: документы проекта, которые НЕ встроены ---
    docs_section = _build_docs_section(root, embedded_set)
    if docs_section:
        lines += [docs_section, "---", ""]

    # --- Секция: git state ---
    lines += [
        "## Состояние git",
        "",
        _build_git_state_section(root),
        "",
    ]
    return "\n".join(lines)


# ================================================================
# MAIN
# ================================================================
def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*"):
        if old.is_file():
            old.unlink()

    print(f"📦 Собираю ai_pack/ в {OUT_DIR}")
    print()
    created: list[tuple[str, int]] = []

    # 1. CODE_partN.md — код в сквозной нарезке
    code_files = collect_code_files(BASE_DIR)
    for name, content in build_code_parts(code_files, BASE_DIR):
        out = OUT_DIR / name
        out.write_text(content, encoding="utf-8")
        created.append((name, out.stat().st_size))
        print(f"✅ {name}  ({human_size(out.stat().st_size)})")

    # 2. CONFIG_TEMPLATES.md
    cfg = build_config_templates(BASE_DIR)
    p = OUT_DIR / "CONFIG_TEMPLATES.md"
    p.write_text(cfg, encoding="utf-8")
    created.append(("CONFIG_TEMPLATES.md", p.stat().st_size))
    print(f"✅ CONFIG_TEMPLATES.md  ({human_size(p.stat().st_size)})")

    # 3. OVERVIEW.md — собирается последним: он содержит manifest (created)
    overview = build_overview(BASE_DIR, created)
    p = OUT_DIR / "OVERVIEW.md"
    p.write_text(overview, encoding="utf-8")
    overview_size = p.stat().st_size
    # В таблице manifest самого себя не показываем (его размер неизвестен до записи),
    # добавим отдельной строкой:
    text = p.read_text(encoding="utf-8")
    text = text.replace(
        "|------|--------|",
        f"|------|--------|\n| `OVERVIEW.md` | {human_size(overview_size)} |",
        1,
    )
    p.write_text(text, encoding="utf-8")
    print(f"✅ OVERVIEW.md  ({human_size(overview_size)})")

    print()
    print(f"🎉 Готово. Файлов: {len(created) + 1}")
    print(f"📁 Смотри: {OUT_DIR}")


if __name__ == "__main__":
    main()