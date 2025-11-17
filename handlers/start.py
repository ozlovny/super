from aiogram.filters import CommandObject, CommandStart, StateFilter
from aiogram.client.default import DefaultBotProperties
from filters.chat_type import ChatTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types, Bot
from aiogram.types import FSInputFile
import profile_generator
import datetime
import sqlite3
import config
import asyncio
import kb

router = Router()
bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

conn = sqlite3.connect("db.db")
cursor = conn.cursor()


def days_text(days):
    if days % 10 == 1 and days % 100 != 11:
        return f"{days} день"
    elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
        return f"{days} дня"
    else:
        return f"{days} дней"

@router.message(F.text, CommandStart(deep_link=True))
async def start_deep(message: types.Message, state: FSMContext, command: CommandObject):
    await state.clear()

    args = command.args

    if args:
        try:
            int(args)
            if int(args) != int(message.from_user.id):
                referrer = cursor.execute("SELECT * FROM users WHERE id=?", (args,)).fetchone()
                if referrer:
                    exist = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()
                    if not exist:
                        cursor.execute("INSERT INTO users(user_id,first_name,username,ref) VALUES(?,?,?,?)", (
                        message.from_user.id, message.from_user.first_name, message.from_user.username, args))
                        conn.commit()

                        await message.answer(
                            f"Вы успешно зарегистрировались в системе по реферальной ссылке {referrer[2]} !")
                        await bot.send_message(referrer[1],
                                               f"👤 По вашей ссылке зарегистрировался <code>{message.from_user.first_name}  ({message.from_user.id})</code>")
        except:
            pass

    exist = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()
    if not exist:
        cursor.execute("INSERT INTO users(user_id,first_name) VALUES(?,?)",
                       (message.from_user.id, message.from_user.first_name,))
        conn.commit()
    else:
        cursor.execute("UPDATE users SET first_name=?, username=? WHERE user_id=?",
                       (message.from_user.first_name, message.from_user.username, message.from_user.id,))
        conn.commit()

    user = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()

    refs = cursor.execute("SELECT COUNT(*) FROM users WHERE ref=?", (user[0],)).fetchone()[0]

    reward = None
    till_next = None
    new_level = None

    if user[5] == 1:
        reward = 10
        till_next = 20 - user[4]
    elif user[5] == 2:
        reward = 15
        till_next = 30 - user[4]
    elif user[5] == 3:
        reward = 20
        till_next = 40 - user[4]
    elif user[5] == 4:
        reward = 25
        till_next = 50 - user[4]
    elif user[5] == 5:
        reward = 30
        till_next = 100000000

    if '-' in str(till_next) or till_next < 1:

        if user[5] == 1:
            new_level = 2
        elif user[5] == 2:
            new_level = 3
        elif user[5] == 3:
            new_level = 4
        elif user[5] == 4:
            new_level = 5
        elif user[5] == 5:
            new_level = 5

        cursor.execute("UPDATE users SET level=? WHERE user_id=?", (new_level, message.from_user.id,))
        conn.commit()

        user = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()

    if till_next > 50:
        till_next = 0

    created_at_str = str(user[13])
    created_at = datetime.datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()

    diff = now - created_at
    days = diff.days

    profile_generator.draw_profile(message.from_user.id, message.from_user.username, int(user[5]), int(days), int(refs),
                                   float(user[4]), till_next)

    status = 'Игрок' if message.from_user.id not in config.ADMINS else 'Администратор' if message.from_user.id in config.ADMINS else 'Модератор' if \
    user[7] != 1 else 'Игрок'

    await message.answer("💎")

    await asyncio.sleep(1)

    try:
        await message.answer_photo(photo=FSInputFile(f"profiles/{str(message.from_user.id)}_banner.png"),
                                   caption=f"""<b>[💎] Твой профиль <code>[{message.from_user.id}]</code></b>, <i><b>{user[5]}</b> уровень</i><b>

Вознаграждение: <code>{reward}%</code>
Приглашено: <code>{refs} игроков</code>
Баланс: <code>{user[3]:.2f} $</code>
Статус: <code>{status}</code>
Способ выплаты: <code>CryptoBot USDT</code>

В команде: <code>{days_text(days)}</code></b>""", reply_markup=kb.profile())
    except Exception as e:
        print(f"Error when sending profile photo: {e}")

@router.message(StateFilter(None), ChatTypeFilter(chat_type=["private"]), F.text)
async def handlers(message: types.Message, state: FSMContext):
    await state.clear()

    args = message.text.split(" ")
    emoji = None

    if len(args) > 1:
        if args[0] == '/start':
            if args[1].isdigit():
                if int(args[1]) != int(message.from_user.id):
                    referrer = cursor.execute("SELECT * FROM users WHERE id=?", (args[1],)).fetchone()
                    if referrer:
                        exist = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()
                        if not exist:
                            cursor.execute("INSERT INTO users(user_id,first_name,username,ref) VALUES(?,?,?,?)", (message.from_user.id,message.from_user.first_name,message.from_user.username,args[1]))
                            conn.commit()

                            await message.answer(f"Вы успешно зарегистрировались в системе по реферальной ссылке {referrer[2]} !")
                            await bot.send_message(referrer[1], f"👤 По вашей ссылке зарегистрировался <code>{message.from_user.first_name}  ({message.from_user.id})</code>")

    exist = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()
    if not exist:
        cursor.execute("INSERT INTO users(user_id,first_name) VALUES(?,?)", (message.from_user.id,message.from_user.first_name,))
        conn.commit()
    else:
        cursor.execute("UPDATE users SET first_name=?, username=? WHERE user_id=?", (message.from_user.first_name,message.from_user.username,message.from_user.id,))
        conn.commit()

    user = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()

    if 'профиль' in message.text.lower() or 'статистика' in message.text.lower() or 'реферальная' in message.text.lower() or 'админ' in message.text.lower() or '/start' in message.text.lower():
        emoji = message.text[0]

        if 'реферальная' in message.text.lower():
            emoji = "💸"
        elif '/start' in message.text.lower():
            emoji = "💎"

        await message.answer(emoji, reply_markup=kb.main(message.from_user.id))
        await asyncio.sleep(1)

    if 'профиль' in message.text.lower() or '/start' in message.text.lower():
        refs = cursor.execute("SELECT COUNT(*) FROM users WHERE ref=?", (user[0],)).fetchone()[0]

        reward = None
        till_next = None
        new_level = None

        if user[5] == 1:
            reward = 10
            till_next = 20 - user[4]
        elif user[5] == 2:
            reward = 15
            till_next = 30 - user[4]
        elif user[5] == 3:
            reward = 20
            till_next = 40 - user[4]
        elif user[5] == 4:
            reward = 25
            till_next = 50 - user[4]
        elif user[5] == 5:
            reward = 30
            till_next = 100000000

        if '-' in str(till_next) or till_next < 1:

            if user[5] == 1:
                new_level = 2
            elif user[5] == 2:
                new_level = 3
            elif user[5] == 3:
                new_level = 4
            elif user[5] == 4:
                new_level = 5
            elif user[5] == 5:
                new_level = 5

            cursor.execute("UPDATE users SET level=? WHERE user_id=?", (new_level,message.from_user.id,))
            conn.commit()

            user = cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()

        if till_next > 50:
            till_next = 0

        created_at_str = str(user[13])
        created_at = datetime.datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()

        diff = now - created_at
        days = diff.days

        profile_generator.draw_profile(message.from_user.id, message.from_user.username, int(user[5]), int(days), int(refs), float(user[4]), till_next)

        status = 'Игрок' if message.from_user.id not in config.ADMINS else 'Администратор' if message.from_user.id in config.ADMINS else 'Модератор' if user[7] != 1 else 'Игрок'

        try:
            await message.answer_photo(photo=FSInputFile(f"profiles/{str(message.from_user.id)}_banner.png"), caption=f"""<b>[{emoji}] Твой профиль <code>[{message.from_user.id}]</code></b>, <i><b>{user[5]}</b> уровень</i><b>

Вознаграждение: <code>{reward}%</code>
Приглашено: <code>{refs} игроков</code>
Баланс: <code>{user[3]:.2f} $</code>
Статус: <code>{status}</code>
Способ выплаты: <code>CryptoBot USDT</code>

В команде: <code>{days_text(days)}</code></b>""", reply_markup=kb.profile())
        except Exception as e:
            print(f"Error when sending profile photo: {e}")
    elif 'реферальная' in message.text.lower():
        bot_info = await bot.get_me()

        await message.answer_photo(photo=FSInputFile("ref.jpg"), caption=f"""<b>[💰] Реферальная система

Получайте до <code>30%</code> от каждого проигрыша приглашённого вами игрока, повышая ваш уровень.

<blockquote>Ваша реферальная ссылка:</blockquote>
<a href="https://t.me/{bot_info.username}?start={user[0]}">ЗАЖМИТЕ И СКОПИРУЙТЕ</a></b>""", reply_markup=kb.ref(user[0], bot_info))
    elif 'статистика' in message.text.lower():
        total_bets = cursor.execute("SELECT COUNT(*) FROM bets WHERE user_id=?", (message.from_user.id,)).fetchone()[0]
        total_bets_summ = cursor.execute("SELECT SUM(amount) FROM bets WHERE user_id=?", (message.from_user.id,)).fetchone()[0]
        total_bets_summ = f"{total_bets_summ:.2f}" if total_bets_summ else f"{float(0):.0f}"
        total_win = cursor.execute("SELECT COUNT(*) FROM bets WHERE win=1 AND user_id=?", (message.from_user.id,)).fetchone()[0]
        total_lose = cursor.execute("SELECT COUNT(*) FROM bets WHERE lose=1 AND user_id=?", (message.from_user.id,)).fetchone()[0]
        total_draw = cursor.execute("SELECT COUNT(*) FROM bets WHERE draw=1 AND user_id=?", (message.from_user.id,)).fetchone()[0]
        await message.answer_photo(photo=FSInputFile("stats.jpg"), caption=f"""<b>[{emoji}] Ваша статистика по казино:

Выигрыши: <code>{total_win} побед(а).</code>

Проигрыши: <code>{total_lose} поражение.</code>

Ничья: <code>{total_draw} ничьи.</code>

Общее количество сыгранных игр: <code>{total_bets} игр.</code>

Сумма всех ставок: <code>{total_bets_summ} $.</code></b>""")
    elif 'админ' in message.text.lower():
        if message.from_user.id not in config.ADMINS:
            await message.answer("<b>Доступ запрещен.</b>")
            return

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

        await message.answer("<b>Доступ разрешен.</b>")
        await message.answer(f"<b><blockquote>Количество пользователей - {total_users} шт.</blockquote>\n\n<blockquote>Всего ставок - <code>{total_bets}</code> шт. [~ <code>{total_bets_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Количество выигрышей - <code>{total_wins}</code> шт. [~ <code>{total_wins_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Количество проигрышей - <code>{total_lose}</code> шт. [~ <code>{total_lose_summ:.2f}</code> $]</blockquote>\n\n<blockquote>Количество ничьи - <code>{total_draw}</code> шт. [~ <code>{total_draw_summ}</code> $]</blockquote></b>", reply_markup=kb.admin())