"""Builds the seven lab report PDFs from the real logs and screenshots in evidence/."""
import json, os, subprocess, textwrap
from PIL import Image as PI, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, ListFlowable, ListItem, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = os.environ.get("REPO", "/home/samir/ensp461-devops-lab1")
EV, OUT = ROOT + "/evidence", ROOT + "/reports"
LOGS, SHOTS = EV + "/logs/", EV + "/screenshots/"
NAME, ROLL = "Samir Kumar Gupta", "2301730243"
ENV = "Ubuntu 24.04 LTS (Docker, systemd)"
REPO = "https://github.com/ksamirdev/ensp461-devops-lab1"
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
ss = getSampleStyleSheet()
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=14, spaceAfter=6)
H = ParagraphStyle("H", parent=ss["Heading2"], fontSize=12.5, textColor=colors.HexColor("#1f3a5f"), spaceBefore=10, spaceAfter=5, keepWithNext=1)
Q = ParagraphStyle("Q", parent=B, fontName="Helvetica-Bold", backColor=colors.HexColor("#eef2f7"), borderPadding=6, spaceAfter=12)
CAP = ParagraphStyle("C", parent=B, fontSize=8.5, textColor=colors.HexColor("#555555"), alignment=1)
CODE = ParagraphStyle("K", fontName="Courier", fontSize=7.8, leading=9.6, backColor=colors.HexColor("#f5f5f5"), borderPadding=4, spaceAfter=8)


def read(name):
    return open(LOGS + name, errors="replace").read()


def term(name, text, width=108, max_lines=46):
    """Renders real log text as a terminal-style PNG."""
    lines = []
    for l in text.expandtabs(4).splitlines():
        if "Reading database" in l:
            continue
        lines += textwrap.wrap(l, width, drop_whitespace=False, replace_whitespace=False) or [""]
    lines = lines[:max_lines]
    im = PI.new("RGB", (int(width * 9.2) + 32, len(lines) * 20 + 32), "#14181f")
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((16, 16 + i * 20), l, font=FONT, fill="#7ee787" if l.startswith("$ ") else "#e6edf3")
    p = SHOTS + "term-" + name + ".png"
    im.save(p)
    return p


def fig(path, cap, w=16.5 * cm, max_h=17 * cm):
    iw, ih = PI.open(path).size
    h = w * ih / iw
    if h > max_h:
        w, h = w * max_h / h, max_h
    return KeepTogether([Image(path, w, h), Paragraph("Fig: " + cap, CAP), Spacer(1, 8)])


def shot(name, cap):
    return fig(SHOTS + name + ".png", cap)


def logfig(name, log, cap, select=None, **kw):
    text = read(log)
    if select:
        text = select(text)
    return fig(term(name, text, **kw), cap + " (rendered from evidence/logs/" + log + ")")


def h(t):
    return Paragraph(t, H)


def p(t):
    return Paragraph(t, B)


def bullets(items):
    return ListFlowable([ListItem(Paragraph(i, B)) for i in items], bulletType="bullet", start="-", leftIndent=12)


def code(path_or_text, is_path=True):
    t = open(os.path.join(ROOT, path_or_text)).read() if is_path else path_or_text
    return Preformatted(t.rstrip(), CODE)


def table(rows, widths):
    rows = [[Paragraph(str(c), B) for c in r] for r in rows]
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dde5ef")), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aab4c0")), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def tail_from(text, marker):
    i = text.find(marker)
    return text[i:] if i >= 0 else text


def build(fname, title, question, story):
    def page(c, d):
        c.saveState(); c.setFont("Helvetica", 8.5); c.setFillColor(colors.HexColor("#444444"))
        c.drawString(2 * cm, A4[1] - 1.1 * cm, "ENSP461 - DevOps & Automation | Lab 1: DevOps Foundations & Continuous Integration")
        c.drawString(2 * cm, A4[1] - 1.5 * cm, f"Name: {NAME}    Roll No.: {ROLL}    Environment: {ENV}")
        c.drawString(2 * cm, 1 * cm, title); c.drawRightString(A4[0] - 2 * cm, 1 * cm, f"Page {d.page}")
        c.restoreState()
    glued, i = [], 0
    while i < len(story):  # keep each heading on the same page as the block after it
        item = story[i]
        if isinstance(item, Paragraph) and item.style is H and i + 1 < len(story):
            nxt = story[i + 1]
            glued.append(KeepTogether([item] + (nxt._content if isinstance(nxt, KeepTogether) else [nxt])))
            i += 2
        else:
            glued.append(item)
            i += 1
    story = glued
    doc = SimpleDocTemplate(f"{OUT}/{fname}.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=1.6 * cm, title=title, author=NAME, subject="ENSP461 Lab 1")
    doc.build([Paragraph(title, ss["Heading1"]), Paragraph(question, Q), p(f"Repository: <a href='{REPO}' color='blue'>{REPO}</a>")] + story, onFirstPage=page, onLaterPages=page)


b = json.load(open(LOGS + "builds.json"))
dur = {x["number"]: round(x["duration"] / 1000) for x in b["builds"]}
git_log = subprocess.run(["git", "-C", ROOT, "log", "--graph", "--format=%h %ad %s", "--date=format:%Y-%m-%d %H:%M", "--all"], capture_output=True, text=True).stdout
PIPE_SHORT = lambda t: "\n".join(l for l in t.splitlines() if not l.startswith((" > ", "[Pipeline] }", "[Pipeline] //")))
WHY_DOCKER = "The lab host is an Ubuntu 24.04 Docker container booted with systemd, so Jenkins and the application run as real services. The container holds no GitHub credentials, so pushes were sent from the host machine using its existing GitHub login, while Jenkins pulls from the public repository."

OBS = {
 "q4": ["Git and Jenkins both installed from apt; the container's minimal image also needed python3-venv, curl and fontconfig.", "Global identity set with git config lives in ~/.gitconfig and applies to every repository for that user.", "Jenkins 2.580.2 was installed with OpenJDK 21, using the 2026 Jenkins repository signing key.", "The apt post-install step did not start Jenkins inside the container (policy-rc.d denied it), so the service was started with systemctl."],
 "q5": ["The feature branch kept main unchanged until the test suite passed.", "Merging with --no-ff keeps a merge commit, so the graph shows when the feature landed.", "An annotated tag marks the first tested release, v1.0.0.", "Output of the very first push was not captured. The later push log and git ls-remote output confirm the branch and tag on GitHub."],
 "q6": [f"Build 1 was started manually and finished with SUCCESS in about {dur.get(1,'?')} seconds.", "Pipeline script from SCM means the pipeline definition is versioned with the code it builds.", "Using a public HTTPS remote means Jenkins needs no stored Git credentials."],
 "q7": ["Declarative stages make failures easy to locate because each stage is reported separately.", "The junit step publishes test results even when tests fail because it runs in post { always }.", "In build 1 the first health probe failed while the service was starting, and the retry loop in the deploy script passed on a later attempt."],
 "q3": [f"Build 2 was started by an SCM change, without clicking Build Now, and finished in about {dur.get(2,'?')} seconds.", "After build 2 the /healthz endpoint reported release 1.1.0, confirming the new code went live.", "sudo for the jenkins user is limited to one root-owned script. That narrows the rule but is not a full security boundary, because the script still installs Python packages from the archive as root.", "One later poll took 58 seconds and logged a stack trace, with no effect on either build. The cause was not investigated, and later polls completed normally."],
}

with open(EV + "/observations.md", "w") as f:
    f.write("# Lab 1 Observations\n")
    for k in ("q4", "q5", "q6", "q7", "q3"):
        f.write(f"\n## {k.upper()}\n" + "".join(f"- {o}\n" for o in OBS[k]))

build("q4-install-configure-git-jenkins", "Question 4 - Install and configure Git and Jenkins", "Question 4: Install and configure Git on Ubuntu Linux, verify the installation, and set up global Git configuration (user name and email).", [
    h("Environment"), p(WHY_DOCKER),
    h("Commands and output"), logfig("q4-git", "q4-install.log", "Git install, version check and global configuration", select=lambda t: "\n".join(l for l in t.split("$ sudo apt-get install -y -qq openjdk")[0].splitlines() if "Reading database" not in l and not l.startswith(("Selecting", "Preparing", "Unpacking", "Setting up", "Processing", "debconf", "invoke-rc", "update-alternatives")))),
    logfig("q4-jenkins", "q4-install.log", "Jenkins repository key, install and package version", select=lambda t: "$ curl" + t.split("$ curl", 1)[1] if "$ curl" in t else t),
    shot("jenkins-dashboard", "Jenkins dashboard after setup"), shot("jenkins-plugins", "Installed Jenkins plugins"),
    h("Observations"), bullets(OBS["q4"])])

build("q5-version-control-git", "Question 5 - Set up version control using Git", "Question 5: Initialize a repository, stage and commit changes, create branches, merge branches, and push the repository to GitHub.", [
    h("Workflow"), logfig("q5-1", "q5-git-workflow.log", "init, stage, commit, branch, tests, merge, tag", max_lines=60),
    logfig("q5-2", "q5-push.log", "Pushes to GitHub, run from the host machine"),
    h("Commit history"), code(git_log, False), shot("github-commits", "Commits on GitHub"), shot("github-repo", "Public repository on GitHub"),
    h("Observations"), bullets(OBS["q5"])])

build("q6-basic-jenkins-pipeline", "Question 6 - Basic Jenkins CI/CD pipeline", "Question 6: Implement a basic Jenkins CI/CD pipeline that pulls source code from the GitHub repository and triggers an automated build.", [
    h("Job configuration"), p("Job text-stats-pipeline uses Pipeline script from SCM, with the public GitHub repository, branch */main and script path Jenkinsfile."), shot("job-config", "Pipeline job configuration"),
    h("Jenkins setup"), logfig("q6-setup", "q6-jenkins-setup.log", "Plugins, service unit and scoped sudo rule"),
    h("Build 1"), shot("build1-overview", "Build 1 summary"), shot("build1-console", "Build 1 console"),
    logfig("q6-console", "q6-q7-build1-console.log", "Build 1 console output, Git operations trimmed", select=PIPE_SHORT, max_lines=60),
    h("Observations"), bullets(OBS["q6"])])

build("q7-jenkinsfile-pipeline-stages", "Question 7 - Jenkinsfile pipeline stages", "Question 7: Create a Jenkinsfile defining pipeline stages (build, test, deploy) and demonstrate a declarative or scripted pipeline execution.", [
    h("Jenkinsfile (declarative pipeline)"), code("Jenkinsfile"),
    h("Stages"), table([["Stage", "Action", "Fails when"], ["Build", "Creates a venv and installs requirements", "A dependency cannot be installed"], ["Test", "Runs pytest and publishes JUnit results", "Any test fails"], ["Package", "Creates and archives a tarball", "Archive creation fails"], ["Deploy", "Installs the tarball, restarts the service, checks /healthz", "Health check fails after 15 attempts"]], [2.5 * cm, 8 * cm, 6.5 * cm]),
    h("Execution"), shot("job-stage-view", "Stage view for the pipeline"), shot("build1-pipeline-graph", "Pipeline graph of build 1"), shot("build1-tests", "Test results of build 1"),
    h("Observations"), bullets(OBS["q7"])])

build("q3-automate-deployment", "Question 3 - Automate application deployment", "Question 3: Automate application deployment using Jenkins by configuring build triggers, post-build actions, and deployment steps.", [
    h("Build trigger"), p("The Jenkinsfile declares pollSCM('H/2 * * * *'), so Jenkins checks GitHub about every two minutes."),
    logfig("q3-trigger", "q3-trigger.log", "Release change committed and tagged"), shot("polling-log", "Polling log of build 2: change found on main"),
    h("Post-build actions"), p("The pipeline archives the tarball with fingerprints, publishes JUnit results, and prints a success or failure message in its post block."),
    h("Deployment steps"), code("deploy/text-stats-deploy"), code("deploy/text-stats.service"),
    h("Automatic build and deployment"), shot("build2-overview", "Build 2 started by an SCM change"), shot("build2-console", "Build 2 console"),
    logfig("q3-verify", "q3-deploy-verify.log", "Service checks after builds 1 and 2"),
    h("Observations"), bullets(OBS["q3"])])

build("q2-cicd-workflow-report", "Question 2 - CI/CD workflow report", "Question 2: Prepare a CI/CD workflow report describing the pipeline architecture, stages, automation results, and observations with supporting screenshots.", [
    h("Objective"), p("Build and deploy a small Flask text statistics service through a Git and Jenkins workflow, with every change tested before release."),
    h("Tools and environment"), table([["Component", "Used"], ["Host", ENV], ["Source control", "Git, GitHub (public repository)"], ["CI/CD", "Jenkins 2.580.2 LTS, OpenJDK 21"], ["Application", "Python, Flask 3.1.0, pytest 8.3.4"], ["Runtime", "systemd service on port 5000"]], [5 * cm, 12 * cm]), p(WHY_DOCKER),
    h("Pipeline architecture"), code("git push\n  -> GitHub main\n  -> Jenkins pollSCM (H/2 * * * *)\n  -> Checkout -> Build -> Test (JUnit results) -> Package (archived tarball)\n  -> Deploy (/opt/text-stats, systemd restart, /healthz check)", False),
    h("Stages"), bullets(["Checkout: Jenkins pulls the Jenkinsfile and source from GitHub.", "Build: creates a venv and installs dependencies.", "Test: runs 5 pytest cases and publishes results.", "Package: archives text-stats-BUILD.tar.gz.", "Deploy: installs the archive, restarts the service and checks health."]),
    h("Automation results"), table([["Build", "Cause", "Result", "Duration", "Deployed"], ["1", "Manual (Build Now equivalent)", "SUCCESS", f"{dur.get(1,'?')} s", "1.0.0"], ["2", "SCM change", "SUCCESS", f"{dur.get(2,'?')} s", "1.1.0"]], [1.5 * cm, 6.5 * cm, 3 * cm, 3 * cm, 3 * cm]),
    h("Evidence"), shot("job-stage-view", "Stage view"), shot("build2-overview", "Automatic build"),
    h("Observations"), bullets(OBS["q6"] + OBS["q3"][:2]),
    h("Conclusion"), p("A push to main now reaches the running service without manual steps, and a failing test or health check stops the pipeline with a visible failure.")])

all_figs = [
    h("Commit history"), code(git_log, False),
    h("Git installation and configuration (Q4)"), fig(SHOTS + "term-q4-git.png", "Git setup"),
    h("Jenkins installation (Q4)"), fig(SHOTS + "term-q4-jenkins.png", "Jenkins install"), shot("jenkins-dashboard", "Dashboard"),
    h("Version control workflow (Q5)"), fig(SHOTS + "term-q5-1.png", "Git workflow"), fig(SHOTS + "term-q5-2.png", "Pushes"),
    h("Pipeline job and execution (Q6, Q7)"), shot("job-config", "Job configuration"), shot("job-stage-view", "Stage view"), fig(SHOTS + "term-q6-console.png", "Build 1 console"),
    h("Automated deployment (Q3)"), shot("polling-log", "Polling log"), shot("build2-overview", "Build 2"), fig(SHOTS + "term-q3-verify.png", "Service checks"),
    h("Pipeline configuration"), code("Jenkinsfile"),
    h("Observations")] + [bullets(OBS[k]) for k in ("q4", "q5", "q6", "q7", "q3")]
build("q1-records", "Question 1 - Records of all experiments", "Question 1: Record all commands, pipeline configurations, screenshots, commit history, and observations for each experiment.", all_figs)
