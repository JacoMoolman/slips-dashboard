# SLIPS Dashboard Deployment Notes

## Current Online Repo

- GitHub repo: `https://github.com/JacoMoolman/slips-dashboard`
- Visibility: public
- Branch: `master`
- Main Streamlit file: `dashboard/dashboard.py`

## Streamlit Community Cloud Settings

Use these values on the Streamlit deploy screen:

```text
Repository: JacoMoolman/slips-dashboard
Branch: master
Main file path: dashboard/dashboard.py
```

The generated app URL can be any available `*.streamlit.app` name.

## What Was Uploaded

Only the sanitized dashboard deploy files were pushed:

```text
dashboard/dashboard.py
dashboard/requirements.txt
dashboard/data/2026-02.json
dashboard/data/2026-04.json
dashboard/data/2026-05.json
README.md
.gitignore
```

The deploy repo does not include the slip photos, raw OCR CSV, PDFs, logs, or the Flask app.

## Local Paths

- Main local project: `G:\SLIPS`
- Sanitized deploy repo: `G:\SLIPS\deploy\slips-dashboard`
- Raw OCR CSV: `G:\SLIPS\manual_ocr_receipts.csv`
- Latest local PDF report: `G:\SLIPS\spending_report_01_Jun_2026.pdf`

## Updating The Online Dashboard Later

1. Update the month JSON files in `G:\SLIPS\dashboard\data`.
2. Copy changed JSON files into `G:\SLIPS\deploy\slips-dashboard\dashboard\data`.
3. From `G:\SLIPS\deploy\slips-dashboard`, run:

```powershell
git status
git add dashboard/data
git commit -m "Update dashboard data"
git push
```

Streamlit Cloud should redeploy automatically after the push.

## GitHub CLI

GitHub CLI was installed here:

```text
C:\Program Files\GitHub CLI\gh.exe
```

The authenticated GitHub user was `JacoMoolman`.

