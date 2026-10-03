# Python Project Template

A skeleton for new Python projects: runtime data, service scripts and
documentation are separated from production code from day one.

## Structure
- repo root — production code (entry point `app.py`/`main.py` and modules);
- `data/` — runtime data (gitignored): db, uploads, exports, personal,
  big_files, reports, logs, temp;
- `service/` — service scripts: migrations, fixes, deploy, tools, docs;
  run ONLY via `python service/run.py service/...`;
- `project_info/manuals/` — hand-written documentation for people;
- `project_info/ai_pack/` — generated AI handover pack (gitignored);
  generator: `service/docs/ai_pack.py`;
- `tests/` — tests.

## Starting a new project
1. Clone this template under a new name, delete the `.git` folder, run `git init`.
2. `python -m venv venv`, then `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill in the values.
4. Keep production code at the root; put service scripts into `service/`.

## Documentation & AI handover
- `AI_BRIEF.md` — conventions and hard rules for AI assistants; update every release;
- `CHANGELOG.md` — one line per version;
- AI handover pack: run `python service/docs/ai_pack.py`, then upload files
  from `project_info/ai_pack/` in the order given by `MANIFEST.md`.

## Mirroring
Pushes to this repository are mirrored to GitHub and MosHub automatically
via the `.gitverse` CI config.