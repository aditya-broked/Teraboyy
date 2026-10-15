import os
import re
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from TeraboxDL import TeraboxDL

# ========== CONFIG ==========
API_ID = int(os.getenv("API_ID", "29191555"))          # ⬅️ apna API_ID daalo
API_HASH = os.getenv("API_HASH", "25402074cabd0d3d3791da81262c100f")    # ⬅️ apna API_HASH daalo
BOT_TOKEN = os.getenv("BOT_TOKEN", "8662284438:AAEh0IeQA6-yk99JyOmFjbTnhBnsnLiuK98") # ⬅️ apna BOT_TOKEN daalo

TERABOX_COOKIE = "browserid=DG0rMBqMXo5tOCWhdcVSVc7aZNShFudCuaiQk4q7sSfqnHbMntS3VRrx28k=; lang=en; TSID=uQRMDXuUI6aWYvGeemG62tJ5BbvAoUqz; __bid_n=1a1401a1a69252777b4207; _fwb=182BNwQfLHmVaIMJoQSqcS8.1792076815726; _fbp=fb.1.1792076816416.200658328834045448; _pin_unauth=dWlkPVlXRmtOakl3WW1ZdE5qZGpZaTAwT0dVekxXRmlOR0l0WlRCbFpHWXhNRFZsT0ROag; _tt_enable_cookie=1; _ttp=01M501M83V7AHNTJDCBPG23A0E_.tt.1.1792076816508; afUserId=7ed32737-d4a3-4095-8855-2ee0ccb030b9-p; AF_SYNC=1792076817392; _clck=5sx60s%5E2%5Egab%5E1%5E2479; ndus=YqDrHXupeHuiT3Qs2m0oyLA3CrytaD259N7Inlc1; _uetsid=11405b70c8aa11f18ca4d5e6da83f46e; _uetvid=11420bc0c8aa11f180af8152ddd48852; ttcsid_D733S1BC77U8D7C8BCKG=1792076816519::jJRfthlyuZSlaAJdzJpp.1.1792076989127.1; ttcsid=1792076816520::WP-Yl90IXHwyRblCUqER.1.1792076989127.0::1.162962.154365::170677.5.72.222::0.0.0; csrfToken=7SWhRFq5VuYZOa_IPp7fXaMR; ndut_fmt=96979D5E1827D53360BDB6F67EF91C3B37F6241B573447CC9FED00E913298389; ndut_fmv=f2708cadbfb74948c3cd49cdbb7562ac27e33ed2565b7d8c88adf6aebacd9e826081404f4a745609a08302eb1eb5cba0d2b110cfb9a4d112bee205432a4acf1d53babeab46c9fbdba5ab261641271a33a9def4dc0b3eed832a390311d9c9ec94b0a54c37b3c1b21a7e8b0149c9b70a7b"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pyrogram client
app = Client(
    "TeraboxBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# TeraboxDL instance
terabox = TeraboxDL(TERABOX_COOKIE)

# Telegram ki limit
TELEGRAM_LIMIT = 2000 * 1024 * 1024  # 2GB

# ========== HELPERS ==========
def extract_terabox_link(text: str):
    """Text se Terabox link nikaalo (sabhi formats support)"""
    patterns = [
        # Standard /s/ format
        r'https?://(?:www\.)?terabox\.com/s/[\w-]+',
        r'https?://(?:www\.)?1024terabox\.com/s/[\w-]+',
        r'https?://(?:www\.)?terabox\.club/s/[\w-]+',
        r'https?://(?:www\.)?terabox\.app/s/[\w-]+',
        r'https?://(?:www\.)?terabox\.link/s/[\w-]+',
        r'https?://(?:www\.)?teraboxapp\.com/s/[\w-]+',
        r'https?://(?:www\.)?4funbox\.co/s/[\w-]+',
        r'https?://(?:www\.)?4funbox\.com/s/[\w-]+',
        r'https?://(?:www\.)?mirrobox\.com/s/[\w-]+',
        r'https?://(?:www\.)?nephobox\.com/s/[\w-]+',
        r'https?://(?:www\.)?momerybox\.com/s/[\w-]+',
        r'https?://(?:www\.)?tibibox\.com/s/[\w-]+',
        r'https?://(?:www\.)?freeterabox\.com/s/[\w-]+',
        # sharing/link format with surl parameter
        r'https?://(?:www\.)?terabox\.com/sharing/link\?surl=[\w-]+',
        r'https?://(?:www\.)?1024terabox\.com/sharing/link\?surl=[\w-]+',
        r'https?://(?:www\.)?teraboxapp\.com/sharing/link\?surl=[\w-]+',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

async def progress_callback(current, total, message: Message, action: str):
    """Download/Upload progress update (har 5% pe)"""
    if total == 0:
        return
    percent = current * 100 / total
    if int(percent) % 5 == 0:
        try:
            await message.edit_text(
                f"**{action}...**\n"
                f"Progress: `{percent:.1f}%`\n"
                f"({current / 1024 / 1024:.1f} MB / {total / 1024 / 1024:.1f} MB)"
            )
        except Exception:
            pass

# ========== BOT ==========
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "**👋 Namaste! Main Terabox Downloader Bot hoon.**\n\n"
        "Mujhe koi bhi Terabox link bhejo, main download karke tumhe bhej dunga.\n\n"
        "**✅ 2GB tak ki video support**\n\n"
        "**Supported domains:**\n"
        "terabox.com, 1024terabox.com, terabox.club, terabox.app, terabox.link, teraboxapp.com, 4funbox.co, momerybox.com, tibibox.com"
    )

@app.on_message(filters.text & filters.private)
async def handle_link(client: Client, message: Message):
    # Debug logging
    logger.info(f"📨 Message received: {message.text}")

    url = extract_terabox_link(message.text)
    if not url:
        logger.info(f"❌ No link matched for: {message.text}")
        await message.reply_text(
            "❌ Bhai, sahi Terabox link bhejo.\n\n"
            "**Example:**\n"
            "`https://terabox.com/s/abc123`\n"
            "`https://teraboxapp.com/s/abc123`\n"
            "`https://1024terabox.com/s/abc123`"
        )
        return

    logger.info(f"✅ Link extracted: {url}")
    status_msg = await message.reply_text("🔍 Link check kar raha hoon...")

    try:
        file_info = terabox.get_file_info(url)
        logger.info(f"📁 File info: {file_info}")

        if "error" in file_info:
            await status_msg.edit_text(f"❌ **File info error:**\n`{file_info['error']}`")
            return

        file_name = file_info.get("file_name", "video.mp4")
        file_size = file_info.get("sizebytes", 0) or file_info.get("file_size", 0)
        download_link = file_info.get("download_link")

        if not download_link:
            await status_msg.edit_text(
                "❌ Download link nahi mila.\n\n"
                "**Possible reasons:**\n"
                "• Cookie expire ho gayi\n"
                "• Link private hai\n"
                "• Link invalid hai"
            )
            return

        if file_size > TELEGRAM_LIMIT:
            await status_msg.edit_text(
                f"⚠️ **File bahut badi hai:**\n"
                f"`{file_name}`\n"
                f"Size: {file_size / 1024 / 1024:.2f} MB\n"
                f"Telegram ki limit: 2000 MB\n\n"
                f"**Direct Download Link:**\n{download_link}"
            )
            return

        await status_msg.edit_text(
            f"⬇️ **Download ho raha hai:**\n`{file_name}`\n"
            f"Size: {file_size / 1024 / 1024:.2f} MB\n\nWait karo..."
        )

        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        loop = asyncio.get_event_loop()

        def sync_progress(downloaded, total, percentage=None):
            asyncio.run_coroutine_threadsafe(
                progress_callback(downloaded, total, status_msg, "Download ho raha hai"),
                loop
            )

        result = await loop.run_in_executor(
            None,
            lambda: terabox.download(
                file_info,
                save_path=download_dir,
                callback=sync_progress
            )
        )

        logger.info(f"📥 Download result: {result}")

        if "error" in result:
            await status_msg.edit_text(f"❌ **Download error:**\n`{result['error']}`")
            return

        file_path = result.get("file_path") or result.get("filepath")
        if not file_path or not os.path.exists(file_path):
            await status_msg.edit_text("❌ File download nahi hui. Dobara try karo.")
            return

        await status_msg.edit_text("✅ **Download pura!**\n\n📤 Telegram pe bhej raha hoon...")

        caption = f"🎬 **{file_name}**\n📦 Size: {file_size / 1024 / 1024:.2f} MB"

        try:
            await message.reply_video(
                video=file_path,
                caption=caption,
                progress=progress_callback,
                progress_args=(status_msg, "Telegram pe bhej raha hoon")
            )
        except Exception as e:
            logger.warning(f"send_video failed, trying send_document: {e}")
            await message.reply_document(
                document=file_path,
                caption=caption,
                progress=progress_callback,
                progress_args=(status_msg, "Telegram pe bhej raha hoon")
            )

        await status_msg.edit_text("🎉 **Success!** File bhej di.\n\nAb Telegram me dekh bhi sakte ho aur download bhi kar sakte ho.")

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ **Error aa gaya:**\n`{str(e)}`")

# ========== RUN ==========
if __name__ == "__main__":
    logger.info("🚀 Bot start ho raha hai...")
    app.run()