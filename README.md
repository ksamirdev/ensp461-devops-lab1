# ENSP461 Lab 1 - DevOps Foundations and Continuous Integration

Author: Samir Kumar Gupta

Text statistics Flask service built, tested, packaged and deployed by a Jenkins pipeline.

## Layout
- `service/` - Flask application
- `tests/` - pytest suite
- `deploy/` - systemd unit and deploy script
- `Jenkinsfile` - declarative pipeline
- `evidence/` - command logs and screenshots from the lab runs
- `reports/` - lab reports, one PDF per question

## Run locally
```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -v
.venv/bin/flask --app service.web run
```
