import asyncio
import re

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton
from pykeyboard import InlineKeyboard

from nana import AdminSettings
from nana import app
from nana import BotUsername
from nana import COMMAND_PREFIXES
from nana import DB_AVAILABLE
from nana import Owner
from nana import OwnerName
from nana import PM_PERMIT
from nana import setbot
from nana.utils.parser import mention_markdown

if DB_AVAILABLE:
    from nana.plugins.database.pm_db import (
        set_whitelist,
        get_whitelist,
        set_req,
        get_req,
        del_whitelist,
    )

welc_txt = f"""
UwU , I'm {OwnerName}'s Loli-chan .
If You want Something, try contacting me with the buttons given below. 
Just dont say 'hello' / 'hi', get staright to the point ,ffs """


NOTIFY_ID = Owner
BLACKLIST = ['hack', 'fuck', 'bitch', 'pubg', 'sex', 'bitcoin','hello' ,'hi',]


@app.on_message(~filters.me & filters.private & ~filters.bot)
async def pm_block(client, message):
    if not PM_PERMIT:
        return
    if message.chat.id in AdminSettings:
        set_whitelist(message.chat.id, True)
    if not get_whitelist(message.chat.id):
        await client.read_history(message.chat.id)
        if message.text:
            for x in message.text.lower().split():
                if x in BLACKLIST:
                    await client.send_sticker(
                        message.chat.id,
                        sticker='CAACAgUAAxkBAAEC3JBgGCUorQxL41RGQwqD2p_YxDlneQACagADNFwoOsGQufTU4CkqHgQ',
                    )
                    await message.reply(
                        'OwO , i am done here , ffs get tf out of here !',
                    )
                    await client.block_user(message.chat.id)
                    return
        if not get_req(message.chat.id):
            x = await client.get_inline_bot_results(BotUsername, 'engine_pm')
        else:
            x = await client.get_inline_bot_results(BotUsername, 'engine_pm')
        await client.send_inline_bot_result(
            message.chat.id,
            query_id=x.query_id,
            result_id=x.results[0].id,
            hide_via=True,
        )


@app.on_message(
    filters.me & filters.command(
        'approve', COMMAND_PREFIXES,
    ) & filters.private,
)
async def approve_pm(_, message):
    if message.chat.type == 'private':
        set_whitelist(message.chat.id, True)
    else:
        if message.reply_to_message:
            set_whitelist(message.reply_to_message.from_user.id, True)
        else:
            message.delete()
            return
    await message.edit('**Approved to PM!**')
    await asyncio.sleep(3)
    await message.delete()


@app.on_message(
    filters.me
    & filters.command(['revoke', 'disapprove'], COMMAND_PREFIXES)
    & filters.private,
)
async def revoke_pm_block(_, message):
    if message.chat.type == 'private':
        del_whitelist(message.chat.id)
    else:
        if message.reply_to_message:
            del_whitelist(message.reply_to_message.from_user.id)
        else:
            message.delete()
            return
    await message.edit('**PM permission revoked!**')
    await asyncio.sleep(3)
    await message.delete()


def pm_button_callback(_, __, query):
    if re.match('engine_pm', query.data):
        return True


pm_filter = filters.create(pm_button_callback)


@setbot.on_callback_query(pm_filter)
async def pm_button(client, query):
    print(query)
    if not PM_PERMIT:
        return
    if (
        query.from_user.id in AdminSettings
        and not re.match('engine_pm_apr', query.data)
        and not re.match('engine_pm_blk', query.data)
    ):
        await client.answer_callback_query(
            query.id, "Tf you should not be the one doin this shit.", show_alert=False,
        )
        return
    if re.match('engine_pm_block', query.data):
        await app.send_sticker(
            query.from_user.id, sticker='CAACAgUAAxkBAAEC3JBgGCUorQxL41RGQwqD2p_YxDlneQACagADNFwoOsGQufTU4CkqHgQ',
        )
        await setbot.edit_inline_text(
            query.from_user.id,
            'I am broke.\nsayonara !',
        )
        await app.block_user(query.from_user.id)
    elif re.match('engine_pm_nope', query.data):
        await setbot.edit_inline_text(query.inline_message_id, '👍')
        await app.send_message(
            query.from_user.id,
            'Hello, please wait for a reply from my master, thank you.',
        )
        buttons = InlineKeyboard(row_width=2)
        buttons.add(
            InlineKeyboardButton(
                'Approve',
                callback_data=f'engine_pm_apr-{query.from_user.id}',
            ),

            InlineKeyboardButton(
                'Block',
                callback_data=f'engine_pm_blk-{query.from_user.id}',
            ),
        )
        pm_bot_mention = mention_markdown(
            query.from_user.id, query.from_user.first_name,
        )
        pm_bot_message = f'~{pm_bot_mention} want to contact you~'
        await setbot.send_message(
            NOTIFY_ID,
            pm_bot_message,
            reply_markup=buttons,
        )
        set_req(query.from_user.id, True)
    elif re.match('engine_pm_report', query.data):
        await setbot.edit_inline_text(query.inline_message_id, '👍')
        await app.send_message(
            query.from_user.id,
            'ffs gtfo.',
        )
    elif re.match('engine_pm_none', query.data):
        await setbot.edit_inline_text(query.inline_message_id, '👍')
        await app.send_message(
            query.from_user.id,
            'Aight then. ',
        )
    elif re.match('engine_pm_apr', query.data):
        target = query.data.split('-')[1]
        await query.message.edit_text(f'[Approved to PM]({target})')
        await app.send_message(
            target, 'Hmph ! does not seem to be a bad guy  still doe get to the point ,Why are you here ? .',
        )
        set_whitelist(int(target), True)
    elif re.match(r'engine_pm_blk', query.data):
        target = query.data.split('-')[1]
        await query.message.edit_text('That user was blocked ~')
        await app.send_message(
            target,
            'OwO Stop pestering and btw Sayoooonara.',
        )
        await app.block_user(target)
    else:
        await setbot.edit_inline_text(query.inline_message_id, '🙆‍')
