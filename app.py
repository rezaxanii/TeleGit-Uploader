import os
import shutil
import zipfile
import requests
import asyncio
import threading
import git
import re
from pathlib import Path
from pyrogram import Client, filters
from github import Github
from fastapi import FastAPI
import uvicorn

# --- CONFIGURATION ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GH_TOKEN = os.getenv("GITHUB_TOKEN")
GH_REPO = os.getenv("GITHUB_REPO")
GH_BRANCH = os.getenv("GH_BRANCH", "main")
USER_ID = int(os.getenv("ALLOWED_USER_ID"))

CHUNK_SIZE = 98 * 1024 * 1024
DOWNLOAD_DIR = Path("downloads_tmp")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Git Config
os.system('git config --global user.email "bot@huggingface.co"')
os.system('git config --global user.name "HF-Bot"')

app = Client("github_uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
web_app = FastAPI()

@web_app.get("/")
@web_app.api_route("/", methods=["GET", "HEAD"])
def health():
    return {"status": "alive", "engine": "git-native-optimized"}

def run_web():
    uvicorn.run(web_app, host="0.0.0.0", port=7860)

# --- GITHUB ENGINE (UNTOUCHED) ---

def upload_to_github_optimized(file_list, github_folder):
    repo_dir = Path("repo_temp")
    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    auth_url = f"https://{GH_TOKEN}@github.com/{GH_REPO}.git"
    links = []

    try:
        cloned_repo = git.Repo.clone_from(auth_url, repo_dir, branch=GH_BRANCH, depth=1)

        for local_p in file_list:
            github_p = f"{github_folder}/{local_p.name}"
            dest_path = repo_dir / github_p
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy(local_p, dest_path)
            cloned_repo.index.add([github_p])

            raw_url = f"https://github.com/{GH_REPO}/raw/refs/heads/{GH_BRANCH}/{github_p}"
            links.append(raw_url)

        cloned_repo.index.commit(f"Upload: {len(file_list)} items")
        origin = cloned_repo.remote(name='origin')
        origin.push()

    finally:
        if repo_dir.exists():
            shutil.rmtree(repo_dir)

    return links

# --- NEW & IMPROVED UTILS ---

async def progress(current, total, status_msg, action):
    """Safe progress bar to avoid FloodWait"""
    percent = current * 100 / total
    
    if int(percent) % 25 == 0:
        try:
            await status_msg.edit(f"🚀 {action}: `{percent:.1f}%`\n📦 `{current / (1024*1024):.1f}MB` / `{total / (1024*1024):.1f}MB`")
        except:
            pass

def get_clean_filename(message=None, url=None):
    """Advanced filename detector for Music and Links"""
    if message and (message.document or message.video or message.audio or message.voice):
        media = message.document or message.video or message.audio or message.voice
        fname = getattr(media, 'file_name', None)
        if not fname and message.audio:
            fname = f"{message.audio.title or 'music'}.mp3"
        return fname or f"file_{message.id}"
    
    if url:
        try:
            with requests.get(url, stream=True, timeout=5) as r:
                cd = r.headers.get('content-disposition')
                if cd and 'filename=' in cd:
                    names = re.findall('filename\*?=["\']?(?:UTF-8\'\')?([^"\';]+)["\']?', cd)
                    if names: return requests.utils.unquote(names[0])
        except:
            pass
        name = url.split('/')[-1].split('?')[0]
        return requests.utils.unquote(name) if name else "file"
    return "file"

def split_file(file_path: Path):
    output_folder = file_path.parent / f"split_{file_path.stem}"
    output_folder.mkdir(exist_ok=True)
    zip_tmp = output_folder / f"{file_path.name}.zip"
    with zipfile.ZipFile(zip_tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(file_path, arcname=file_path.name)
    parts = []
    part_num = 1
    with open(zip_tmp, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk: break
            p_name = f"{file_path.name}.zip.{part_num:03d}"
            p_path = output_folder / p_name
            p_path.write_bytes(chunk)
            parts.append(p_path)
            part_num += 1
    zip_tmp.unlink()
    return output_folder, parts

# --- HANDLERS ---

@app.on_message(filters.user(USER_ID) & filters.command("start"))
async def start_handler(client, message):
    await message.reply(
        "👋 **Welcome to GitHub Uploader Bot!**\n\n"
        "I'm ready. You can:\n"
        "1️⃣ Send me any **File, Video, or Audio**.\n"
        "2️⃣ Send me a **Direct Download Link**.\n\n"
        "I will upload them to your GitHub repository automatically. 🚀"
    )

@app.on_message(filters.user(USER_ID) & (filters.document | filters.video | filters.audio | filters.text))
async def main_handler(client, message):
    if message.text and not message.text.startswith("http"): return

    status = await message.reply("⚡️ Initializing...")
    temp_path = None
    split_dir = None

    try:
        media = message.document or message.video or message.audio
        if media:
            fname = get_clean_filename(message)
            await status.edit(f"📥 Downloading: `{fname}`")
            temp_path = Path(DOWNLOAD_DIR / fname)
            await message.download(
                file_name=str(temp_path),
                progress=progress,
                progress_args=(status, "Downloading")
            )
        else:
            url = message.text
            fname = get_clean_filename(url=url)
            await status.edit(f"📥 Fetching Link: `{fname}`")
            temp_path = DOWNLOAD_DIR / fname
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(temp_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

        f_size = temp_path.stat().st_size

        if f_size <= CHUNK_SIZE:
            await status.edit("📤 Uploading to GitHub...")
            links = upload_to_github_optimized([temp_path], "downloads")
            formatted_links = f"🔗 {links[0]}"
        else:
            await status.edit("📦 Splitting & Zipping...")
            split_dir, parts = split_file(temp_path)
            await status.edit(f"📤 Uploading {len(parts)} parts...")
            links = upload_to_github_optimized(parts, f"downloads/{temp_path.stem}")
            formatted_links = "\n\n".join([f"🧩 Part {i+1}: {l}" for i, l in enumerate(links)])

        await status.edit(f"✅ **Upload Complete!**\n\n{formatted_links}", disable_web_page_preview=True)

    except Exception as e:
        await status.edit(f"❌ Error: `{str(e)}`")
    finally:
        if temp_path and temp_path.exists(): temp_path.unlink()
        if split_dir and split_dir.exists(): shutil.rmtree(split_dir)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    app.run()
