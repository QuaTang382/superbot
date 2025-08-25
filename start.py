import asyncio
import os
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ======= CONFIG =======
TOKEN = "8440205431:AAGthcmlLZRe_TYufKXKKDUDV2rXSVvD5fg"
ADMIN_ID = 6132441793  # thay id admin
RUNNING = True
current_process = None

# ======= COMMANDS =======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not RUNNING:
        return
    user = update.effective_user
    await update.message.reply_text(
        f"Xin chào {user.first_name}, tôi là Bot Virus make bởi GHuy"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not RUNNING:
        return
    help_text = """
Lệnh có sẵn:
  /cau - chạy bash cau.sh
  /craft - chạy bash Tiger.sh
  Chỉ Admin👑:
  /stopbot - dừng bot
  /startbot - bật lại bot
"""
    await update.message.reply_text(help_text)

async def run_bash(update: Update, context: ContextTypes.DEFAULT_TYPE, script: str):
    global current_process, RUNNING
    if not RUNNING:
        return

    if current_process:
        await update.message.reply_text("Đang chạy tool khác,Vui lòng đợi")
        return

    # track file trước khi chạy
    before_files = set(os.listdir("."))

    async def run():
        global current_process
        proc = await asyncio.create_subprocess_shell(
            f"bash {script}",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        current_process = proc

        buffer = ""
        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                buffer += line.decode()
                # gửi mỗi 1s thay vì từng dòng
                if len(buffer) > 0:
                    await asyncio.sleep(1)
                    await update.message.reply_text(buffer.strip(), reply_to_message_id=update.message.message_id)
                    buffer = ""

            if buffer.strip():
                await update.message.reply_text(buffer.strip(), reply_to_message_id=update.message.message_id)

            await proc.wait()
        finally:
            current_process = None

            # so sánh file mới
            after_files = set(os.listdir("."))
            new_files = after_files - before_files

            for file in new_files:
                if os.path.isfile(file):
                    try:
                        await update.message.reply_document(InputFile(file))
                    except:
                        pass

    asyncio.create_task(run())

async def cau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_bash(update, context, "cau.sh")

async def craft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_bash(update, context, "Tiger.sh")

async def stopbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global RUNNING
    if update.effective_user.id == ADMIN_ID:
        RUNNING = False
        await update.message.reply_text("Bot đã tắt❌")
    else:
        await update.message.reply_text("Chỉ Admin mới có thể sử dụng lệnh")

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global RUNNING
    if update.effective_user.id == ADMIN_ID:
        RUNNING = True
        await update.message.reply_text("Bot đã bật✅")
    else:
        await update.message.reply_text("Chỉ Admin mới có thể sử dụng lệnh!")

async def user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_process, RUNNING
    if not RUNNING:
        return
    if current_process:
        text = update.message.text + "\n"
        current_process.stdin.write(text.encode())
        await current_process.stdin.drain()

# ======= MAIN =======
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("cau", cau))
    app.add_handler(CommandHandler("craft", craft))
    app.add_handler(CommandHandler("stopbot", stopbot))
    app.add_handler(CommandHandler("startbot", startbot))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_input))

    app.run_polling()

if __name__ == "__main__":
    main()