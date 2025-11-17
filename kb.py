from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import config
import sqlite3

def main(userid):
    btns = [
        [KeyboardButton(text="💎 Профиль")],
        [KeyboardButton(text="🔗 Реферальная система"), KeyboardButton(text="📊 Статистика")]
    ]

    if userid in config.ADMINS:
        btns.append([KeyboardButton(text="🚀 Админ-Панель")])

    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=btns)
    return kb

def profile():
    btns = [
        [InlineKeyboardButton(text="💸 Вывести", callback_data='withdraw'), InlineKeyboardButton(text="📚 FAQ", callback_data='faq')],
        [InlineKeyboardButton(text="🛡 Канал с выплатами", url=config.PAYMENTS_URL)]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb

def ref(userid, bot_info):
    btns = [
        #[InlineKeyboardButton(text="➕ Пригласить друга", url=f"https://t.me/share/url?url=https://t.me/{bot_info.username}?start={userid}&text=")],
        [InlineKeyboardButton(text='➕ Пригласить друга', switch_inline_query=f'https://t.me/{bot_info.username}?start={userid}')],
        [InlineKeyboardButton(text="🗄 Мои рефералы", callback_data='my_refs')]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb

def faq(page):
    if int(page) == 1:
        btns = [
            [InlineKeyboardButton(text="❌ Выйти", callback_data="close"), InlineKeyboardButton(text="Вперёд ˒", callback_data=f"faq:{page + 1}")]
        ]
    elif int(page) < 6:
        btns = [
            [InlineKeyboardButton(text="˓ Назад", callback_data=f"faq:{page-1}"), InlineKeyboardButton(text="Вперёд ˒", callback_data=f"faq:{page+1}")]
        ]
    else:
        btns = [
            [InlineKeyboardButton(text="˓ Назад", callback_data=f"faq:{page - 1}"), InlineKeyboardButton(text="Закрыть ˒", callback_data="close")]
        ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def bet_kb():
    btns = [
        [InlineKeyboardButton(text="Сделать ставку", url=config.STAVKA_URL)],
        [InlineKeyboardButton(text="Пользовательское соглашение", url=config.USER_AGREEMENT)]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def rules_kb():
    btns = [
        [InlineKeyboardButton(text='Правила', url=config.RULES_URL)]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def admin():
    btns = [
        [InlineKeyboardButton(text="💵 Управление пользователями", callback_data='page_1'), InlineKeyboardButton(text="Управление казной 💵", callback_data='control_kazna')],
        [InlineKeyboardButton(text="💵 Управление подкрутом️", callback_data='podkrut'), InlineKeyboardButton(text="Конкурсы 💵", callback_data='contests')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def control_kazna():
    btns = [
        [InlineKeyboardButton(text="💵 Пополнить казну", callback_data='popol'), InlineKeyboardButton(text="Вывести казну 💵", callback_data='withd')],
        [InlineKeyboardButton(text="💵 Баланс 💵", callback_data='balance')],
        [InlineKeyboardButton(text="↩️ Назад", callback_data='admin')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def podkrut():
    with sqlite3.connect("db.db") as conn:
        cursor = conn.cursor()
        podkrut_status, prokrut = cursor.execute("SELECT * FROM podkrut").fetchone()

    print(prokrut)

    btns = []

    if podkrut_status == 0:
        btns.append([InlineKeyboardButton(text="🔋 Включить", callback_data='set_podkrut:1')])
    else:
        btns.append([InlineKeyboardButton(text="🏮 Выключить", callback_data='set_podkrut:0')])

    prokrut_text, prokrut_call = None, None

    if prokrut == 2:
        prokrut_text = "2️⃣"
        prokrut_call = "set_prokrut:3"
    elif prokrut == 3:
        prokrut_text = "3️⃣"
        prokrut_call = "set_prokrut:2"

    btns.append([InlineKeyboardButton(text=prokrut_text, callback_data=prokrut_call)])

    btns.append([InlineKeyboardButton(text="↩️ Назад", callback_data='admin')])

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def back(call):
    btns = [
        [InlineKeyboardButton(text="↩️ Назад", callback_data=call)]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def pay(invoice):
    btns = [
        [InlineKeyboardButton(text="💵 Оплатить 💵", url=invoice)],
        [InlineKeyboardButton(text="↩️ Назад", callback_data='admin')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def get_pagination_keyboard(page: int, total_pages: int, users):
    btns = []
    userss = []

    for i in range(0, len(users), 3):
        row = [
            InlineKeyboardButton(text=str(user[1]) if user[1] else str(user[2]), callback_data=f"user:{user[0]}")
            for user in users[i:i + 3]
        ]
        userss.append(row)

    btns.extend(userss)

    arrows = []
    if page > 1:
        arrows.append(InlineKeyboardButton(text="<<", callback_data=f"page_{page - 1}"))
    if page < total_pages:
        arrows.append(InlineKeyboardButton(text=">>", callback_data=f"page_{page + 1}"))
    btns.append(arrows)

    btns.append([InlineKeyboardButton(text="🔍 Поиск", callback_data='search_user'),
                 InlineKeyboardButton(text="↩️ Назад", callback_data='admin')])

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

async def get_users_keyboard(page: int):
    limit = 12
    offset = (page - 1) * limit

    with sqlite3.connect("db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = (cursor.fetchone())[0]
        total_pages = (total_users + limit - 1) // limit

        cursor.execute("SELECT id, first_name, user_id FROM users LIMIT ? OFFSET ?", (limit, offset))
        users = cursor.fetchall()

    keyboard = get_pagination_keyboard(page, total_pages, users)
    return keyboard

def control_user(userid, mod, ban):
    mod_text = "💵 Отозвать модератора 💵" if mod == 1 else '💵 Выдать модератора 💵'
    mod_call = f"set_mod:{userid}:0" if mod == 1 else f"set_mod:{userid}:1"

    ban_text = "💵 Разбанить 💵" if ban == 1 else '💵 Забанить 💵'
    ban_call = f"set_ban:{userid}:0" if ban == 1 else f"set_ban:{userid}:1"

    btns = [
        [InlineKeyboardButton(text="💵 Отправить сообщение 💵", callback_data=f'msg:{userid}')],
        [InlineKeyboardButton(text=mod_text, callback_data=mod_call)],
        [InlineKeyboardButton(text=ban_text, callback_data=ban_call)],
        [InlineKeyboardButton(text="↩️ Назад", callback_data='admin')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def found(user):
    btns = []

    if user:
        btns.append([InlineKeyboardButton(text=user[2], callback_data=f'user:{user[0]}')])
    else:
        btns.append([InlineKeyboardButton(text="Нету результатов.", callback_data='empty')])

    btns.append([InlineKeyboardButton(text="↩️ Назад", callback_data='admin')])

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def control(user_id, panel_id):
    btns = [
        [InlineKeyboardButton(text="💵 Забанить", callback_data=f'ban:{user_id}:{panel_id}'), InlineKeyboardButton(text="Замутить 💵", callback_data=f'mute:{user_id}:{panel_id}')],
        [InlineKeyboardButton(text="💵 Закрыть 💵", callback_data=f'delete:{panel_id}')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def close(panel_id):
    btns = [
        [InlineKeyboardButton(text="💵 Закрыть 💵", callback_data=f'delete:{panel_id}')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def mutes(user_id, panel_id):
    btns = [
        [InlineKeyboardButton(text="10 мин.", callback_data=f'mutee:{user_id}:10:{panel_id}'), InlineKeyboardButton(text="15 мин.", callback_data=f'mutee:{user_id}:15:{panel_id}'), InlineKeyboardButton(text='20 мин.', callback_data=f'mutee:{user_id}:20:{panel_id}')],
        [InlineKeyboardButton(text='25 мин.', callback_data=f'mutee:{user_id}:25:{panel_id}'), InlineKeyboardButton(text='30 мин.', callback_data=f'mutee:{user_id}:30:{panel_id}'), InlineKeyboardButton(text='35 мин.', callback_data=f'mutee:{user_id}:35:{panel_id}')],
        [InlineKeyboardButton(text='40 мин.', callback_data=f'mutee:{user_id}:40:{panel_id}'), InlineKeyboardButton(text='45 мин.', callback_data=f'mutee:{user_id}:45:{panel_id}'), InlineKeyboardButton(text='50 мин.', callback_data=f'mutee:{user_id}:50:{panel_id}')],
        [InlineKeyboardButton(text='55 мин.', callback_data=f'mutee:{user_id}:55:{panel_id}'), InlineKeyboardButton(text='1 ч.', callback_data=f'mutee:{user_id}:60:{panel_id}'), InlineKeyboardButton(text="1 д.", callback_data=f'mutee:{user_id}:1440:{panel_id}')],
        [InlineKeyboardButton(text="💵 Закрыть 💵", callback_data=f'delete:{panel_id}')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def vuvod():
    btns = [
        [InlineKeyboardButton(text='🏮 В ожидании', callback_data='vuvod:0')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def contests():
    btns = [
        [InlineKeyboardButton(text='💵 Запустить конкурс', callback_data='create_contest'), InlineKeyboardButton(text='Остановить все активные конкурсы 💵', callback_data='stop_all')],
        [InlineKeyboardButton(text='↩️ Назад', callback_data='admin')]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb

def support():
    btns = [
        [InlineKeyboardButton(text='Поддержка', url=config.SUPPORT_URL)]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    return kb