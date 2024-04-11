from telegram import InlineKeyboardButton

BUY_ONE_WEEK, BUY_ONE_MONTH, BUY_ONE_YEAR, SCHEDULE, SIGN, SUBSCRIPTION, BUY, CHOOSE_ACTION, PREVIOUS, NEXT, DAY = (
    range(0, 11))

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