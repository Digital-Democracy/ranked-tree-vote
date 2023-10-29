import base64
import tempfile

from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv_vault import load_dotenv

load_dotenv()

from utils import request


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        await join(update, context)
    else:
        data = {
            'telegramUserId': update.effective_user.id
        }

        output_president_init = request.post("/citizen/v1/citizens/president/init", data=data)

        await update.message.reply_text(
            f"Hi, {update.effective_user.full_name} here is link to invite tenants from you block of apartments and QR "
            f"code what you can print:\n"
        )

        await update.message.reply_text(f"{output_president_init['url']}")

        base64_img = output_president_init['qrCode'].replace("data:image/png;base64,", "")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            binary_data = base64.b64decode(base64_img)
            temp_file.write(binary_data)

        with open(temp_file.name, 'rb') as photo:
            await update.message.reply_photo(
                photo=InputFile(photo),
                caption="QR code what you can print"
            )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = {
        'telegramUserId': update.effective_user.id,
        'blockId': context.args[0]
    }

    output_join_block = request.post("/citizen/v1/citizens/tenant/login", data=data)

    await update.message.reply_text(
        f"Hi, {update.effective_user.full_name} you joined to block of apartments\n"
        f"Block id: {output_join_block['blockId']}\n"
    )


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    output_exit_block = request.delete("/citizen/v1/citizens/tenant/logout?telegramUserId={}".format(update.effective_user.id))

    await update.message.reply_text(
        f"Hi, {update.effective_user.full_name} you exit from block of apartments\n"
        f"Block id: {output_exit_block['blockId']}\n"
    )


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    output_delete_block = request.delete("/citizen/v1/citizens/president/delete?telegramUserId={}".format(update.effective_user.id))

    await update.message.reply_text(
        f"Hi, {update.effective_user.full_name} you delete block of apartments\n"
        f"Block id: {output_delete_block['blockId']}\n"
    )


app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(CommandHandler("logout", logout))

app.run_polling()
