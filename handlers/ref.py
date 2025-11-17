import requests
import sqlite3
import config
import random
import kb
import os
import re

from aiogram.types import FSInputFile, ChatPermissions
from aiogram import Bot, Dispatcher, F, types
from handlers.casino import transfer, get_cb_balance
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from datetime import timedelta
from aiogram import Router

router = Router()

conn = sqlite3.connect("db.db")
cursor = conn.cursor()


emoji_options = ["😃", "😉", "😍", "😜", "😎", "🤓", "😢", "😡", "🤯", "😇", '☪', '✝', '🔈', '🈯️', '🕑', '🐣', '💌', '🕦', '👲', '🌵',
                 '🐍', '🚄', '♊️', '📡', '🍱', '🐈', '🏎', '🗳', '😑', '💲', '🈁', '🏍', '🏂', '🍒', '🎦', '🎱', '💐', '🛁', '🕓', '👈',
                 '🎙', '☎️', '📽', '😀', '🕵', '0️⃣', '😙', '🌯', '🕙', '🐻', '🔑', '0️⃣', '🌂', '🖼', '☦', '🐸', '🙋', '🐆', '❌',
                 '🦁', '✨', '🍗', '🗃', '🌬', '❣', '🦄', '📡', '📁', '☹', '😄', '🎶', '🅾️', '📏', '♐️', '🛠', '😣', '👀', '👔', '🍳',
                 '🎯', '🛅', '🚅', '🐫', '😄', '🏅', '⛓', '👘', '😤', '🐹', '⚓️', '⬜️', '😣', '👋', '🏢', '🗜', '🔸', '💋', '🎵', '🐷',
                 '⏯', '🔭', '🛠', '🔯', '🏚', '🍷', '🔌', '🚓', '💟', '😃', '😺']

def generate_captcha():
    correct_emoji = random.choice(emoji_options)
    all_options = random.sample(emoji_options, 6)

    if correct_emoji not in all_options:
        all_options[0] = correct_emoji

    random.shuffle(all_options)
    return correct_emoji, all_options

bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

class States(StatesGroup):
    popol = State()
    withd = State()
    msg = State()
    search = State()
    captcha = State()
    c1 = State()
    c2 = State()

@router.callback_query(StateFilter('*'))
async def calls(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()

    exist = cursor.execute("SELECT * FROM users WHERE user_id=?", (call.from_user.id,)).fetchone()
    if not exist:
        cursor.execute("INSERT INTO users(user_id,first_name) VALUES(?,?)", (call.from_user.id,call.from_user.first_name,))
        conn.commit()
    else:
        cursor.execute("UPDATE users SET first_name=?, username=? WHERE user_id=?", (call.from_user.first_name,call.from_user.username,call.from_user.id,))
        conn.commit()

    user = cursor.execute("SELECT * FROM users WHERE user_id=?", (call.from_user.id,)).fetchone()

    if call.data == 'withdraw':
        if float(user[3]) < float(1):
            await call.message.answer("<b>❌ Минимальная сумма для вывода: <code>1$</code></b>")
        else:
            await bot.send_message(config.VUVOD_ID,
                                   f"""<b>💵 Новая заявка на вывод!\n\n<blockquote>Никнейм игрока: {call.from_user.full_name}</blockquote>\n\n<blockquote>Сумма вывода: {user[3]:.2f}</blockquote>\n\n<blockquote><a href="tg://user?id={call.from_user.id}">Перейти к пользователю</a></blockquote></b>""", reply_markup=kb.vuvod())

            cursor.execute("UPDATE users SET balance=0 WHERE id=?", (user[0],))
            conn.commit()

            await call.message.answer(f"<b>💵 Заявка на вывод <code>{user[3]:.2f}$</code> успешно подана!</b>")
    elif call.data == 'my_refs':
        refs = cursor.execute("SELECT * FROM users WHERE ref=?", (user[0],)).fetchall()

        if not refs:
            await call.message.answer("У вас пока нет рефералов")
        else:
            text = ""
            for ref in refs:
                text += f"Реферал: {ref[2]}\nID: {ref[1]}"

            with open("referals.txt", "a") as f:
                f.write(text)
                f.close()

            await call.message.answer_document(FSInputFile("referals.txt"))

            os.remove("referals.txt")
    elif call.data == 'faq':
        p1 = f"""<b>[👋] Приветствуем тебя в {config.TEAM_NAME}!

Для ознакомления с нашим проектом, советуем пройти небольшое обучение, листай дальше. ➡️</b>"""

        await call.message.answer_photo(photo=FSInputFile('info.jpg'), caption=p1, reply_markup=kb.faq(1))
    elif call.data.startswith("faq:"):
        page = int(call.data.split(":")[1])
        p1 = f"""<b>[👋] Приветствуем тебя в {config.TEAM_NAME}!

Для ознакомления с нашим проектом, советуем пройти небольшое обучение, листай дальше. ➡️</b>"""
        p2 = """<b>[💼] Работа в проекте.</b><i>

Наш проект предоставляет партнёрскую программу для наших игроков.

<b>Твоя задача приглашать новых игроков по реферальной ссылке под любым предлогом, за депозиты ты будешь получать <u>до</u> <code>30%</code> от каждого проигрыша приглашённого игрока.</b>

<blockquote>Мы регулярно работаем над обновлениями и улучшаем экосистему. ➡️</blockquote></i>"""
        p3 = """<b>[💰] Выплаты и профиты.

Любая выплата на любую сумму выплачивается автоматически от бота, в котором ты читаешь это обучение.

— Выплаты более 15.000 могут выплачиваться с задержкой.

<blockquote>Профит, это успешное пополнение [депозит] от клиента в бота. ➡️</blockquote></b>"""
        p4 = """<b>[📊] Уровни.

При достижении определенного уровня, тебе откроются эксклюзивные возможности.
Минимальное реферальное вознаграждение 10% от суммы депозитов, по мере поступления депозитов вы сможете прокачать свой процент вплоть до 30%!

<blockquote>1 уровень</blockquote>
—  ( <code>10% от 0$ оборота</code> )

<blockquote>2 уровень</blockquote>
—  ( <code>15%, от 20$ оборота</code> )

<blockquote>3 уровень</blockquote>
—  ( <code>20%, от 30$ оборота</code> )

<blockquote>4 уровень</blockquote>
—  ( <code>25%, от 40$ оборота</code> )

<blockquote>5 уровень</blockquote>
—  ( <code>30%, от 50$ оборота</code> )

<blockquote>Чтобы повысить уровень, необходимо совершать профиты ➡️</blockquote></b>"""
        p5 = """<b>[👔] Карьера и возможности.

Успешные работники могут претендовать на повышение. Становиться частью администрации и получать стабильный доход

<blockquote>Повышение по карьерной по лестнице может получить каждый, если будет упорно трудиться и развиваться в команде! ➡️</blockquote></b>"""
        p6 = f"""<i><b>[💎] Обучение завершено!</b>

Не забудь вступить в каналы проекта, чтобы быть всегда в центре событий.

<b>Желаем удачи в начинаниях!</b>

<blockquote><b>С уважением, персонал {config.TEAM_NAME}!</b></blockquote></i>"""

        text = None

        if page == 1:
            text = p1
        elif page == 2:
            text = p2
        elif page == 3:
            text = p3
        elif page == 4:
            text = p4
        elif page == 5:
            text = p5
        elif page == 6:
            text = p6

        await call.message.edit_caption(caption=text, reply_markup=kb.faq(page))
    elif call.data == 'close':
        await call.message.delete()
    elif call.data == 'control_kazna':
        await call.message.edit_reply_markup(reply_markup=kb.control_kazna())
    elif call.data == 'popol':
        await call.message.edit_text("<b><blockquote>💵 Введите сумму</blockquote></b>", reply_markup=kb.back('admin'))
        await state.set_state(States.popol)
    elif call.data == 'withd':
        await call.message.edit_text("<b><blockquote>💵 Введите сумму</blockquote></b>", reply_markup=kb.back('admin'))
        await state.set_state(States.withd)
    elif call.data.startswith("page_"):
        page = int(call.data.split("_")[1])
        keyboard = await kb.get_users_keyboard(page)
        await call.message.edit_reply_markup(reply_markup=keyboard)
    elif call.data.startswith("user:"):
        user_id = call.data.split(":")[1]
        user_info = cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

        if user_info[6]:
            referrer = cursor.execute("SELECT first_name FROM users WHERE id=?", (user_info[6],)).fetchone()
            referrer = referrer[0] if referrer else "Никем"
        else:
            referrer = "Никем"

        total_bets = cursor.execute("SELECT COUNT(*) FROM bets WHERE user_id=?", (user_info[1],)).fetchone()[0]
        total_bets_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE user_id=?", (user_info[1],)).fetchone()[0]
        total_bets_summ = total_bets_summ if total_bets_summ else float(0)
        total_wins = cursor.execute("SELECT COUNT(*) FROM bets WHERE win=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_wins_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE win=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_wins_summ = total_wins_summ if total_wins_summ else float(0)
        total_lose = cursor.execute("SELECT COUNT(*) FROM bets WHERE lose=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_lose_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE lose=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_lose_summ = total_lose_summ if total_lose_summ else float(0)
        total_draw = cursor.execute("SELECT COUNT(*) FROM bets WHERE draw=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_draw_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE draw=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_draw_summ = total_draw_summ if total_draw_summ else float(0)

        status = 'Модератор' if user_info[7] == 1 else 'Пользователь'
        status = 'Администратор' if user_info[1] in config.ADMINS else status
        status = 'Заблокирован' if user_info[8] == 1 else status

        await call.message.edit_text(f"<b><blockquote>💵 Управление пользователем {user_info[2]}</blockquote>\n\n<blockquote>Статус - {status}</blockquote>\n\n<blockquote>Баланс - <code>{user_info[3]:.2f}</code> $</blockquote>\n\n<blockquote>{user_info[5]} уровень</blockquote>\n\n<blockquote>Всего ставок - <code>{total_bets}</code> шт. [~ <code>{total_bets_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Выигрышей - <code>{total_wins}</code> шт. [~ <code>{total_wins_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Проигрышей - <code>{total_lose}</code> шт. [~ <code>{total_lose_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Ничьи - <code>{total_draw}</code> шт. [~ <code>{total_draw_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Приглашен - {referrer}</blockquote></b>", reply_markup=kb.control_user(user_info[0], user_info[7], user_info[8]))
    elif call.data.startswith("set_mod:"):
        user_id = call.data.split(":")[1]
        status = call.data.split(":")[2]

        cursor.execute("UPDATE users SET mod=? WHERE id=?", (status,user_id,))
        conn.commit()

        user_info = cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

        if user_info[6]:
            referrer = cursor.execute("SELECT first_name FROM users WHERE id=?", (user_info[6],)).fetchone()
            referrer = referrer[0] if referrer else "Никем"
        else:
            referrer = "Никем"

        total_bets = cursor.execute("SELECT COUNT(*) FROM bets WHERE user_id=?", (user_info[1],)).fetchone()[0]
        total_bets_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE user_id=?", (user_info[1],)).fetchone()[0]
        total_bets_summ = total_bets_summ if total_bets_summ else float(0)
        total_wins = cursor.execute("SELECT COUNT(*) FROM bets WHERE win=1 AND user_id=?", (user_info[1],)).fetchone()[
            0]
        total_wins_summ = \
        cursor.execute("SELECT SUM(amount) FROM bets WHERE win=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_wins_summ = total_wins_summ if total_wins_summ else float(0)
        total_lose = cursor.execute("SELECT COUNT(*) FROM bets WHERE lose=1 AND user_id=?", (user_info[1],)).fetchone()[
            0]
        total_lose_summ = \
        cursor.execute("SELECT SUM(amount) FROM bets WHERE lose=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_lose_summ = total_lose_summ if total_lose_summ else float(0)
        total_draw = cursor.execute("SELECT COUNT(*) FROM bets WHERE draw=1 AND user_id=?", (user_info[1],)).fetchone()[
            0]
        total_draw_summ = \
        cursor.execute("SELECT SUM(amount) FROM bets WHERE draw=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_draw_summ = total_draw_summ if total_draw_summ else float(0)

        status = 'Модератор' if user_info[7] == 1 else 'Пользователь'
        status = 'Администратор' if user_info[1] in config.ADMINS else status
        status = 'Заблокирован' if user_info[8] == 1 else status

        await call.message.edit_text(
            f"<b><blockquote>💵 Управление пользователем {user_info[2]}</blockquote>\n\n<blockquote>Статус - {status}</blockquote>\n\n<blockquote>Баланс - <code>{user_info[3]:.2f}</code> $</blockquote>\n\n<blockquote>{user_info[5]} уровень</blockquote>\n\n<blockquote>Всего ставок - <code>{total_bets}</code> шт. [~ <code>{total_bets_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Выигрышей - <code>{total_wins}</code> шт. [~ <code>{total_wins_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Проигрышей - <code>{total_lose}</code> шт. [~ <code>{total_lose_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Ничьи - <code>{total_draw}</code> шт. [~ <code>{total_draw_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Приглашен - {referrer}</blockquote></b>",
            reply_markup=kb.control_user(user_info[0], user_info[7], user_info[8]))
    elif call.data.startswith("set_ban:"):
        user_id = call.data.split(":")[1]
        status = call.data.split(":")[2]

        cursor.execute("UPDATE users SET ban=? WHERE id=?", (status,user_id,))
        conn.commit()

        user_info = cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

        if user_info[6]:
            referrer = cursor.execute("SELECT first_name FROM users WHERE id=?", (user_info[6],)).fetchone()
            referrer = referrer[0] if referrer else "Никем"
        else:
            referrer = "Никем"

        total_bets = cursor.execute("SELECT COUNT(*) FROM bets WHERE user_id=?", (user_info[1],)).fetchone()[0]
        total_bets_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE user_id=?", (user_info[1],)).fetchone()[0]
        total_bets_summ = total_bets_summ if total_bets_summ else float(0)
        total_wins = cursor.execute("SELECT COUNT(*) FROM bets WHERE win=1 AND user_id=?", (user_info[1],)).fetchone()[
            0]
        total_wins_summ = \
        cursor.execute("SELECT SUM(amount) FROM bets WHERE win=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_wins_summ = total_wins_summ if total_wins_summ else float(0)
        total_lose = cursor.execute("SELECT COUNT(*) FROM bets WHERE lose=1 AND user_id=?", (user_info[1],)).fetchone()[
            0]
        total_lose_summ = \
        cursor.execute("SELECT SUM(amount) FROM bets WHERE lose=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_lose_summ = total_lose_summ if total_lose_summ else float(0)
        total_draw = cursor.execute("SELECT COUNT(*) FROM bets WHERE draw=1 AND user_id=?", (user_info[1],)).fetchone()[
            0]
        total_draw_summ = \
        cursor.execute("SELECT SUM(amount) FROM bets WHERE draw=1 AND user_id=?", (user_info[1],)).fetchone()[0]
        total_draw_summ = total_draw_summ if total_draw_summ else float(0)

        status = 'Модератор' if user_info[7] == 1 else 'Пользователь'
        status = 'Администратор' if user_info[1] in config.ADMINS else status
        status = 'Заблокирован' if user_info[8] == 1 else status

        await call.message.edit_text(
            f"<b><blockquote>💵 Управление пользователем {user_info[2]}</blockquote>\n\n<blockquote>Статус - {status}</blockquote>\n\n<blockquote>Баланс - <code>{user_info[3]:.2f}</code> $</blockquote>\n\n<blockquote>{user_info[5]} уровень</blockquote>\n\n<blockquote>Всего ставок - <code>{total_bets}</code> шт. [~ <code>{total_bets_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Выигрышей - <code>{total_wins}</code> шт. [~ <code>{total_wins_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Проигрышей - <code>{total_lose}</code> шт. [~ <code>{total_lose_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Ничьи - <code>{total_draw}</code> шт. [~ <code>{total_draw_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Приглашен - {referrer}</blockquote></b>",
            reply_markup=kb.control_user(user_info[0], user_info[7], user_info[8]))

    elif call.data.startswith("msg:"):
        user_id = call.data.split(":")[1]

        await call.message.edit_text("<b><blockquote>💵 Введите сообщение</blockquote></b>", reply_markup=kb.back(f'user:{user_id}'))
        await state.set_state(States.msg)
        await state.update_data(user_id=user_id)
    elif call.data == 'search_user':
        await call.message.edit_text("<b><blockquote>💵 Отправьте ID или @username пользователя</blockquote></b>", reply_markup=kb.back('admin'))
        await state.set_state(States.search)
    elif call.data == 'admin':
        total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_bets = cursor.execute("SELECT COUNT(*) FROM bets").fetchone()[0]
        total_bets_summ = cursor.execute("SELECT SUM(amount) FROM bets").fetchone()[0]
        total_bets_summ = total_bets_summ if total_bets_summ else float(0)
        total_wins = cursor.execute("SELECT COUNT(*) FROM bets WHERE win=1").fetchone()[0]
        total_wins_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE win=1").fetchone()[0]
        total_wins_summ = total_wins_summ if total_wins_summ else float(0)
        total_lose = cursor.execute("SELECT COUNT(*) FROM bets WHERE lose=1").fetchone()[0]
        total_lose_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE lose=1").fetchone()[0]
        total_lose_summ = total_lose_summ if total_lose_summ else float(0)
        total_draw = cursor.execute("SELECT COUNT(*) FROM bets WHERE draw=1").fetchone()[0]
        total_draw_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE draw=1").fetchone()[0]
        total_draw_summ = total_draw_summ if total_draw_summ else float(0)

        await call.message.edit_text(
            f"<b><blockquote>Количество пользователей - {total_users} шт.</blockquote>\n\n<blockquote>Всего ставок - <code>{total_bets}</code> шт. [~ <code>{total_bets_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Количество выигрышей - <code>{total_wins}</code> шт. [~ <code>{total_wins_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Количество проигрышей - <code>{total_lose}</code> шт. [~ <code>{total_lose_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Количество ничьи - <code>{total_draw}</code> шт. [~ <code>{total_draw_summ}</code> $]</blockquote></b>",
            reply_markup=kb.admin())
    elif call.data.startswith("start_captcha:"):
        user_id = call.data.split(":")[1]

        if int(call.from_user.id) != int(user_id):
            await call.answer("Это не для вас", show_alert=True)
            return

        await bot.send_message(call.from_user.id, "<b>🛡 Проверка на пользователя</b>")

        correct_emoji, options = generate_captcha()
        cursor.execute("UPDATE users SET correct_emoji=? WHERE user_id=?",
                       (options.index(correct_emoji), call.from_user.id,))
        conn.commit()

        msg = await bot.send_poll(
            chat_id=call.from_user.id,
            question=f"Выберите {correct_emoji}",
            options=options,
            type='quiz',
            correct_option_id=options.index(correct_emoji),
            open_period=60,
            is_anonymous=False
        )

        cursor.execute("UPDATE users SET poll_msg=? WHERE user_id=?", (msg.message_id, call.from_user.id,))
        conn.commit()
    elif call.data.startswith("delete:"):
        panel_id = call.data.split(":")[1]

        if int(call.from_user.id) != int(panel_id):
            await call.answer("Не нужно так!", show_alert=True)
            return

        await call.message.delete()
    elif call.data.startswith("ban:"):
        user_id = call.data.split(":")[1]
        panel_id = call.data.split(":")[2]

        if int(call.from_user.id) != int(panel_id):
            await call.answer("Не нужно так!", show_alert=True)
            return

        user_info = cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        cursor.execute("UPDATE users SET ban=1 WHERE user_id=?", (user_id,))
        conn.commit()
        await bot.ban_chat_member(config.CHAT_ID, int(user_id))

        await call.message.delete()
        await call.message.answer(f"""<b>💵 Пользователь <a href="tg://user?id={user_id}">{user_info[2]}</a> был забанен модератором <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a></b>""")
    elif call.data.startswith("mute:"):
        user_id = call.data.split(":")[1]
        panel_id = call.data.split(":")[2]

        if int(call.from_user.id) != int(panel_id):
            await call.answer("Не нужно так!", show_alert=True)
            return

        await call.message.edit_text("<b>💵 Выберите на какой срок выдать мут</b>", reply_markup=kb.mutes(user_id, panel_id))
    elif call.data.startswith("mutee:"):
        user_id = call.data.split(":")[1]
        duration = call.data.split(":")[2]
        panel_id = call.data.split(":")[3]

        if int(call.from_user.id) != int(panel_id):
            await call.answer("Не нужно так!", show_alert=True)
            return

        user_info = cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()

        until_date = timedelta(minutes=float(duration))

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

        await bot.restrict_chat_member(config.CHAT_ID, int(user_id), new_permissions, until_date=until_date)

        await call.message.delete()
        await call.message.answer(
            f"""<b>💵 Пользователь <a href="tg://user?id={user_id}">{user_info[2]}</a> был замучен модератором <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a> на {duration} мин.</b>""")
    elif call.data == 'podkrut':
        await call.message.edit_text(f"<b><blockquote>💵 Управление подкрутом</blockquote></b>", reply_markup=kb.podkrut())
    elif call.data.startswith('set_podkrut:'):
        status = call.data.split(":")[1]

        cursor.execute("UPDATE podkrut SET podkrut_status=?", (status,))
        conn.commit()

        await call.message.edit_reply_markup(reply_markup=kb.podkrut())
    elif call.data.startswith('set_prokrut:'):
        prokrut = call.data.split(":")[1]

        cursor.execute("UPDATE podkrut SET prokrut=?", (prokrut,))
        conn.commit()

        await call.message.edit_reply_markup(reply_markup=kb.podkrut())
    elif call.data.startswith('vuvod:'):
        current = call.data.split(":")[1]
        if int(current) == 0:
            btns = [
                [types.InlineKeyboardButton(text='🔋 Выплачено', callback_data='vuvod:1')]
            ]

            keyb = types.InlineKeyboardMarkup(inline_keyboard=btns)

            await call.message.edit_reply_markup(reply_markup=keyb)
        elif int(current) == 1:
            btns = [
                [types.InlineKeyboardButton(text='🏮 В ожидании', callback_data='vuvod:0')]
            ]

            keyb = types.InlineKeyboardMarkup(inline_keyboard=btns)

            await call.message.edit_reply_markup(reply_markup=keyb)
    elif call.data == 'balance':
        await call.message.edit_text(f"<b>💵 Управление казной 💵</b>\n\n<i>Баланс - {get_cb_balance()} USDT</i>", reply_markup=kb.back('admin'))
    elif call.data == 'contests':
        await call.message.edit_text("<b>💵 Система конкурсов 💵</b>\n\n<i>В данном меню вы можете управлять системой конкурсов и самими конкурсами</i>", reply_markup=kb.contests())
    elif call.data == 'create_contest':
        await call.message.edit_text("<b>💵 Система конкурсов 💵</b>\n\n<i>Введите сумму выигрыша</i>", reply_markup=kb.back('contests'))
        await state.set_state(States.c1)
    elif call.data == 'stop_all':
        contests = cursor.execute("SELECT * FROM contests WHERE end=0").fetchall()

        for contest in contests:
            try:
                cursor.execute("UPDATE contests SET end=1 WHERE id=?", (contest[0],))
                conn.commit()
                await bot.send_message(config.BETS_ID, f"<b>💵 Конкурс №{contest[0]} завершён!</b>\n<blockquote><b>Победитель должен забрать приз ({contest[8]}$) у администратора.</b></blockquote>", reply_to_message_id=contest[9])
                cursor.execute("DELETE FROM contests WHERE id=?", (contest[0],))
                conn.commit()
            except:
                pass

        await call.message.edit_text("Все конкурсы были завершены", reply_markup=kb.back('contests'))

@router.message(States.c1, F.text)
async def c1_handler(message: types.Message, state: FSMContext):
    try:
        float(message.text)
        await state.update_data(amount=message.text)
        await message.answer("<b>💵 Система конкурсов 💵</b>\n\n<i>Отправьте дату окончания (Пример: <code>13.06.2024 13:10</code>)</i>", reply_markup=kb.back('contests'))
        await state.set_state(States.c2)
    except:
        await message.answer("<b>💵 Система конкурсов 💵</b>\n\n<i>Отправьте сумму числом!</i>", reply_markup=kb.back('contests'))

@router.message(States.c2, F.text)
async def c2_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get('amount')
    date = message.text

    pattern = re.compile(r"^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$")

    if pattern.match(date):
        msg = await bot.send_message(config.BETS_ID, f"""<b>💸 Конкурс</b>

<i>Игрок который сделает самую крупную ставку до {date}
— Получит {amount}$</i>

<blockquote><b>🥇 Пустое место [0.0$]</b>

<b>🥈 Пустое место [0.0$]</b>

<b>🥉 Пустое место [0.0$]</b></blockquote>""", reply_markup=kb.bet_kb())
        await message.answer("<b>💵 Система конкурсов 💵</b>\n\n<i>Конкурс создан!</i>", reply_markup=kb.back('contests'))
        cursor.execute("INSERT INTO contests(top1,top2,top3,top1_summa,top2_summa,top3_summa,end_date,win_amount,msg_id) VALUES('Пустое место','Пустое место','Пустое место',0.0,0.0,0.0,?,?,?)", (date,amount,msg.message_id,))
        conn.commit()
    else:
        await message.answer("<b>💵 Система конкурсов 💵</b>\n\n<i>Отправляйте дату как указано в примере!! (Пример: <code>13.06.2024 13:10</code>)</i>", reply_markup=kb.back('contests'))

def create_invoice(amount):
    headers = {"Crypto-Pay-API-Token": config.CRYPTOPAY_TOKEN}
    data = {"asset": "USDT", "amount": float(amount)}
    r = requests.get("https://pay.crypt.bot/api/createInvoice", data=data, headers=headers).json()
    return r['result']['bot_invoice_url']

@router.message(States.search, F.text)
async def search_state(message: types.Message, state: FSMContext):
    await state.clear()

    user = None

    if message.text.isdigit():
        user = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.text,)).fetchone()
    else:
        username = message.text.replace("@", "")
        user = cursor.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

    await message.answer("<b><blockquote>💵 Найденные результаты:</blockquote></b>", reply_markup=kb.found(user))

@router.message(States.msg, F.text)
async def msg_state(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    user_idd = cursor.execute("SELECT user_id FROM users WHERE id=?", (user_id,)).fetchone()[0]

    await state.clear()

    try:
        await bot.send_message(user_idd, f"<b><blockquote>💌 Вам поступило сообщение от администратора: <code>{message.text}</code></blockquote></b>", parse_mode='HTML')
        await message.answer("<b><blockquote>💵 Сообщение успешно отправлено</blockquote></b>", reply_markup=kb.back(f'user:{user_id}'))
    except:
        await message.answer("<b><blockquote>💵 Сообщение не было отправлено, возможно пользователь заблокировал бота</blockquote></b>", reply_markup=kb.back(f'user:{user_id}'))

@router.message(States.popol, F.text)
async def popol_state(message: types.Message, state: FSMContext):
    try:
        summa = float(message.text)
        invoice = create_invoice(summa)

        await state.clear()
        await message.answer(f"<b><blockquote>💵 Пополнение казны на сумму <code>{summa}</code> $</blockquote></b>", reply_markup=kb.pay(invoice))
    except:
        await message.answer("<b><blockquote>💵 Вы ввели сумму не числом! Попробуйте еще раз</blockquote></b>", reply_markup=kb.back('admin'))
        return

@router.message(States.withd, F.text)
async def withd_state(message: types.Message, state: FSMContext):
    try:
        summa = float(message.text)
        if summa < 1.05:
            await message.answer("<b><blockquote>💵 Сумма вывода меньше <code>1.05</code> $ вывод не был произведен!</blockquote></b>", reply_markup=kb.back('admin'))
            return

        transferr = await transfer(summa, message.from_user.id)

        await state.clear()

        if transferr:
            await message.answer(f"<b><blockquote>💵 Вывод казны на сумму <code>{summa}</code> $ был произведен!</blockquote></b>", reply_markup=kb.back('admin'))
        else:
            await message.answer("<b><blockquote>💵 В казне нету такой суммы! Вывод не был произведен.</blockquote></b>", reply_markup=kb.back('admin'))
    except:
        await message.answer("<b><blockquote>💵 Вы ввели сумму не числом! Попробуйте еще раз</blockquote></b>", reply_markup=kb.back('admin'))
        return