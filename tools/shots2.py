import os
from playwright.sync_api import sync_playwright
U = "http://localhost:8080"; J = U + "/job/text-stats-pipeline"; O = "/lab/evidence/screenshots/"; G = "https://github.com/ksamirdev/ensp461-devops-lab1"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(viewport={"width": 1400, "height": 900})
    pg.goto(U + "/login"); pg.fill("#j_username", "samir"); pg.fill("#j_password", os.environ["PW"]); pg.click("button[name=Submit]"); pg.wait_for_load_state("networkidle")
    pg.goto(J + "/2/pollingLog/"); pg.wait_for_timeout(1500); pg.screenshot(path=O + "polling-log.png"); print("poll", pg.url)
    pg.goto(J + "/1/"); pg.click("text=Pipeline Overview"); pg.wait_for_timeout(4000); pg.screenshot(path=O + "build1-pipeline-graph.png"); print("graph", pg.url)
    for n, u in (("github-repo", G), ("github-commits", G + "/commits/main")):
        pg.goto(u, wait_until="load", timeout=120000); pg.wait_for_timeout(3000); pg.screenshot(path=O + n + ".png"); print(n, pg.title())
    b.close()
