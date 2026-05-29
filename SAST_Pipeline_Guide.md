# Step-by-Step: Create a GitHub Project and Run the SAST Pipeline

---

## Prerequisites

Install these tools on your machine before starting:

| Tool | Install command |
|------|----------------|
| Git | https://git-scm.com/downloads |
| Python 3.10+ | https://www.python.org/downloads |
| GitHub CLI (optional but handy) | `brew install gh` (macOS) or https://cli.github.com |

---

## Step 1 — Create a New Repository on GitHub

1. Go to [https://github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name**: e.g., `sast-demo`
   - **Visibility**: `Public` *(required for free CodeQL scanning; private repos need GitHub Advanced Security)*
   - Leave "Initialize this repository" **unchecked** — you'll push your local files
3. Click **Create repository**
4. Copy the HTTPS URL shown on the next page, e.g.:
   ```
   https://github.com/YOUR_USERNAME/sast-demo.git
   ```

---

## Step 2 — Initialize Your Local Project

Open a terminal and navigate to the `SAST in CICD` folder (where the files from this session live):

```bash
cd "/Users/taotaoding/Desktop/SAST/SAST in CICD"
```

Initialize Git and make the first commit:

```bash
git init
git add .
git commit -m "Initial commit: add SAST pipeline and demo app"
```

---

## Step 3 — Push Files to GitHub

Connect your local repo to GitHub and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/sast-demo.git
git branch -M main
git push -u origin main
```

> Replace `YOUR_USERNAME` with your actual GitHub username.

After the push, refresh your GitHub repo page — you should see all the files including `.github/workflows/sast.yml`.

---

## Step 4 — Watch the Pipeline Run

The push automatically triggers the workflow. To watch it:

1. Go to your repo on GitHub
2. Click the **Actions** tab at the top
3. You'll see a workflow run called **"SAST Pipeline"** in progress
4. Click it to expand — you'll see 5 jobs running in parallel:
   - `bandit`
   - `semgrep`
   - `codeql`
   - `pip-audit`
   - `sast-gate` (waits for the others)

Each job shows live logs. Click any job to drill into its steps.

> **First run tip:** CodeQL takes 3–5 minutes. Bandit and pip-audit finish in under 1 minute.

---

## Step 5 — Enable GitHub Code Scanning (for SARIF results)

Bandit and Semgrep upload findings as SARIF files to GitHub's Security tab. To see them:

1. Go to your repo → **Settings** → **Code security and analysis**
2. Under **Code scanning**, click **Enable**
3. That's it — no extra config needed. Results appear automatically after the first workflow run.

---

## Step 6 — View SAST Findings

### In the Security tab (recommended)
1. Repo → **Security** → **Code scanning**
2. Each finding shows:
   - File name and line number
   - Severity (Critical / High / Medium / Low)
   - Which tool found it (Bandit, Semgrep, or CodeQL)
   - A description and remediation hint

### In the Actions artifacts
1. Repo → **Actions** → click the workflow run
2. Scroll to **Artifacts** at the bottom
3. Download `bandit-report` or `pip-audit-report` for raw JSON output

---

## Step 7 — Test the Gate: Create a Pull Request

The `sast-gate` job is designed to block merges when findings exist. Try it:

1. Create a new branch:
   ```bash
   git checkout -b add-feature
   ```
2. Make any small change to `app.py` (e.g., add a comment)
3. Push and open a PR:
   ```bash
   git add app.py
   git commit -m "test: trigger SAST on PR"
   git push origin add-feature
   ```
4. Go to GitHub → **Pull requests** → open the PR
5. The pipeline runs again. Because `app.py` contains vulnerabilities, Semgrep will fail, and the **`sast-gate` check will block the merge** with a red ❌.

This is SAST in CI/CD working as intended.

---

## Step 8 — Fix a Vulnerability and Re-run

Let's fix the MD5 password hashing issue in `app.py`:

**Before (line ~28):**
```python
return hashlib.md5(password.encode()).hexdigest()
```

**After:**
```python
import secrets
salt = secrets.token_bytes(16)
return hashlib.sha256(salt + password.encode()).hexdigest()
```

Commit and push:
```bash
git add app.py
git commit -m "fix: replace MD5 with SHA-256 + salt"
git push origin add-feature
```

The pipeline reruns. One fewer finding — one step closer to a green gate.

---

## Step 9 — Set Up Local Pre-commit Hooks (optional but recommended)

Catch issues *before* they hit CI:

```bash
pip install pre-commit
pre-commit install
```

Now every `git commit` automatically runs Bandit, Semgrep, and pip-audit locally. If any check fails, the commit is blocked and you see the findings immediately in your terminal.

To run all hooks manually (without committing):
```bash
pre-commit run --all-files
```

---

## Summary: What You Now Have

```
SAST in CICD/
├── .github/
│   └── workflows/
│       └── sast.yml          ← GitHub Actions pipeline (4 SAST tools + gate)
├── app.py                    ← Demo app with intentional vulnerabilities
├── .bandit                   ← Bandit configuration
├── .pre-commit-config.yaml   ← Local pre-commit hooks
└── requirements.txt          ← Scanned by pip-audit for CVEs
```

| Tool | What it catches | Where results appear |
|------|----------------|----------------------|
| Bandit | Python-specific issues (injection, crypto, secrets) | Security tab + artifact |
| Semgrep | OWASP Top 10, broad rule set | Security tab |
| CodeQL | Deep semantic bugs, data-flow issues | Security tab |
| pip-audit | Dependency CVEs | Artifact (JSON) |

---

## Troubleshooting

**CodeQL fails with "no source code found"**
→ Make sure your repo has at least one `.py` file at the root level. `app.py` satisfies this.

**Semgrep exits non-zero and blocks the pipeline**
→ This is expected — `app.py` has real findings. Fix the vulnerabilities or remove `--error` from the Semgrep step to make it advisory-only.

**SARIF upload fails on a private repo**
→ Private repos require GitHub Advanced Security (paid). Either make the repo public or remove the `upload-sarif` steps and rely on the artifact JSON reports instead.

**pip-audit can't find requirements.txt**
→ Make sure `requirements.txt` exists at the repo root and has at least one package listed.
