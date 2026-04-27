---
description: Pull, split staged work into topical commits, and push to origin
---

You are running the project's `/commit` workflow. Execute these steps in order. If any step fails, stop and report the failure to the user instead of continuing.

## 1. Pull from origin

- Run `git status -sb` and `git branch --show-current` to confirm the current branch and capture untracked/modified files.
- Run `git pull --ff-only origin <current-branch>`.
  - If the pull cannot fast-forward (diverged history), stop and ask the user how to proceed (rebase vs. merge). Do NOT auto-rebase or auto-merge.
  - If the pull introduces conflicts, stop and surface them.

## 2. Inspect the working tree

- Run `git status` and `git diff` (and `git diff --staged` if anything is already staged) to see every pending change.
- Read enough of the changed files to understand *what each change does*, not just which files moved. You need this to group commits well.
- Skip files that look like secrets (`.env`, credentials, key files). If you see any, stop and warn the user before doing anything else.

## 3. Group changes into topical commits

Decide whether the working tree contains one logical change or several. Bias toward **fewer, larger commits** — do not split for the sake of splitting.

Group by topic, not by file type or directory. Examples of a topic boundary:
- A bug fix vs. an unrelated feature touched in the same session.
- A refactor vs. behavior changes that ride on top of it.
- Scenario data updates (e.g. new `.rou.xml` / `.net.xml` for a date) vs. config/script edits.

Examples of things that should stay in **one** commit:
- A feature plus the config wiring it needs.
- Edits to a `.sumocfg` and the `additional-files` it references for the same scenario.
- A rename and the call-site updates that follow from it.

If everything belongs together, make one commit and move on.

## 4. Stage and commit each group

For each group:
1. Stage only that group's files explicitly by name (`git add <file> <file> …`). **Never** use `git add -A` or `git add .` — they sweep in unrelated changes and risk committing secrets.
2. Write a Conventional-Commits-style subject under ~70 chars. Pick the prefix that fits:
   - `feat: Introduce …` — new capability.
   - `fix: …` — bug fix.
   - `refactor: …` — restructuring without behavior change.
   - `docs: …` — docs only.
   - `chore: …` — tooling, configs, housekeeping.
   - `data: …` — scenario data updates (routes, networks, TL logic) when no behavior code changed.
3. If the change needs explanation beyond the subject, add a short body describing the *why*.
4. Commit with a HEREDOC so formatting is preserved:

   ```bash
   git commit -m "$(cat <<'EOF'
   feat: Introduce <thing>

   <optional body explaining why, if non-obvious>
   EOF
   )"
   ```

   Do not add Claude/Co-Authored-By trailers unless the user has previously asked for them.
5. After each commit, run `git status -s` to confirm the staging area is clean for that group before moving to the next.

If a pre-commit hook fails: fix the underlying issue, re-stage, and create a **new** commit. Never `--amend` to silence a hook, never pass `--no-verify`.

## 5. Push to origin

- Run `git push origin <current-branch>`.
- If the branch has no upstream set, use `git push -u origin <current-branch>`.
- If the push is rejected (non-fast-forward), stop and report — do not force-push.

## 6. Report

Print a concise summary: branch name, list of commit subjects created (in order), and the resulting `git status -sb`. Nothing else.

## Hard rules

- Never run `git add -A` / `git add .` / `git add *`.
- Never `--amend` an existing commit.
- Never `--no-verify`, `--no-gpg-sign`, or other hook/signature bypasses.
- Never `push --force` or `push --force-with-lease`.
- Never commit files that look like secrets without explicit user confirmation.
- Never invent changes that aren't in the diff just to justify a split.
