# Personal Opportunity Agent (skeleton)

A private, scheduled research pipeline that collects possible opportunities,
ranks them against a personal profile, remembers previously seen items, and
writes a daily Markdown report.

This is intentionally a skeleton. The included dry run works without API keys
or network access, while the provider and source interfaces are ready to refine.

## What is included

- A daily GitHub Actions workflow, plus a manual **Run workflow** trigger
- Profile, priorities, and source configuration files
- RSS/Atom collection and an included sample-data collector
- Deterministic filtering, scoring, and deduplication
- Optional Gemini or OpenRouter analysis
- Persistent `data/seen-opportunities.json` history
- Daily reports under `reports/`
- Optional generic webhook delivery

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m opportunity_scout --dry-run
```

The command prints the report and writes it to `reports/YYYY-MM-DD.md`.

To preview a run without changing reports or history:

```powershell
python -m opportunity_scout --dry-run --no-save
```

## Put it on GitHub

1. Create a **private** repository.
2. Push this directory to its default branch.
3. Edit the YAML files under `config/`.
4. In **Settings > Secrets and variables > Actions**, add whichever secrets
   you need:

   - `GEMINI_API_KEY`, or
   - `OPENROUTER_API_KEY`
   - optionally `DELIVERY_WEBHOOK`

5. Edit `.github/workflows/daily-scout.yml` to select the provider and model.
6. Open **Actions > Daily opportunity scout > Run workflow** for a manual test.

The default scheduled workflow uses deterministic analysis, so it runs without
a model API key. Switch `MODEL_PROVIDER` to `gemini` or `openrouter` after
choosing a model.

## Configuration

- `config/profile.yml`: relatively stable facts used for eligibility matching
- `config/priorities.yml`: current goals and topic weights
- `config/sources.yml`: RSS/Atom feeds and per-run collection limits

Do not store names, passwords, student IDs, exact addresses, financial account
details, or other highly sensitive information in these files.

## Pipeline

```text
Load profile and priorities
        -> collect candidates
        -> remove previously seen URLs
        -> deterministic pre-ranking
        -> optional model analysis
        -> final ranking
        -> Markdown report
        -> update history
        -> optional webhook delivery
```

## Current limitations

- RSS/Atom is the only live collector included in the skeleton.
- Direct search API integration is left as a clear extension point.
- Eligibility verification is advisory; important claims must be checked at
  the linked primary source.
- The generic webhook sends a JSON payload with a `content` property. Adapt
  `opportunity_scout/deliver.py` for email, Telegram, or another destination.

