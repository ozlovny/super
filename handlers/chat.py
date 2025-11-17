import datetime
import sqlite3, config, asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.types import ChatPermissions, ChatMember
from filters.chat_type import ChatTypeFilter
from aiogram import Router, types, Bot
from aiogram.filters import Command

router = Router()
bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

conn = sqlite3.connect("db.db")
cursor = conn.cursor()


@router.message(ChatTypeFilter(chat_type=['group', 'supergroup']), Command(commands=["ban"]))
async def ban(message: types.Message):
    user_id = None
    full_name = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        full_name = message.reply_to_message.from_user.full_name

    mod = cursor.execute("SELECT mod FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()[0]

    if mod == 0 or message.from_user.id not in config.ADMINS:
        msg = await message.reply("<b>Не достаточно прав.</b>")

        await asyncio.sleep(4)

        await msg.delete()

        try:
            await message.delete()
        except:
            return

        return

    try:
        mod = cursor.execute("SELECT mod FROM users WHERE user_id=?", (user_id,)).fetchone()[0]

        if mod == 1:
            msg = await message.reply("<b>Вы не можете взаимодействовать с данным пользователем.</b>")

            await asyncio.sleep(4)

            await msg.delete()

            try:
                await message.delete()
            except:
                return

            return
    except Exception as e:
        msg = await message.reply(f"<b>📵 Неизвестная ошибка:</b> <code>{e}</code>")
        await asyncio.sleep(4)
        await msg.delete()
        try:
            await message.delete()
        except:
            pass
        return

    args = message.text.split(" ")

    if len(args) == 1 and message.reply_to_message:
        try:
            await bot.ban_chat_member(config.CHAT_ID, int(user_id))
        except Exception as e:
            msg = await message.reply(f"<b>📵 Неизвестная ошибка:</b> <code>{e}</code>")
            await asyncio.sleep(4)
            await msg.delete()
            try:
                await message.delete()
            except:
                pass
            return

        btns = [
            [types.InlineKeyboardButton(text='✅ Разблокировать', callback_data=f'unban:{user_id}')]
        ]

        markup = types.InlineKeyboardMarkup(inline_keyboard=btns)

        await message.reply(f"""<a href="tg://user?id={user_id}">{full_name}</a> [<code>{user_id}</code>] заблокирован(а).""", reply_markup=markup)
    else:
        msg = await message.reply("<b>Неправильное использование!</b>\n\n<i>Ответом на сообщение</i> <code>/ban</code>")

        await asyncio.sleep(4)

        await msg.delete()

        try:
            await message.delete()
        except:
            pass

@router.message(ChatTypeFilter(chat_type=['group', 'supergroup']), Command(commands=["mute"]))
async def mute(message: types.Message):
    user_id = None
    full_name = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        full_name = message.reply_to_message.from_user.full_name

    mod = cursor.execute("SELECT mod FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()[0]

    if mod == 0 or message.from_user.id not in config.ADMINS:
        msg = await message.reply("<b>Не достаточно прав.</b>")

        await asyncio.sleep(4)

        await msg.delete()

        try:
            await message.delete()
        except:
            return

        return

    try:
        mod = cursor.execute("SELECT mod FROM users WHERE user_id=?", (user_id,)).fetchone()[0]

        if mod == 1:
            msg = await message.reply("<b>Вы не можете взаимодействовать с данным пользователем.</b>")

            await asyncio.sleep(4)

            await msg.delete()

            try:
                await message.delete()
            except:
                return

            return
    except Exception as e:
        msg = await message.reply(f"<b>📵 Неизвестная ошибка:</b> <code>{e}</code>")
        await asyncio.sleep(4)
        await msg.delete()
        try:
            await message.delete()
        except:
            pass
        return

    args = message.text.split(" ")

    if len(args) == 2 and message.reply_to_message:
        time = args[1].lower()
        section = None
        until = None

        if 'd' in time or 'день' in time or 'дней' in time or 'дня' in time:
            section = "days"
            time = time.replace("d", "").replace("день", "").replace("дней", "").replace("дня", "").replace(" ", "")
        elif 's' in time or 'с' in time or 'секунд' in time or 'секунда' in time or 'секунды' in time or 'сек' in time:
            section = "seconds"
            time = time.replace("s", "").replace("с", "").replace("секунд", "").replace("секунда", "").replace("секунды", "").replace("сек", "").replace(" ", "")
        elif 'm' in time or 'м' in time or 'минут' in time or 'минута' in time or 'минуты' in time or 'мин' in time:
            section = "minutes"
            time = time.replace("m", "").replace("м", "").replace("минут", "").replace("минута", "").replace("минуты", "").replace("мин", "").replace(" ", "")
        elif 'h' in time or 'ч' in time or 'час' in time or 'часов' in time or 'часа' in time:
            section = "hours"
            time = time.replace("h", "").replace("ч", "").replace("час", "").replace("часов", "").replace("часа", "").replace(" ", "")
        else:
            msg = await message.reply("<b>Неправильно использование!</b>\n\n<i>Ответом на сообщение:</i> <code>/mute 1день</code>")

            await asyncio.sleep(4)

            await msg.delete()

            try:
                await message.delete()
            except:
                pass
            return

        if section == "days":
            until = datetime.timedelta(days=float(time))
        elif section == "seconds":
            until = datetime.timedelta(seconds=float(time))
        elif section == "minutes":
            until = datetime.timedelta(minutes=float(time))
        elif section == "hours":
            until = datetime.timedelta(hours=float(time))

        permissions = {
            'can_send_messages': False,
            'can_send_media_messages': False,
            'can_send_other_messages': False
        }

        new_permissions = ChatPermissions(**permissions)

        try:
            await bot.restrict_chat_member(config.CHAT_ID, int(user_id), new_permissions, until_date=until)
        except Exception as e:
            msg = await message.reply(f"<b>📵 Неизвестная ошибка:</b> <code>{e}</code>")
            await asyncio.sleep(4)
            await msg.delete()
            try:
                await message.delete()
            except:
                pass
            return

        expiration_time = datetime.datetime.now() + until
        until_text = expiration_time.strftime("%d/%m/%Y %H:%M")

        btns = [
            [types.InlineKeyboardButton(text='✅ Включить звук', callback_data=f'unmute:{user_id}')]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=btns)

        await message.reply(
            f"""<a href="tg://user?id={user_id}">{full_name}</a> [<code>{user_id}</code>] 🔇 обеззвучен(а).\n<b>До</b>: {until_text}""",
            reply_markup=markup)
    else:
        msg = await message.reply("<b>Неправильно использование!</b>\n\n<i>Ответом на сообщение:</i> <code>/mute 1день</code>")

        await asyncio.sleep(4)

        await msg.delete()

        try:
            await message.delete()
        except:
            pass

        return

@router.callback_query(lambda call: call.data.startswith('unban:'))
async def unban(call: types.CallbackQuery):
    user_id = call.data.split(":")[1]

    try:
        await bot.unban_chat_member(config.CHAT_ID, int(user_id))
    except Exception as e:
        msg = await call.message.reply(f"<b>📵 Неизвестная ошибка:</b> <code>{e}</code>")
        await asyncio.sleep(4)
        await msg.delete()
        return

    await bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=None)

@router.callback_query(lambda call: call.data.startswith('unmute:'))
async def unmute(call: types.CallbackQuery):
    user_id = call.data.split(":")[1]

    permissions = {
        'can_send_messages': True,
        'can_send_media_messages': True,
        'can_send_polls': False,
        'can_send_other_messages': True,
        'can_add_web_page_previews': False,
        'can_change_info': False,
        'can_invite_users': False,
        'can_pin_messages': False
    }

    new_permissions = ChatPermissions(**permissions)

    try:
        await bot.restrict_chat_member(config.CHAT_ID, int(user_id), new_permissions)
    except Exception as e:
        msg = await call.message.reply(f"<b>📵 Неизвестная ошибка:</b> <code>{e}</code>")
        await asyncio.sleep(4)
        await msg.delete()
        return

    await bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=None)

@router.chat_join_request()
async def on_chat_request(chat_request: types.ChatJoinRequest):
    exist = cursor.execute("SELECT * FROM users WHERE user_id=?", (chat_request.from_user.id,)).fetchone()
    if not exist:
        cursor.execute("INSERT INTO users(user_id) VALUES(?)", (chat_request.from_user.id,))
        conn.commit()

    await chat_request.approve()

    permissions = {
        'can_send_messages': False,
        'can_send_media_messages': False,
        'can_send_polls': False,
        'can_send_other_messages': False,
        'can_add_web_page_previews': False,
        'can_change_info': False,
        'can_invite_users': False,
        'can_pin_messages': False
    }

    new_permissions = ChatPermissions(**permissions)

    await bot.restrict_chat_member(chat_request.chat.id, chat_request.from_user.id, new_permissions)

    try:
        await chat_request.answer_pm("<b>Пожалуйста зайдите в чат и пройдите каптчу</b>")
    except:
        pass

    btns = [
        [types.InlineKeyboardButton(text="✅ Пройти каптчу",
                                    callback_data=f'start_captcha:{chat_request.from_user.id}')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=btns)

    msg = await bot.send_message(chat_request.chat.id,
                           f"""<b><a href="tg://user?id={chat_request.from_user.id}">{chat_request.from_user.first_name}</a>, вы должны пройти каптчу чтобы начать писать в чате</b>""", reply_markup=keyboard)

    cursor.execute("UPDATE users SET welcome_msg=? WHERE user_id=?", (msg.message_id,chat_request.from_user.id,))
    conn.commit()

@router.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer):
    user_id = poll_answer.user.id
    first_name = poll_answer.user.first_name
    correct_emoji = cursor.execute("SELECT correct_emoji FROM users WHERE user_id=?", (user_id,)).fetchone()[0]
    poll_id = poll_answer.poll_id
    poll_msg = cursor.execute("SELECT poll_msg FROM users WHERE user_id=?", (user_id,)).fetchone()[0]
    welcome_msg = cursor.execute("SELECT welcome_msg FROM users WHERE user_id=?", (user_id,)).fetchone()[0]

    if poll_id == poll_answer.poll_id:
        selected_option_id = poll_answer.option_ids[0]
        correct_option_id = correct_emoji

        if int(selected_option_id) == int(correct_option_id):
            await bot.send_message(user_id, "<b>💵 Проверка пройдена!</b>")
            await bot.delete_message(user_id, poll_msg)

            permissions = {
                'can_send_messages': True,
                'can_send_media_messages': True,
                'can_send_polls': False,
                'can_send_other_messages': True,
                'can_add_web_page_previews': False,
                'can_change_info': False,
                'can_invite_users': False,
                'can_pin_messages': False
            }

            new_permissions = ChatPermissions(**permissions)

            await bot.restrict_chat_member(config.CHAT_ID, user_id, new_permissions)

            btns = [
                [types.InlineKeyboardButton(text="Наш переходник", url="https://t.me/t3ther_cube")],
                [types.InlineKeyboardButton(text="Пользовательское соглашение", url=config.USER_AGREEMENT)]
            ]

            keyboard = types.InlineKeyboardMarkup(inline_keyboard=btns)
            await bot.delete_message(config.CHAT_ID, welcome_msg)
            await bot.send_message(config.CHAT_ID,
                                   f"""<b><a href="tg://user?id={user_id}">{first_name}</a>, добро пожаловать в наше логово!</b>""",
                                   reply_markup=keyboard)
        else:
            await bot.send_message(user_id, "<b>Упс! Вы выбрали неверный вариант. Попробуйте снова позже</b>")
            await bot.delete_message(user_id, poll_msg)