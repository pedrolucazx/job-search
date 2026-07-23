# workflows/startup.md — Agent Session Startup

Run this workflow once, before the first job-search task in every new agent
session. It gives the candidate a consistent setup status without relying on
an interactive shell prompt.

## 1. Check without a terminal prompt

```bash
python3 scripts/check_setup.py --no-prompt
```

Always use `--no-prompt` here. Agent shell tools are commonly non-interactive,
so the agent owns the user-facing question in step 3.

## 2. If the environment is complete

Briefly tell the candidate that the environment is ready, then continue with
their requested task. Do not offer to reinstall already-present dependencies.

## 3. If dependencies are missing

Summarize the missing dependencies from the command output and ask exactly:

> Install all missing dependencies now?

Stop and wait for the candidate's answer. Installation changes the machine and
may request a sudo password, so never infer consent.

- If the candidate answers yes (`y` or `yes`), run:

  ```bash
  python3 scripts/check_setup.py --install
  ```

- If the candidate answers no, continue only when their requested task can run
  without the missing dependencies. Otherwise, explain which dependency blocks
  it and point them to `SETUP.md`.

## 4. Scope

Run this once per agent session, not once per command or turn. This startup
check never submits a job application and does not create or modify the
candidate profile.
