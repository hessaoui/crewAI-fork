# marketing-crew

A small CrewAI project that turns a brand brief into market research and
ready-to-test ad angles, then scores those angles with a critic agent.
Built to run on free LLM backends (Groq by default, Gemini optional).

The pipeline runs two agents in sequence, plus a standalone critic:

1. `market_researcher` → purchase triggers, objections, angles to avoid (`outputs/research.md`)
2. `ad_strategist` → 6 ad hooks across 3 emotional levers (`outputs/ad_angles.md`)
3. `ad_critic` (separate, always on Groq) → scores hooks 1-10 on brand fit,
   hook strength, and platform compliance (`outputs/critic_scores_<label>.md`)

All brand-specific details are supplied as **inputs**, not hard-coded — so this
repo contains no brand strategy of its own.

---

## Setup

```bash
cd marketing-crew
cp .env.example .env                              # add your GROQ_API_KEY
cp src/marketing_crew/config/brand.example.yaml \
   src/marketing_crew/config/brand.local.yaml     # fill in your real brand
```

`.env` and `brand.local.yaml` are both git-ignored — your keys and your brand
positioning never get committed. If `brand.local.yaml` is absent, the committed
`brand.example.yaml` placeholders are used.

This project runs inside the CrewAI workspace venv (`crewAI-fork/.venv`); it has
no `pyproject.toml` of its own, so use the `python -m` entrypoints below.

## Daily Usage

### 1. Run the pipeline (research → ad angles)

```bash
cd marketing-crew
PYTHONPATH=src uv run --project .. python -m marketing_crew.main
```

→ writes `outputs/research.md` and `outputs/ad_angles.md`.

### 2. Score the hooks with the critic

```bash
PYTHONPATH=src uv run --project .. python -m marketing_crew.critic outputs/ad_angles.md groq
```

- Arg 1 = hooks file (default `outputs/ad_angles.md`)
- Arg 2 = label (default derived from the filename)
- Output → `outputs/critic_scores_<label>.md`

The critic is **always pinned to Groq** (`critic_llm()` in `crew.py`,
`temperature=0`) so scores stay consistent and cheap no matter which backend
generated the hooks.

### 3. Switch / compare backends (Groq vs Gemini)

Backend is selected by the **`MKT_BACKEND`** env var:

| `MKT_BACKEND` | Model env var | Default model | API key |
|---------------|---------------|---------------|---------|
| `groq` (default) | `MKT_MODEL`        | `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| `gemini`         | `MKT_MODEL_GEMINI` | `gemini/gemini-2.0-flash`      | `GEMINI_API_KEY` |

Generate with each backend, score both with the same (Groq) critic, then
compare totals instead of eyeballing:

```bash
RUN="PYTHONPATH=src uv run --project .. python -m marketing_crew.main"
CRITIC="PYTHONPATH=src uv run --project .. python -m marketing_crew.critic"

MKT_BACKEND=groq   bash -c "$RUN"; cp outputs/ad_angles.md outputs/ad_angles_groq.md
MKT_BACKEND=gemini bash -c "$RUN"; cp outputs/ad_angles.md outputs/ad_angles_gemini.md

bash -c "$CRITIC outputs/ad_angles_groq.md   groq"
bash -c "$CRITIC outputs/ad_angles_gemini.md gemini"

diff outputs/critic_scores_groq.md outputs/critic_scores_gemini.md
```

> The Gemini path only runs if your Google AI Studio project has free-tier
> quota; a key with `limit: 0` returns HTTP 429. Groq is the default.

## Known limits

- The default models (Groq Llama, Gemini Flash) are tuned for natural-language
  work — research, ad copy, brand storytelling. **Do not route code-generation
  subtasks through them.** Give any coding step a code-capable model instead.
- Pipeline output is non-deterministic (`temperature=0.7`), so repeated runs
  produce different hooks. Run a few times and shortlist by critic score.

## Requirements

Depends on `crewai` plus `litellm` (Groq) and, for the optional Gemini backend,
`google-genai`.
