# Шаблон Python-проекта

Скелет для новых проектов: данные, служебные скрипты и документация
отделены от боевого кода с первого дня.

## Структура
- корень — боевой код (точка входа app.py/main.py и модули);
- `data/` — данные рантайма (в .gitignore): db, uploads, exports, personal, big_files, reports, logs, temp;
- `service/` — служебное: migrations, fixes, deploy, tools, docs; запуск ТОЛЬКО через `python service/run.py service/...`;
- `project_info/manuals/` — рукописная документация для людей;
- `project_info/ai_pack/` — генерируемая упаковка для ИИ (в .gitignore); генератор — `service/docs/ai_pack.py`;
- `tests/` — тесты.

## Старт нового проекта
1. Клонируйте шаблон под новым именем, удалите `.git`, сделайте `git init`.
2. `python -m venv venv`, `pip install -r requirements.txt`.
3. Скопируйте `.env.example` в `.env`, заполните.
4. Боевой код — в корень, служебное — в `service/`.

## Документация и ИИ
- `AI_BRIEF.md` — договорённости и табу, обновлять каждую версию;
- `CHANGELOG.md` — строка на версию;
- упаковка для чата: `python service/docs/ai_pack.py`, грузить по MANIFEST из `project_info/ai_pack/`.