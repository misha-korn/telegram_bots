from telegram import InlineKeyboardButton

SCHEDULE, SIGN, SUBSCRIPTION, BUY, CHOOSE_ACTION = range(1, 6)

keyboard_start = [
        [
            # первая строчка кнопочек
            InlineKeyboardButton('расписание', callback_data=str(SCHEDULE)),
            InlineKeyboardButton('запись', callback_data=str(SIGN)),
        ], [
            InlineKeyboardButton('абонемент', callback_data=str(SUBSCRIPTION)),
        ], [
            InlineKeyboardButton('купить', callback_data=str(BUY))
        ]
]