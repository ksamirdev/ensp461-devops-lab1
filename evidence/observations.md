# Lab 1 Observations

## Q4
- Git and Jenkins both installed from apt; the container's minimal image also needed python3-venv, curl and fontconfig.
- Global identity set with git config lives in ~/.gitconfig and applies to every repository for that user.
- Jenkins 2.580.2 was installed with OpenJDK 21, using the 2026 Jenkins repository signing key.
- The apt post-install step did not start Jenkins inside the container (policy-rc.d denied it), so the service was started with systemctl.

## Q5
- The feature branch kept main unchanged until the test suite passed.
- Merging with --no-ff keeps a merge commit, so the graph shows when the feature landed.
- An annotated tag marks the first tested release, v1.0.0.
- Output of the very first push was not captured. The later push log and git ls-remote output confirm the branch and tag on GitHub.

## Q6
- Build 1 was started manually and finished with SUCCESS in about 15 seconds.
- Pipeline script from SCM means the pipeline definition is versioned with the code it builds.
- Using a public HTTPS remote means Jenkins needs no stored Git credentials.

## Q7
- Declarative stages make failures easy to locate because each stage is reported separately.
- The junit step publishes test results even when tests fail because it runs in post { always }.
- In build 1 the first health probe failed while the service was starting, and the retry loop in the deploy script passed on a later attempt.

## Q3
- Build 2 was started by an SCM change, without clicking Build Now, and finished in about 7 seconds.
- After build 2 the /healthz endpoint reported release 1.1.0, confirming the new code went live.
- sudo for the jenkins user is limited to one root-owned script. That narrows the rule but is not a full security boundary, because the script still installs Python packages from the archive as root.
- One later poll took 58 seconds and logged a stack trace, with no effect on either build. The cause was not investigated, and later polls completed normally.
