TOKEN = "6894507056:AAEcCdFJRHqzY75Q_sHMWELs5WwIY1KfBWk" # Токен бота
PAYMENTS_URL = "https://t.me/+URFxwN-Q_UBiNTky" # Канал выплат
BETS_ID = -1002238635644 # ID Канала со ставками (НЕ С ПЛАТЕЖАМИ)
BROKER_ID = -1002238635644 # ID Канала с платежами (НЕ СО СТАВКАМИ)
VUVOD_ID = -1002149445368 # ID Канала с заявками на вывод
CHAT_ID = -1002221565734 # ID Чата
USER_AGREEMENT = "https://telegra.ph/Polzovatelskoe-Soglashenie-proekta-TetherBet-08-28" # Пользовательское соглашение
STAVKA_URL = "https://t.me/send?start=IV3ZZIjS3gLO" # Ссылка на счёт CryptoBot
RULES_URL = "https://t.me/+fMhi5Mkb0mg1MTli" # Ссылка на канал правил
SUPPORT_URL = "https://t.me/vemorr" # Ссылка на тех поддержку
NEWS_URL = "https://t.me/+4IErPhfRr2ozN2Y6" # Ссылка на новостной канал
CHAT_URL = "https://t.me/+YdUvOb4EHGZiMWQy" # Ссылка на чат
CRYPTOPAY_TOKEN = "239640:AAuCFAyAuZp6NyKv1SqDL28aTPfsl3Y2mEe" # Токен CryptoPay
ADMINS = [640612893] # ID Администраторов через запятую
NAME = "Tether Bet" # Название
TEAM_NAME = "TETHER TEAM" # Название в FAQ

# Игры, формат: 'игра': ("эмоджи", [значения выигрышные])
GAMES = {
    'чет': ("🎲", [2, 4, 6]),
    'нечет': ("🎲", [1, 3, 5]),
    'больше': ("🎲", [4, 5, 6]),
    'меньше': ("🎲", [1, 2, 3]),
    'победа1': ("🎲", [1]),
    'победа2': ("🎲", [1]),
    'ничья': ("🎲", [1]),
}

# Коэффиценты, формат: 'игра': коэффицент
COEFS = {
    'чет': 1.8,
    'нечет': 1.8,
    'больше': 1.8,
    'меньше': 1.8,
    'победа1': 1.8,
    'победа2': 1.8,
    'ничья': 3
}