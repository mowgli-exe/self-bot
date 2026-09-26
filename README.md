# Discord Selfbot

Selfbot with Rich Presence, public fun commands, auto-responder, and optional server cloning.

> **Warning:** Automating a user account violates [Discord's Terms of Service](https://discord.com/terms). Use at your own risk — accounts can be disabled.

---

## Features

- **Rich Presence** – custom status text + up to 2 buttons (`dc`, `guns`)
- **Public commands** – anyone in a shared channel can use them
- **Owner-only commands** – ban / unban auto-responder, server clone
- **Auto-responder** – replies when you are mentioned (with spam protection)
- **Random content** – cats, quotes, jokes, cuteness rating

---

## Commands

### Public (everyone)

| Command | Description |
|---------|-------------|
| `.ping` | Bot latency |
| `.donate` | Crypto donation addresses |
| `.cat` | Random cat image |
| `.quote` / `.qoute` | Random quote |
| `.joke` | Random joke (punchline spoilered) |
| `.rate` / `.rate @user` | Cuteness rating 0–100 |
| `.cmd` | Command list |

### Owner only

| Command | Description |
|---------|-------------|
| `.ban @user` | Block user from auto-responder |
| `.unban @user` | Unblock user |
| `.server <source_id>` | Clone roles & channels from another server into the **current** one |

---

## Setup

### 1. Requirements

- Python 3.10+
- A Discord user token (not a bot token)
- A Discord Application ID (for Rich Presence buttons)

### 2. Install

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```
git+https://github.com/dolfies/discord.py-self.git
aiohttp>=3.9.0
```

### 3. Configure

Edit `main.py`:

```python
MY_ID = 123456789012345678          # your Discord user ID
APPLICATION_ID = xxxx # from Discord Developer Portal
```

Set your token as an environment variable (never hardcode it):

```bash
export DISCORD_TOKEN="your_token_here"
```

### 4. Run

```bash
python main.py
```

---

## Deploy on Railway (24/7)

Railway runs the selfbot as a background worker so it stays online.

### Step 1 — GitHub repo

1. Create a new repository on GitHub
2. Upload these files to the **root** of the repo:
   - `main.py`
   - `requirements.txt`
   - `Procfile`
   - `README.md`
3. Make sure `Procfile` has **no file extension** and contains:

```
worker: python main.py
```

### Step 2 — Create Railway project

1. Go to [railway.app](https://railway.app) and sign in (GitHub login works)
2. Click **New Project**
3. Choose **Deploy from GitHub repo**
4. Select this repository
5. Railway will detect Python and start building

### Step 3 — Environment variable

1. Open your service on Railway
2. Go to **Variables**
3. Add:

| Key | Value |
|-----|-------|
| `DISCORD_TOKEN` | your Discord user token |

> Never put the token inside `main.py` or commit it to GitHub.

### Step 4 — Start command / process type

Railway should pick up the `Procfile` automatically (`worker: python main.py`).

If it does not:

1. Open **Settings** → **Deploy**
2. Set **Custom Start Command** to:

```
python main.py
```

### Step 5 — Deploy & check logs

1. Click **Deploy** (or push a new commit — Railway redeploys automatically)
2. Open the **Deployments** tab → latest deploy → **View Logs**
3. You should see something like:

```
Logged in as YourName#0000 (ID: ...)
Presence updated ...
Rich Presence loop started.
```

If you see `ERROR: DISCORD_TOKEN is missing` → the variable was not set correctly (Step 3).

### Step 6 — Keep it running

- Railway free/hobby plans can sleep inactive services. Prefer a **worker** service (no HTTP port needed).
- After code changes: push to GitHub → Railway rebuilds and restarts automatically.
- To force restart: Deployments → **Restart** or redeploy.

### Common Railway issues

| Problem | Fix |
|---------|-----|
| Build fails on `discord.py-self` | Use the git URL in `requirements.txt` (already set) |
| `DISCORD_TOKEN is missing` | Add the variable under **Variables**, then redeploy |
| Service exits immediately | Check logs; token may be invalid or revoked |
| No presence / no replies | Confirm logs show successful login; test with another account for buttons |
| Wrong start command | Set start command to `python main.py` |

---


## Rich Presence notes

- Buttons are **only visible to other users**, never on your own client
- You need a valid **Application ID** from the [Discord Developer Portal](https://discord.com/developers/applications)
- Presence is refreshed every 5 minutes so Discord does not drop it

Button links (edit in `main.py` if needed):

- `dc` → `https://discord.gg/36EAyW5Z4F`
- `guns` → `https://guns.lol/tpa`

---

## Server clone (`.server`)

1. Be a member of **both** servers (source + target)
2. Open a channel in the **target** (new) server
3. Run:

```
.server SOURCE_SERVER_ID
```

Copies roles, categories, text channels, and voice channels (best effort; large servers may hit rate limits).

---

## Project structure

```
├── main.py            # selfbot entry point
├── requirements.txt   # dependencies
├── Procfile           # Railway / process definition
└── README.md
```

---

## Disclaimer

This project is for educational purposes. Discord does not allow selfbots. The authors are not responsible for any account actions taken by Discord.
