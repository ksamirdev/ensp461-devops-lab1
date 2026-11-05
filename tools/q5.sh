set -u
. /lab/tools/rec.sh /lab/evidence/logs/q5-git-workflow.log
S=/lab/tools/src; R=~/ensp461-devops-lab1
mkdir -p $R; cd $R
rec "git init"
cp $S/.gitignore $S/requirements.txt $S/README.md .; mkdir -p service; cp $S/service/* service/
rec "git status --short"
rec "git add ."
rec "git commit -m 'Add text statistics Flask service'"
rec "git checkout -b feature/test-suite"
mkdir -p tests; cp $S/tests/* tests/
rec "git add tests"
rec "git commit -m 'Add pytest suite for service endpoints'"
rec "python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt && .venv/bin/python -m pytest -v"
rec "git checkout main"
rec "git merge --no-ff feature/test-suite -m 'Merge feature/test-suite into main'"
rec "git tag -a v1.0.0 -m 'First tested release'"
rec "git branch -a"
rec "git log --oneline --graph --decorate --all"
