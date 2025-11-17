import random, string, requests, config, re, sqlite3, kb, asyncio
import make_duel

from aiogram.client.default import DefaultBotProperties
from aiogram import types, Router, Bot
from aiogram.types import FSInputFile
from datetime import datetime

router = Router()
bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

conn = sqlite3.connect("db.db")
cursor = conn.cursor()


fast_games = {
    '2': "🪐",
    '3': "🌸",
    '4': "🐟",
    '5': "🐠",
    '6': "🐡",
    '10': "🐸",
    '20': "🐬",
    '50': "🐳"
}

def generate_random_code(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def transfer(amount, us_id):
    amount = float(amount)
    try:
        spend_id = generate_random_code(length=10)
        headers = {"Crypto-Pay-API-Token": config.CRYPTOPAY_TOKEN}
        data = {"asset": "USDT", "amount": float(amount), "user_id": us_id, "spend_id": spend_id}
        r = requests.get("https://pay.crypt.bot/api/transfer", data=data, headers=headers).json()

        if r['ok'] == True:
            return True
        else:
            return False
    except Exception as e:
        print(e)

        return False

def get_cb_balance():
    headers = {"Crypto-Pay-API-Token": config.CRYPTOPAY_TOKEN}
    r = requests.get("https://pay.crypt.bot/api/getBalance", headers=headers).json()
    for currency_data in r['result']:
        if currency_data['currency_code'] == 'USDT':
            usdt_balance = currency_data['available']
            break
    return usdt_balance

def parser(message: types.Message):
    # Надежный способ получения через entities ниже

    if message.entities:
        if message.entities[0].user:
            user = message.entities[0].user
            name = user.full_name
            msg_text = message.text.removeprefix(name).replace("🪙", "")
            name = re.sub(r'@[\w]+', '@t3th3r_bet', name) if '@' in name else name
            user_id = int(user.id)
            asset = msg_text.split("отправил(а)")[1].split()[1]
            amount = float(msg_text.split("отправил(а)")[1].split()[0].replace(',', ""))

            if '💬' in message.text:
                comment = message.text.split("💬 ")[1].lower()
                game = comment.replace("ё", "е").replace("ное", "").replace(" ", "").replace("куб", "").replace("х", "x")
            else:
                comment = None
                game = None

            return {
                'id': user_id,
                'name': name,
                'usd_amount': amount,
                'asset': asset,
                'comment': comment,
                'game': game
            }

async def result_msg(parsed_data, winning_values, dice_result, bet_msg=None):
    text = ""
    duel = None
    duel1 = None
    dice1 = None
    dice2 = None
    result = None
    image = None
    dice_msg_id = None

    if parsed_data['game'] in ['победа1', 'победа2', 'ничья']:
        dice1 = dice_result
        podkrut_status, prokrut = cursor.execute("SELECT * FROM podkrut").fetchone()

        if podkrut_status == 0:
            dice2 = await bot.send_dice(config.BETS_ID)
        else:
            dice2 = await bot.send_dice(config.BETS_ID)
            if prokrut == 2:
                await dice2.delete()
                dice2 = await bot.send_dice(config.BETS_ID)
            elif prokrut == 3:
                await dice2.delete()
                dice2 = await bot.send_dice(config.BETS_ID)
                await dice2.delete()
                dice2 = await bot.send_dice(config.BETS_ID)

        dice2 = dice2.dice.value

        if dice1 > dice2:
            duel = 1
            duel1 = 'первого'
        elif dice1 < dice2:
            duel = 2
            duel1 = 'второго'
        elif dice1 == dice2:
            duel = 3

        if parsed_data['game'] == 'победа1':
            result = dice1 > dice2
        elif parsed_data['game'] == 'победа2':
            result = dice1 < dice2
        elif parsed_data['game'] == 'ничья':
            result = dice1 == dice2

        if duel == 1:
            image = 'dice/win1.jpg'
        elif duel == 2:
            image = 'dice/win2.jpg'
        elif duel == 3:
            image = 'dice/draw.jpg'

    else:
        result = dice_result in winning_values

    if parsed_data['game'] == 'чет' and result == True:
        image = 'dice/odd.jpg'
    elif parsed_data['game'] == 'нечет' and result == True:
        image = 'dice/non_odd.jpg'
    elif parsed_data['game'] == 'больше' and result == True:
        image = 'dice/more.jpg'
    elif parsed_data['game'] == 'меньше' and result == True:
        image = 'dice/less.jpg'
    elif parsed_data['game'] == 'чет' and result == False:
        image = 'dice/non_odd.jpg'
    elif parsed_data['game'] == 'нечет' and result == False:
        image = 'dice/odd.jpg'
    elif parsed_data['game'] == 'больше' and result == False:
        image = 'dice/less.jpg'
    elif parsed_data['game'] == 'меньше' and result == False:
        image = 'dice/more.jpg'

    if result:
        win_amount = float(parsed_data['usd_amount']) * config.COEFS[parsed_data['game']]

        if parsed_data['game'] not in ['победа1', 'победа2', 'ничья']:
            cursor.execute("INSERT INTO bets(win,amount,win_amount,user_id) VALUES(1,?,?,?)", (parsed_data['usd_amount'],win_amount,parsed_data['id'],))
            conn.commit()

            text += f"<b>Победа! Выпало значение {dice_result}.\n\n"
        elif parsed_data['game'] in ['ничья'] and duel == 3:
            cursor.execute("INSERT INTO bets(draw,amount,win_amount,user_id) VALUES(1,?,?,?)", (parsed_data['usd_amount'],win_amount, parsed_data['id'],))
            conn.commit()

            text += f"<b>Победа! Сессия закрыта [{dice1}:{dice2}], ничья.\n\n"
        else:
            cursor.execute("INSERT INTO bets(win,amount,win_amount,user_id) VALUES(1,?,?,?)", (parsed_data['usd_amount'],win_amount, parsed_data['id'],))
            conn.commit()

            text += f"<b>Победа! Сессия закрыта [{dice1}:{dice2}] в пользу {duel1} кубика.\n\n"

        transferr = await transfer(win_amount, parsed_data['id'])
        if transferr:
            text += f"</b><blockquote><code>На баланс победителя была зачислена сумма в размере {win_amount:.2f}$.</code> <i>Бросай кости заново и испытай свою удачу!</i></blockquote>\n\n"
        else:
            text += f"</b><blockquote><code>Сумма в размере {win_amount:.2f}$ будет зачислена администрацией вручную.</code> <i>Бросай кости заново и испытай свою удачу!</i></blockquote>\n\n"
    else:
        user = cursor.execute("SELECT * FROM users WHERE user_id=?", (parsed_data['id'],)).fetchone()

        if user[6] is not None:
            referrer = cursor.execute("SELECT * FROM users WHERE id=?", (user[6],)).fetchone()
            profit = None

            lvl = referrer[5] if referrer[5] else 1

            if int(lvl) == 1:
                profit = float(parsed_data['usd_amount']) * (10 / 100)
            elif int(lvl) == 2:
                profit = float(parsed_data['usd_amount']) * (15 / 100)
            elif int(lvl) == 3:
                profit = float(parsed_data['usd_amount']) * (20 / 100)
            elif int(lvl) == 4:
                profit = float(parsed_data['usd_amount']) * (25 / 100)
            elif int(lvl) == 5:
                profit = float(parsed_data['usd_amount']) * (30 / 100)

            cursor.execute("UPDATE users SET total_got=total_got+?, balance=balance+? WHERE id=?", (profit,profit,referrer[0],))
            conn.commit()

        if parsed_data['game'] not in ['победа1', 'победа2', 'ничья']:
            cursor.execute("INSERT INTO bets(lose,amount,user_id) VALUES(1,?,?)", (parsed_data['usd_amount'], parsed_data['id'],))
            conn.commit()

            text += f"<b>Проигрыш! Выпало значение {dice_result}.\n\n"
        elif parsed_data['game'] in ['ничья'] or duel == 3:
            cursor.execute("INSERT INTO bets(draw,amount,user_id) VALUES(1,?,?)", (parsed_data['usd_amount'], parsed_data['id'],))
            conn.commit()

            text += f"<b>Проигрыш! Сессия закрыта [{dice1}:{dice2}], ничья.\n\n"
        else:
            cursor.execute("INSERT INTO bets(lose,amount,user_id) VALUES(1,?,?)", (parsed_data['usd_amount'], parsed_data['id'],))
            conn.commit()

            text += f"<b>Проигрыш! Сессия закрыта [{dice1}:{dice2}] в пользу {duel1} кубика.\n\n"

        text += "</b><blockquote><i>Бросай кубик заново и испытай свою удачу!</i></blockquote>\n\n"

    me = await bot.get_me()

    text += f"""<b><a href="{config.RULES_URL}">Правила</a> | <a href="{config.NEWS_URL}">Новостной Канал</a>  | <a href="{config.CHAT_URL}">Наш Чат</a>  | <a href="https://t.me/{me.username}">Реферальный Бот</a>  | <a href="{config.SUPPORT_URL}">Техническая Поддержка</a></b>"""

    return text, image

async def handle_bet(parsed_data):
    emoji, winning_values = config.GAMES[parsed_data['game']]
    dice = None

    bet_msg = await bot.send_message(config.BETS_ID,
                           f"""<b>[💎] Новая ставка

<blockquote>Никнейм игрока: {parsed_data['name']}</blockquote>

<blockquote>Сумма ставки: {parsed_data['usd_amount']:.2f} $</blockquote>

<blockquote>Исход ставки: {parsed_data['comment']}</blockquote></b>""")

    if parsed_data['game'] in ['победа1', 'победа2', 'ничья']:
        try:
            podkrut_status, prokrut = cursor.execute("SELECT * FROM podkrut").fetchone()

            if podkrut_status == 0:
                dice1 = await bot.send_dice(config.BETS_ID, emoji=emoji)
            else:
                dice1 = await bot.send_dice(config.BETS_ID, emoji=emoji)

                if prokrut == 2:
                    await dice1.delete()
                    dice1 = await bot.send_dice(config.BETS_ID, emoji=emoji)
                elif prokrut == 3:
                    await dice1.delete()
                    dice1 = await bot.send_dice(config.BETS_ID, emoji=emoji)
                    await dice1.delete()
                    dice1 = await bot.send_dice(config.BETS_ID, emoji=emoji)
        except Exception as e:
            await bot.send_message(config.BETS_ID, f"""<b>[❌] Ошибка!</b>\n\n<blockquote>Похоже что у нас вышла ошибка при отправке кубика, пожалуйста обратитесь в <a href="{config.SUPPORT_URL}">поддержку</a> чтобы получить ваши средства обратно.</blockquote>\n\n<i>Код ошибки: <code>FloodDice103</code></i>""", reply_markup=kb.bet_kb())
            print(f"Error sending dice: {e}")
            return

        result_text, image = await result_msg(parsed_data, winning_values, dice1.dice.value)
    else:
        try:
            podkrut_status, prokrut = cursor.execute("SELECT * FROM podkrut").fetchone()

            if podkrut_status == 0:
                dice = await bot.send_dice(config.BETS_ID, emoji=emoji)
            else:
                dice = await bot.send_dice(config.BETS_ID, emoji=emoji)

                if prokrut == 2:
                    await dice.delete()
                    dice = await bot.send_dice(config.BETS_ID, emoji=emoji)
                elif prokrut == 3:
                    await dice.delete()
                    dice = await bot.send_dice(config.BETS_ID, emoji=emoji)
                    await dice.delete()
                    dice = await bot.send_dice(config.BETS_ID, emoji=emoji)
        except Exception as e:
            print(f"Error sending dice: {e}")
            return

        result_text, image = await result_msg(parsed_data, winning_values, dice.dice.value, bet_msg.message_id)

    await asyncio.sleep(3)

    try:
        if image:
            if parsed_data['comment'] not in ['победа1', 'победа2', 'ничья']:
                await bot.send_photo(config.BETS_ID, FSInputFile(str(image)), caption=result_text,
                                reply_markup=kb.bet_kb(), reply_to_message_id=dice.message_id)
            else:
                await bot.send_photo(config.BETS_ID, FSInputFile(str(image)), caption=result_text,
                                     reply_markup=kb.bet_kb())
        else:
            if parsed_data['comment'] not in ['победа1', 'победа2', 'ничья']:
                await bot.send_message(config.BETS_ID, text=result_text, reply_markup=kb.bet_kb(),
                                   disable_web_page_preview=True, reply_to_message_id=dice.message_id)
            else:
                await bot.send_message(config.BETS_ID, text=result_text, reply_markup=kb.bet_kb(),
                                       disable_web_page_preview=True)
    except Exception as e:
        print(f"Error sending photo: {e}")

    await check_contest()
    await update_contest(parsed_data['name'], parsed_data['usd_amount'])

@router.channel_post()
async def channel_post_handler(message: types.Message):
    if message.chat.id == config.BROKER_ID:
        if not 'tg://user?id=' in message.md_text:
            await message.delete()
            await bot.send_message(config.BETS_ID, """<b>[❌] Ошибка!</b>

<i>включите, пожалуйста пересылку сообщений в настройках.</i>
<blockquote><code>Настройки телеграмма ➙ Конфиденциальность ➙ Пересылка сообщений ➙ ( Кто может ссылаться на мой аккаунт при пересылке сообщений )</code></blockquote>""", reply_markup=kb.bet_kb())
            return

        parsed_data = parser(message)
        await message.delete()
        await bot.send_message(config.BETS_ID, f"<b>[✅] {parsed_data['name']}, ваша ставка принята в работу!</b>")

        if not '💬' in message.text:
            summa = float(parsed_data['usd_amount']) * (90 / 100)

            if float(get_cb_balance()) < summa:
                status = 'Заберите ваши денежные средства у поддержки'
                markup = kb.support()
            else:
                try:
                    await transfer(summa, parsed_data['id'])
                    status = 'Был совершён возврат денежных средств'
                    markup = None
                except:
                    status = 'Ошибка при отправке возврата, заберите ваши денежные средства через поддержку'
                    markup = kb.support()

            await bot.send_message(config.BETS_ID, f"""<b>[❌] Ошибка!</b>

<b>{parsed_data['name']}</b>  <b>-</b> <b>Вы</b> <i>забыли дописать комментарий к игре.</i>
<b><u>{status}</u></b>

<blockquote><code>Комиссия составляет: 10%.</code></blockquote>""", reply_markup=markup)
            return

        if parsed_data:
            user = cursor.execute("SELECT * FROM users WHERE user_id=?", (parsed_data['id'],)).fetchone()
            if not user:
                cursor.execute("INSERT INTO users(user_id) VALUES(?)", (parsed_data['id'],))
                conn.commit()

            if parsed_data['game'] in config.GAMES:
                await handle_bet(parsed_data)
            else:
                summa = float(parsed_data['usd_amount']) * (90 / 100)

                if float(get_cb_balance()) < summa:
                    status = 'Заберите ваши денежные средства у поддержки'
                    markup = kb.support()
                else:
                    try:
                        await transfer(summa, parsed_data['id'])
                        status = 'Был совершён возврат денежных средств'
                        markup = None
                    except:
                        status = 'Ошибка при отправке возврата, заберите ваши денежные средства через поддержку'
                        markup = kb.support()

                await bot.send_message(config.BETS_ID, f"""<b>[❌] Ошибка!</b>

<b>{parsed_data['name']}</b>  <b>-</b> <b>Вы</b> <i>написали неверный комментарий к игре.</i>
<b><u>{status}</u></b>

<blockquote><code>Комиссия составляет: 10%.</code></blockquote>""", reply_markup=markup)
                return
        else:
            return

async def update_contest(username, amount):
    text = """<b>💸 Конкурс</b>

<i>Игрок который сделает самую крупную ставку до %end_date%
— Получит %win_amount%$</i>

<blockquote><b>🥇 %top1% [%top1_summa%$]</b>

<b>🥈 %top2% [%top2_summa%$]</b>

<b>🥉 %top3% [%top3_summa%$]</b></blockquote>"""

    try:
        contest = cursor.execute("SELECT * FROM contests").fetchone()

        if contest[1] != username:
            top1 = username if contest[2] < amount and contest[3] != username and contest[5] != username or contest[1] == 'Пустое место' and contest[3] != username and contest[5] != username else 'Пустое место'
            top1_summa = amount if contest[2]  < amount and contest[3] != username and contest[5] != username or contest[1] == 'Пустое место' and contest[3] != username and contest[5] != username else contest[2]

            cursor.execute("UPDATE contests SET top1=?, top1_summa=? WHERE id=?", (top1, top1_summa, contest[0],))
            conn.commit()
        elif contest[3] != username:
            top2 = username if contest[4] < amount and contest[1] != username and contest[5] != username or contest[3] == 'Пустое место' and contest[1] != username and contest[5] != username else 'Пустое место'
            top2_summa = amount if contest[4] < amount and contest[1] != username and contest[5] != username or contest[3] == 'Пустое место' and contest[1] != username and contest[5] != username else contest[4]

            cursor.execute("UPDATE contests SET top2=?, top2_summa=? WHERE id=?", (top2, top2_summa, contest[0],))
            conn.commit()
        elif contest[5] != username:
            top3 = username if contest[6] < amount and contest[1] != username and contest[3] != username or contest[5] == 'Пустое место' and contest[1] != username and contest[3] != username else 'Пустое место'
            top3_summa = amount if contest[6] < amount or contest[5] == 'Пустое место' else contest[6]

            cursor.execute("UPDATE contests SET top3=?, top3_summa=? WHERE id=?", (top3,top3_summa,contest[0],))
            conn.commit()

        contest = cursor.execute("SELECT * FROM contests WHERE id=?", (contest[0],)).fetchone()

        if contest[10] != 1:
            text = text.replace("%end_date%", str(contest[7])).replace("%win_amount%", str(contest[8]))

            text = text.replace("%top1%", str(contest[1])).replace("%top1_summa%", str(contest[2]))
            text = text.replace("%top2%", str(contest[3])).replace("%top2_summa%", str(contest[4]))
            text = text.replace("%top3%", str(contest[5])).replace("%top3_summa%", str(contest[6]))

            try:
                await bot.edit_message_text(text, chat_id=config.BETS_ID, message_id=contest[9])
            except:
                pass
        else:
            cursor.execute("DELETE FROM contests WHERE id=?", (contest[0],))
            conn.commit()
            pass
    except:
        pass

async def check_contest():
    try:
        contests = cursor.execute("SELECT * FROM contests WHERE end=0").fetchall()
        if contests:
            for contest in contests:
                contest_end_str = contest[7]
                contest_end = datetime.strptime(contest_end_str, "%d.%m.%Y %H:%M")
                current_datetime = datetime.now()
                if current_datetime > contest_end:
                    await bot.send_message(config.BETS_ID,
                                           f"<b>♠️ Конкурс №{contest[0]} завершён!</b>\n<blockquote><b>Победитель должен забрать приз ({contest[8]}$) у администратора.</b></blockquote>",
                                           reply_to_message_id=contest[10])
                    cursor.execute("UPDATE contests SET end=1 WHERE id=?", (contest[0],))
                    conn.commit()
    except:
        pass