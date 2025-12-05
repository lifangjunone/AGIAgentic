<h1 align="center">
  <img style="vertical-align:middle" height="600"
  src="https://github.com/lifangjunone/AGIAgentic/blob/main/AGIAgentic-backend/docs/_static/imgs/logo.png">
</h1>
<p align="center">
  <i>AGI Agentic 🚀</i>
</p>

<p align="center">
    <a href="https://github.com/lifangjunone/AGIAgentic/releases">
        <img alt="Latest release" src="https://img.shields.io/github/release/vibrantlabsai/ragas.svg">
    </a>
    <a href="https://www.python.org/">
        <img alt="Made with Python" src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg?color=purple">
    </a>
    <a href="https://github.com/vibrantlabsai/ragas/blob/master/LICENSE">
        <img alt="License Apache-2.0" src="https://img.shields.io/github/license/vibrantlabsai/ragas.svg?color=green">
    </a>
</p>

<h4 align="center">
    <p>
        <a href="https://127.0.0.1">Documentation</a> |
        <a href="#fire-quickstart">Quick start</a> |
        <a href="https://127.0.0.1">Join Discord</a> |
        <a href="https://https://en.wikipedia.org/wiki/Agentic_AI">Blog</a> |
        <a href="https://https://en.wikipedia.org/wiki/Agentic_AI">NewsLetter</a> |
        <a href="https://https://en.wikipedia.org/wiki/Agentic_AI">Careers</a>
    <p>
</h4>

## Demo

### Video

<h1 align="center">
  <video width="800" controls>
    <source src="https://github.com/lifangjunone/AGIAgentic/raw/main/AGIAgentic-backend/docs/_static/video/demo_video.mp4" type="video/mp4">
    您的浏览器不支持视频标签。
  </video>
</h1>

### Images

<h1 align="center">
  <img style="vertical-align:middle" height="600"
  src="https://github.com/lifangjunone/AGIAgentic/blob/main/AGIAgentic-backend/docs/_static/imgs/image_01.png">
    <img style="vertical-align:middle" height="600"
  src="https://github.com/lifangjunone/AGIAgentic/blob/main/AGIAgentic-backend/docs/_static/imgs/image_02.png">
    <img style="vertical-align:middle" height="600"
  src="https://github.com/lifangjunone/AGIAgentic/blob/main/AGIAgentic-backend/docs/_static/imgs/image_03.png">
    <img style="vertical-align:middle" height="600"
  src="https://github.com/lifangjunone/AGIAgentic/blob/main/AGIAgentic-backend/docs/_static/imgs/image_04.png">
    <img style="vertical-align:middle" height="600"
  src="https://github.com/lifangjunone/AGIAgentic/blob/main/AGIAgentic-backend/docs/_static/imgs/image_05.png">
</h1>

<!-- > [!NOTE] -->

## Key Features

- 🎯 ReAct
- 🧪 MCP
- 🔗 Tools
- 📊 Agent

## :fire: Quickstart (uv-based)

This Quickstart uses the project's uv workflow (preferred). Commands assume macOS and a POSIX shell.

Prerequisites

- Python 3.11+ (3.12 recommended)
- Git
- uv CLI (project package manager). If you don't have it, install per your environment (e.g. pip install uv).

1. Clone repository

```bash
git clone https://github.com/lifangjunone/AGIAgentic.git
cd AGIAgentic/AGIAgentic-backend
```

2a) (Optional) Create and activate a venv (recommended if you prefer)

```bash
python -m venv .venv
source .venv/bin/activate
```

2b) (If you rely on uv-managed env, skip venv creation)

3. Sync dependencies with uv (reads uv.lock / pyproject)

```bash
# synchronize / install pinned deps from uv.lock
uv sync
```

4. Configure environment variables

```bash
# environment config
export RUN_ENV=development|production|test
# config file path:
├─ envs/
│  ├─ development.env # dev env
│  ├─ production.env # prod env
│  ├─ test.env # test env
```

Or export for current shell:

```bash
export OPENAI_API_KEY="sk-..."
```

5. Start the backend (preferred: uv)

```bash
# run the app via project CLI (hot-reload behaviour depends on project)
uv run main.py
```

Fallback: uvicorn (if uv is unavailable)

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. Test the streaming plan API (example)

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/plan_executor/stream' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_task": "昨天北京到天津的车票都有哪些时间的",
  "user_id": "001"
}'
```

The endpoint returns Server-Sent Events (SSE). Parse each "data:" line as JSON.

7. Run tests

```bash
pytest -q
```

Troubleshooting (common)

- "Expected dict, got <...>": ensure runtime events/state only contain serializable types (strings/dicts/lists/primitives). Avoid writing langchain HumanMessage / complex objects into graph state or SSE payloads.
- Dependency / lock issues: run `uv sync` again, or recreate your venv and re-run `uv sync`.
- Model/tool errors: verify API keys and tool configurations in .env.

If you want, I can add platform-specific launch scripts, a systemd service example, or a docker-compose file next.

We welcome contributions from the community! Whether it's bug fixes, feature additions, or documentation improvements, your input is valuable.

1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## Cite Us

```
@misc{ragas2024,
  author       = {LI},
  title        = {AGIAgentic: Plan and execute},
  year         = {2025},
  howpublished = {\url{https://github.com}},
}
```

## Technical documentation

+Jump to the streaming events reference: [astream_events — API Reference](./AGIAgentic-backend/docs/docs/astream_events.md)

