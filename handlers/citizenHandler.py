import base64
import tempfile

from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import request, i18n
import os

from dotenv_vault import load_dotenv

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        await join(update, context)
    else:
        output_president_init = request.post("/citizen/v1/citizens/president/init", data={
            'telegramUserId': update.effective_user.id,
            'telegramUserName': update.effective_user.username,
        })

        await update.message.reply_text(
            i18n(update.effective_user.language_code)("start", full_name=update.effective_user.full_name)
        )

        base64_img = output_president_init['qrCode'].replace("data:image/png;base64,", "")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            binary_data = base64.b64decode(base64_img)
            temp_file.write(binary_data)

        await update.effective_message.reply_chat_action("upload_photo")
        with open(temp_file.name, 'rb') as photo:
            await update.message.reply_photo(
                photo=InputFile(photo),
                caption=f"{output_president_init['url']}"
            )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    output_join_block = request.post("/citizen/v1/citizens/tenant/login", data={
        'telegramUserId': update.effective_user.id,
        'telegramUserName': update.effective_user.username,
        'blockId': context.args[0],
    })

    await update.message.reply_text(
        i18n(update.effective_user.language_code)("joined",
                                                  full_name=update.effective_user.full_name,
                                                  block_id=output_join_block['blockId'],
                                                  president_telegram_username=output_join_block[
                                                      'presidentTelegramUserName'])
    )

    await update.effective_message.reply_chat_action("upload_video")
    with open("media/intro.mp4", 'rb') as video:
        await update.message.reply_video(
            video=InputFile(video),
            width=1280,
            height=720,
            caption=i18n(update.effective_user.language_code)("intro_video_caption"),
        )

    await menu(update, context)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    citizen = request.get("/citizen/v1/citizens/info?telegramUserId={}".format(update.effective_user.id))

    keyboard = [[
        InlineKeyboardButton(
            i18n(update.effective_user.language_code)("create"),
            callback_data="create"
        ),
        InlineKeyboardButton(
            i18n(update.effective_user.language_code)("info_label"),
            callback_data="info"
        )
    ]]

    if citizen['type'] == 'president':
        keyboard.append([InlineKeyboardButton(
            i18n(update.effective_user.language_code)("settings"),
            callback_data="settings")]
        )
        # todo move it to settings of admin/president
        keyboard.append([InlineKeyboardButton(
            i18n(update.effective_user.language_code)("delete"),
            callback_data="delete"
        )])
    elif citizen['type'] == 'tenant':
        keyboard.append([InlineKeyboardButton(
            i18n(update.effective_user.language_code)("logout"),
            callback_data="logout"
        )])

    keyboard.append([InlineKeyboardButton(
        i18n(update.effective_user.language_code)("support_platform"),
        url=os.getenv("PATREON_URL")
    )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(i18n(update.effective_user.language_code)("commands_prompt"),
                                    reply_markup=reply_markup)


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    output_exit_block = request.delete(
        "/citizen/v1/citizens/tenant/logout?telegramUserId={}".format(update.effective_user.id))

    await update.message.reply_text(
        i18n(update.effective_user.language_code)
        ("exit_message", full_name=update.effective_user.full_name, block_id=output_exit_block['blockId']))


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    output_delete_block = request.delete(
        "/citizen/v1/citizens/president/delete?telegramUserId={}".format(update.effective_user.id))

    await update.message.reply_text(
        i18n(update.effective_user.language_code)
        ("delete_message", full_name=update.effective_user.full_name, block_id=output_delete_block['blockId'])
    )
