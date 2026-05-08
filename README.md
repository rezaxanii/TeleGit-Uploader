# 🚀 Telegram to GitHub Uploader Bot

> **Note:** The whole project was created with AI and vibe coding.

This bot is a professional bridge between Telegram and GitHub. It allows you to upload files or direct links to your GitHub repository, bypassing standard API limitations. Using the **Native Git Engine**, it handles large files by zipping and splitting them into 98MB parts.

---

## ✨ Features
*   **⚡ Native Git Engine:** Uses real Git commands for 100% stability.
*   **📦 Smart File Splitting:** Automatically splits files > 98MB into zipped parts.
*   **🚀 Optimized Upload:** Clones the repo once and pushes all parts in one batch.
*   **💤 24/7 Uptime:** FastAPI health check to keep Hugging Face awake.
*   **🛡 Secure:** Restricted to your Telegram User ID only.

---

## 🛠 Step 0: Prepare Your GitHub (The Foundation)

Before deploying the bot, you must set up your storage on GitHub:

### 1. Create a New Repository
*   Login to [GitHub](https://github.com).
*   Click the **+** icon (top right) -> **New repository**.
*   **Repository name:** Give it a name (e.g., `my-storage`).
*   **Public/Private:** You can choose either. (Private is safer for personal files).
*   **Initialize:** Check "Add a README file" (Important for the first clone).
*   Click **Create repository**.

### 2. Generate Personal Access Token (PAT)
*   Go to **Settings** (of your profile, not the repo).
*   Scroll down to **Developer settings** (left sidebar).
*   Click **Personal access tokens** -> **Tokens (classic)**.
*   Click **Generate new token (classic)**.
*   **Note:** Name it `MyBotToken`.
*   **Expiration:** Select "No expiration" or a long period.
*   **Scopes:** Check the **`repo`** box (this allows the bot to push files).
*   Click **Generate token** and **COPY IT**. (You won't see it again!).

---

## 🛠 Step 1: Gathering Telegram Credentials

1.  **API_ID & API_HASH:** Get them from [my.telegram.org](https://my.telegram.org) under "API development tools".
2.  **BOT_TOKEN:** Get it from [@BotFather](https://t.me/BotFather) by creating a new bot.
3.  **ALLOWED_USER_ID:** Send a message to [@userinfobot](https://t.me/userinfobot) to get your numerical ID.

---

## 🏗 Step 2: Deployment Options

### Option A: Hugging Face (Recommended & Free)
1.  Create a **New Space** on Hugging Face.
2.  Select **Blank (Python)** as the SDK.
3.  Go to **Settings > Variables and Secrets**.
4.  Add your credentials to the **Secrets** section (NOT Variables):
    *   `API_ID`
    *   `API_HASH`
    *   `BOT_TOKEN`
    *   `GITHUB_TOKEN` (The PAT you copied in Step 0).
    *   `GITHUB_REPO` (Your `username/repo-name`).
    *   `ALLOWED_USER_ID`
    *   `GH_BRANCH` (Usually `main`).

### Option B: Private Server (VPS)
1.  Clone the repo: `git clone <your-space-url>`.
2.  Install requirements: `pip install -r requirements.txt`.
3.  Set environment variables or use a `.env` file.
4.  Run: `python app.py`.

---

## 📦 Step 3: Project Files

Ensure these files are in your Space/Server:

1.  **`requirements.txt`**: Contains `GitPython`, `pyrogram`, `tgcrypto`, `requests`, `fastapi`, `uvicorn`, `PyGithub`.
2.  **`app.py`**: The core logic (Native Git + Telegram Client).

---

## 💤 Step 4: Setup 24/7 Monitoring

Hugging Face Spaces sleep after 48h of inactivity. To keep it alive:
1.  Set Space visibility to **Public** in Settings.
2.  Copy your **Direct URL** (e.g., `https://user-name-space-name.hf.space`).
3.  Add this URL to [UptimeRobot](https://uptimerobot.com) as an **HTTP(s) Monitor**.
4.  Set the interval to **5 minutes**.

---

## 📖 How to Use
1.  Open your bot in Telegram and click `/start`.
2.  **File Upload:** Send/Forward any document or video.
3.  **Link Upload:** Send a direct download URL.
4.  The bot will Zip (if needed) -> Split -> Git Push.
5.  Receive your **GitHub Raw Link** instantly.

---

## ⚠️ Security Note
*   **Privacy:** The bot only responds to YOUR ID. Other users cannot use your GitHub storage.
*   **Tokens:** Never hardcode tokens in `app.py`. Always use **Secrets**.

---
*Built with 🤖 and ☕.*
