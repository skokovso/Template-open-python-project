# ЗАПОЛНИТЬ: название проекта

ЗАПОЛНИТЬ: один абзац — что это, зачем, для кого.

## Быстрый старт
1. `python -m venv venv`, затем `pip install -r requirements.txt`.
2. Скопировать `.env.example` в `.env`, заполнить значения.
3. ЗАПОЛНИТЬ: команда запуска и адрес/порт.

## Структура
- корень — боевой код (точка входа и модули);
- `data/` — данные рантайма (в .gitignore): db, uploads, exports,
  personal, big_files, reports, logs, temp;
- `service/` — служебное: migrations, fixes, deploy, tools, docs;
  запуск ТОЛЬКО через `python service/run.py service/...`;
- `project_info/manuals/` — руководства пользователей (md + pdf);
- `project_info/ai_pack/` — упаковка для ИИ (`service/docs/ai_pack.py`);
- `tests/` — тесты.

## Документация
- `AI_BRIEF.md` — правила и табу для ИИ-ассистентов;
- `CHANGELOG.md` — история версий (строка на версию);
- `ARCHITECTURE.md` — устройство, схема БД, потоки данных;
- `DIGEST.md` — короткий дайджест для быстрого входа в контекст;
- руководства — в `project_info/manuals/`, PDF собирает
  `service/docs/manuals_to_pdf.py`.

Все документы правятся в `service/docs/make_docs.py` (словарь DOCS)
и раскладываются командой с флагом `--force`.
