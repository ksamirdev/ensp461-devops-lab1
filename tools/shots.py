import os
from playwright.sync_api import sync_playwright
U = "http://localhost:8080"; J = U + "/job/text-stats-pipeline"; O = "/lab/evidence/screenshots/"
PAGES = [
    ("jenkins-dashboard", U + "/", False),
    ("jenkins-plugins", U + "/manage/pluginManager/installed", False),
    ("job-stage-view", J + "/", True),
    ("job-config", J + "/configure", True),
    ("build1-overview", J + "/1/", False),
    ("build1-pipeline-graph", J + "/1/pipeline-overview/", False),
    ("build1-console", J + "/1/console", False),
    ("build1-tests", J + "/1/testReport/", False),
    ("build2-overview", J + "/2/", False),
    ("build2-console", J + "/2/console", False),
    ("polling-log", J + "/scmPollLog/", False),
    ("github-repo", "https://github.com/ksamirdev/ensp461-devops-lab1", False),
    ("github-commits", "https://github.com/ksamirdev/ensp461-devops-lab1/commits/main", False),
]
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1400, "height": 900})
    pg.goto(U + "/login"); pg.fill("#j_username", "samir"); pg.fill("#j_password", os.environ["PW"]); pg.click("button[name=Submit]"); pg.wait_for_load_state("networkidle")
    for name, url, full in PAGES:
        pg.goto(url); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1500)
        pg.screenshot(path=O + name + ".png", full_page=full); print(name, pg.title())
    b.close()
