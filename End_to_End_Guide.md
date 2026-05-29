# End-to-End Guide: SAST Pipeline with Cursor + GitHub Actions

---

## Overview

```
Your Machine (Cursor)  →  GitHub Repo  →  GitHub Actions  →  Security Tab
      ↑                                                            |
      └──────────── Fix findings with Cursor AI ←─────────────────┘
```

---

## Part 1 — One-Time Setup

### 1.1 Install Git

1. Go to https://git-scm.com/downloads
2. Download and run the installer for macOS
3. Verify in Terminal:
   ```bash
   git --version
   # Expected: git version 2.x.x
   ```

### 1.2 Configure Git with your identity

Open Terminal and run (use the email linked to your GitHub account):

```bash
git config --global user.name "Your Name"
git config --global user.email "dingtaotao1022@gmail.com"
```

### 1.3 Install Python

1. Go to https://www.python.org/downloads
2. Download Python 3.12 and install
3. Verify:
   ```bash
   python3 --version
   # Expected: Python 3.12.x
   ```

### 1.4 Verify Cursor is installed

Open Cursor. If not installed: https://cursor.com/download

---

## Part 2 — Open the Project in Cursor

### 2.1 Open the folder

1. Open Cursor
2. Go to **File → Open Folder**
3. Navigate to: `Desktop → SAST → SAST in CICD`
4. Click **Open**

You should see these files in the left sidebar:
```
SAST in CICD/
├── .github/workflows/sast.yml
├── app.py
├── .bandit
├── .pre-commit-config.yaml
├── requirements.txt
└── SAST_Pipeline_Guide.md
```

### 2.2 Explore the demo vulnerable app

Click `app.py` to open it. You'll see 5 intentional security issues:

| Line | Issue | Tool that catches it |
|------|-------|---------------------|
| ~14 | SQL Injection | Bandit, Semgrep, CodeQL |
| ~22 | Command Injection (`shell=True`) | Bandit, Semgrep |
| ~28 | Weak hashing (MD5) | Bandit, Semgrep |
| ~33 | Hardcoded secret | Bandit, Semgrep |
| ~39 | Insecure random | Bandit |

---

## Part 3 — Create a GitHub Repository

### 3.1 Sign in to GitHub

Go to https://github.com and sign in (or create a free account if you don't have one).

### 3.2 Create a new repo

1. Click the **+** icon (top-right) → **New repository**
2. Fill in:
   - **Repository name**: `sast-demo`
   - **Description**: `SAST pipeline demo with Bandit, Semgrep, CodeQL, pip-audit`
   - **Visibility**: ✅ **Public** *(required for free CodeQL and Security tab)*
   - **Initialize this repository**: leave **unchecked**
3. Click **Create repository**
4. On the next page, copy the HTTPS URL — it looks like:
   ```
   https://github.com/YOUR_USERNAME/sast-demo.git
   ```
   Keep this tab open.

---

## Part 4 — Connect Cursor to GitHub

### 4.1 Open the Terminal inside Cursor

In Cursor: **Terminal → New Terminal** (or press `` Ctrl+` ``)

A terminal opens at the bottom of Cursor, already pointed at your project folder.

### 4.2 Initialize Git

```bash
git init
git add .
git commit -m "Initial commit: SAST pipeline setup"
```

Expected output:
```
[main (root-commit) abc1234] Initial commit: SAST pipeline setup
 5 files changed, ...
```

### 4.3 Push to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/sast-demo.git
git branch -M main
git push -u origin main
```

You'll be prompted for your GitHub credentials:
- **Username**: your GitHub username
- **Password**: use a **Personal Access Token**, NOT your account password

> **How to create a Personal Access Token:**
> 1. GitHub → top-right avatar → **Settings**
> 2. Left sidebar → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
> 3. Click **Generate new token (classic)**
> 4. Give it a name, set expiry, check **repo** scope
> 5. Click **Generate token** — copy it immediately (shown only once)
> 6. Paste this token as your password in the terminal prompt

After a successful push, go back to your GitHub repo page and refresh — all files should be there.

---

## Part 5 — Watch the SAST Pipeline Run

### 5.1 Open the Actions tab

1. Go to your GitHub repo: `https://github.com/YOUR_USERNAME/sast-demo`
2. Click the **Actions** tab

You'll see a workflow run called **"SAST Pipeline"** that started automatically when you pushed.

### 5.2 Monitor the jobs

Click the workflow run to see 5 jobs:

```
bandit    ● Running  ~30s
semgrep   ● Running  ~1min
codeql    ● Running  ~4min
pip-audit ● Running  ~20s
sast-gate ⏳ Waiting (depends on all above)
```

- Green ✅ = passed (no findings or findings below threshold)
- Red ❌ = findings detected

Click any job to see live logs.

### 5.3 Enable the Security tab

1. Repo → **Settings** → **Code security and analysis**
2. Under **Code scanning** → click **Enable**

After the pipeline finishes, go to **Security → Code scanning** to see all findings.

---

## Part 6 — View SAST Findings

### 6.1 In the Security tab

Go to: `https://github.com/YOUR_USERNAME/sast-demo/security/code-scanning`

Each finding shows:
- **Tool**: Bandit / Semgrep / CodeQL
- **File and line number**: e.g., `app.py line 14`
- **Severity**: Critical / High / Medium / Low
- **Description**: what the issue is and why it's dangerous
- **Remediation hint**: how to fix it

### 6.2 Download raw reports

1. Actions tab → click the workflow run
2. Scroll to the bottom → **Artifacts**
3. Download:
   - `bandit-report` → JSON with all Bandit findings
   - `pip-audit-report` → JSON with dependency CVEs

---

## Part 7 — Fix Vulnerabilities Using Cursor AI

### 7.1 Fix SQL Injection (line ~14)

In Cursor, open `app.py`. Select the `get_user` function (lines 13–18).

Press **Cmd+K** and type:
> *Fix this SQL injection by using parameterized queries*

Cursor will rewrite it to something like:
```python
def get_user(username: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchall()
```

### 7.2 Fix Command Injection (line ~22)

Select the `run_ping` function, press **Cmd+K**:
> *Fix the command injection — avoid shell=True and sanitize input*

### 7.3 Fix MD5 hashing (line ~28)

Select the `hash_password` function, press **Cmd+K**:
> *Replace MD5 with a secure password hashing approach*

### 7.4 Fix hardcoded secret (line ~33)

Select the `SECRET_KEY` line, press **Cmd+K**:
> *Move this hardcoded secret to an environment variable*

### 7.5 Fix insecure random (line ~39)

Select the `generate_token` function, press **Cmd+K**:
> *Replace random.randint with a cryptographically secure alternative*

### 7.6 Use Cursor chat for explanations

If you want to understand a finding before fixing it:

1. Copy the finding text from GitHub Security tab
2. Open Cursor chat: **Cmd+L**
3. Paste and ask:
   > *"Explain this Bandit finding and show me the secure fix: [paste finding]"*

---

## Part 8 — Push Fixes and Re-run the Pipeline

After fixing vulnerabilities in Cursor:

### 8.1 Commit and push from Cursor's terminal

```bash
git add app.py
git commit -m "fix: resolve SAST findings (SQLi, command injection, MD5, hardcoded secret, insecure random)"
git push origin main
```

### 8.2 Watch the pipeline re-run

Go to GitHub → **Actions** — a new run starts automatically.

With the fixes applied, Semgrep and Bandit should pass (green ✅), and the `sast-gate` should go green, meaning the code is safe to merge.

---

## Part 9 — Test the PR Gate (Blocking a Merge)

This shows SAST acting as a quality gate on pull requests.

### 9.1 Create a new branch in Cursor's terminal

```bash
git checkout -b feature/add-new-endpoint
```

### 9.2 Add a new vulnerability intentionally

In `app.py`, add this insecure function at the bottom:

```python
def execute_query(query: str):
    conn = sqlite3.connect("users.db")
    # ❌ SQL injection — for demo purposes
    conn.execute(query)
```

### 9.3 Push the branch and open a PR

```bash
git add app.py
git commit -m "feat: add execute_query endpoint"
git push origin feature/add-new-endpoint
```

Then on GitHub:
1. Click **Compare & pull request**
2. Open the PR
3. Watch the checks at the bottom of the PR — the SAST pipeline runs
4. Because of the new SQL injection, **`sast-gate` will fail with ❌**
5. GitHub blocks the **Merge pull request** button

This is the full SAST gate in action: bad code cannot be merged.

---

## Part 10 — Local Pre-commit Hooks (prevent issues before CI)

Set this up once to catch issues *before* they ever reach GitHub:

```bash
# In Cursor's terminal
pip3 install pre-commit
pre-commit install
```

Now every `git commit` automatically runs Bandit, Semgrep, and pip-audit. If anything fails, the commit is blocked locally.

Test it:
```bash
pre-commit run --all-files
```

---

## Full Workflow Summary

```
1. Write code in Cursor
       ↓
2. git commit  →  pre-commit hooks run (Bandit, Semgrep, pip-audit locally)
       ↓ (if hooks pass)
3. git push  →  GitHub Actions triggers SAST Pipeline
       ↓
4. 4 SAST jobs run in parallel (Bandit, Semgrep, CodeQL, pip-audit)
       ↓
5. sast-gate evaluates all results
       ↓
   ✅ All pass → PR can be merged
   ❌ Any fail → PR is blocked → view findings in Security tab
       ↓
6. Copy finding → Cursor AI (Cmd+K or Cmd+L) → fix code → push again
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password repeatedly | Set up a credential helper: `git config --global credential.helper osxkeychain` |
| CodeQL takes too long | Normal — first run is 3–5 min. Subsequent runs are faster. |
| Security tab not showing findings | Make sure Code Scanning is enabled in repo Settings |
| Semgrep fails with rate limit | Add `SEMGREP_APP_TOKEN` as a GitHub secret (free at semgrep.dev) |
| pre-commit: command not found | Run `pip3 install pre-commit` and restart the terminal |
