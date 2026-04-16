# Helldivers Data Collector (GitHub Actions)

This folder now contains a CI-friendly collector script:

- `collector.py`: runs one API collection pass and appends to `planet_history.csv`
- `requirements.txt`: dependencies for the collector runtime
- `.github/workflows/helldivers-data-collection.yml`: hourly workflow

## Triggering runs

- Automatic run: every hour (`cron: 0 * * * *`)
- Manual run: Actions tab -> `Helldivers Data Collection` -> Run workflow

## Output persistence

Each run updates:

- `personal_projects/helldivers2/data_collection/planet_history.csv`

If the CSV changes, the workflow commits and pushes the update automatically.
