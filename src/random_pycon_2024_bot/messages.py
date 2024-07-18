import typing as tp

UNAUTHORIZED_MESSAGE = 'UNAUTHORIZED_MESSAGE'
UNAUTHORIZED_MESSAGE_RU = UNAUTHORIZED_MESSAGE_EN = """
(English version below)

Сорри, мы не знаем, кто ты.
Если ты наш пользователь, то возможно стоит подождать, в крайнем случае до завтра.

(English)

Hi,
it looks like you are unknown to bot.

If problem still persists, write to author: @serjflint
"""

FORBIDDEN_MESSAGE = 'FORBIDDEN_MESSAGE'
FORBIDDEN_MESSAGE_RU = """
Пардон, но для выполнения этой команды нужно быть модератором нашей системы.
"""
FORBIDDEN_MESSAGE_EN = """
You should be administrator.
"""

START_SUCCESS_MESSAGE = 'START_SUCCESS_MESSAGE'
START_SUCCESS_MESSAGE_RU = """
Привет! Авторизация пройдена успешно.
Набери /help чтобы узнать, что я умею.
"""
START_SUCCESS_MESSAGE_EN = """
Hi, access granted.
Type /help for supported commands.
"""

CANCEL_SUCCESS_MESSAGE = 'CANCEL_SUCCESS_MESSAGE'
CANCEL_SUCCESS_MESSAGE_RU = """
Окей.
"""
CANCEL_SUCCESS_MESSAGE_EN = """
OK
"""

STOP_SUCCESS_MESSAGE = 'STOP_SUCCESS_MESSAGE'
STOP_SUCCESS_MESSAGE_RU = """
Принято, больше не побеспокою.
Набери /start, если передумаешь.
Ну или просто напиши мне что-нибудь.
"""
STOP_SUCCESS_MESSAGE_EN = """
I will not disturb you.
Type /start or something else if you change your mind.
"""

ADMIN_HELP_MESSAGE = 'ADMIN_HELP_MESSAGE'
ADMIN_HELP_MESSAGE_RU = ADMIN_HELP_MESSAGE_EN = """
Администраторы (и ты тоже) могут выполнять следующие команды:

/leaderboard - посмотреть статистику бота по всем пользователям
/newround - сообщить ВСЕМ пользователям, что у них есть новые встречи (начало нового рауда)
/notifyall - напомнить ВСЕМ пользователям, что им нужно отметить встречи (по пятницам вызывать лучше всего)

Последние две команды присылают уведомления только тем пользователям, у которых есть незакрытые встречи.
"""

HELP_SUCCESS_MESSAGE = 'HELP_SUCCESS_MESSAGE'
HELP_SUCCESS_MESSAGE_RU = """
Бот умеет следующее:
/help - показать, что я умею
/stop - отказаться от использования этого бота

/who - список всех моих не закрытых встреч
/all - список всех моих встреч
/stats - моя статистика
/pass login - встреча была с login
/reset login - держать встречу, как запланированную (все встречи такие по умолчанию).
    Это значит, что она будет отображаться в /who листе
/deny login - встречи не было и не будет с login
/interests - список интересов

ВАЖНО! Если ты ПОДТВЕРДИЛ встречу (/pass), то это НЕЛЬЗЯ ОТКАТИТЬ. Мы против обмана и отказа от своих слов :)
"""
HELP_SUCCESS_MESSAGE_EN = """
Bot commands:
/help - list available commands
/stop - stop using bot

/who - list of my open meetings
/all - list of all my meetings
/stats - statistics
/pass login - mark meeting with login as done
/reset login - mark meeting as planned (default). It will be printed in /who response.
/deny login - mark meeting with login as declined

Attention: /pass action can't be undone. Be careful please :)
"""

STATS_MESSAGE = 'STATS_MESSAGE'
STATS_MESSAGE_RU = """
Итак, наслаждайся статистикой:
Всего назначено встреч: {all_m}
Встреч, которые проведены: {success_m}
Встреч, которые пока что не завершены: {not_yet_m}
Встреч, которые не будут завершены: {deny_m}
"""
STATS_MESSAGE_EN = """
Meeting statistics:
Created: {all_m}
Done: {success_m}
Waiting: {not_yet_m}
Declined: {deny_m}
"""

UNKNOWN_TEXT_MESSAGE = 'UNKNOWN_TEXT_MESSAGE'
UNKNOWN_TEXT_MESSAGE_RU = """
Пока что я не умею общаться с обычным человеческим языком.
Набери /help - узнаешь, что я умею
"""
UNKNOWN_TEXT_MESSAGE_EN = """
I can't speak human language by now.
Enter /help for list of my commands
"""

UNKNOWN_COMMAND_MESSAGE = 'UNKNOWN_COMMAND_MESSAGE'
UNKNOWN_COMMAND_MESSAGE_RU = UNKNOWN_COMMAND_MESSAGE_EN = """
(English version below)

Мне непонятна такая команда.
Используй /help для понимания того, что я умею.

(English)
Unknown command :(
Enter /help for list of my commands
"""

MESSAGE_NO_NEW_MEETINGS = 'MESSAGE_NO_NEW_MEETINGS'
MESSAGE_NO_NEW_MEETINGS_RU = """
У тебя нет новых встреч. Чтобы узнать информация обо всех встречах, введи /all
"""
MESSAGE_NO_NEW_MEETINGS_EN = """
You don't have new meetings. Enter /all for all meetings list.
"""

MESSAGE_NO_MEETINGS_AT_ALL = 'MESSAGE_NO_MEETINGS_AT_ALL'
MESSAGE_NO_MEETINGS_AT_ALL_RU = """
У тебя нет встреч. Вообще. Не знаю, как такое может быть :)
"""
MESSAGE_NO_MEETINGS_AT_ALL_EN = """
You don't have meetings at all. It is confusing to me :)
"""

WHO_FULL_MESSAGE = 'WHO_FULL_MESSAGE'
WHO_FULL_MESSAGE_RU = """
{greetings} (в порядке назначения):
{records}
"""
WHO_FULL_MESSAGE_EN = """
{greetings} (in order of creation):
{records}
"""
NEW_MEETING_MESSAGE = 'NEW_MEETING_MESSAGE'
NEW_MEETING_MESSAGE_RU = """
Привет! У тебя запланирована новая встреча.
{telegram}
совместные интересы: {interests}
""".strip()
NEW_MEETING_MESSAGE_EN = """
Hello! You have a new meeting scheduled.
{telegram}
joint interests: {interests}
""".strip()

WHO_MESSAGE_RECORD = 'WHO_MESSAGE_RECORD'
WHO_MESSAGE_RECORD_RU = """
статус встречи: {status}
{telegrams}
совместные интересы: {interests}
{additional}""".strip()
WHO_MESSAGE_RECORD_EN = """
meeting's status: {status}
{telegrams}
joint interests: {interests}
{additional}""".strip()

MEETING_STATUS_TEXTS = 'MEETING_STATUS_TEXTS'
MEETING_STATUS_TEXTS_RU = ['пока не было', 'состоялась', 'не состоится']
MEETING_STATUS_TEXTS_EN = ['waiting', 'done', 'declined']

STATUS_UPDATE_MESSAGE = 'STATUS_UPDATE_MESSAGE'
STATUS_UPDATE_MESSAGE_RU = """Готово."""
STATUS_UPDATE_MESSAGE_EN = """Done."""

HELP_UPDATE_STATUS_MESSAGE = 'HELP_UPDATE_STATUS_MESSAGE'
HELP_UPDATE_STATUS_MESSAGE_RU = """
Нужно выполнять команду в формате /{command} login
"""
HELP_UPDATE_STATUS_MESSAGE_EN = """
Command format: /{command} login
"""

UPDATE_MEETING_ERROR_MESSAGE = 'UPDATE_MEETING_ERROR_MESSAGE'
UPDATE_MEETING_ERROR_MESSAGE_RU = """
Информация о встрече не обновлена. Возможно, логин введен с ошибкой.
Если же была попытка поменять статус встречи, которая уже отмечена как прошедшая, то все пошло по плану.
Нельзя менять статус прошедших встреч :)
"""
UPDATE_MEETING_ERROR_MESSAGE_EN = """
Meeting info haven't updated. Wrong login?
Or you are trying to change status of already done meeting (it is ok).
"""

ADMIN_HELLO_MESSAGE = 'ADMIN_HELLO_MESSAGE'
ADMIN_HELLO_MESSAGE_RU = ADMIN_HELLO_MESSAGE_EN = """
Привет, админ! Ты отправил обычное сообщение.
Ты можешь сделать следующее:

/helpadmin - помощь по админским командам
/help - помощь по остальным командам

Больше я ничего не умею!
"""

LEADER_BOARD_MESSAGE = 'LEADER_BOARD_MESSAGE'
LEADER_BOARD_MESSAGE_RU = LEADER_BOARD_MESSAGE_EN = """
Итак:
Всего раундов: {all_rounds}
Всего авторизовались у бота: {all_auth}
Всего людей, участвовавших во встречах: {all_members}
Всего назначенных встреч: {all_meetings}
Всего подтвержденных встреч: {all_passed}
Всего отклоненных встреч: {all_denied}
Всего неотмеченных встреч (среди авторизовавшихся): {all_notyet}
"""

REMIND_PEOPLE_TO_MARK_MEETINGS = 'REMIND_PEOPLE_TO_MARK_MEETINGS'
REMIND_PEOPLE_TO_MARK_MEETINGS_RU = """
Привет! У тебя есть неподтвержденные встречи.
Нажми сюда: /who , чтобы узнать, что нужно подтверждать.

Чтобы узнать все команды бота, нажми сюда: /help
Чтобы отказаться от уведомлений этого бота, нажми сюда: /stop
"""
REMIND_PEOPLE_TO_MARK_MEETINGS_EN = """
Hi,
you have waiting meetings.
Press here: /who to list them.

All bot commands: /help
To stop bot notifications: /stop
"""

TELL_PEOPLE_THEY_HAVE_NEW_MEETINGS = 'TELL_PEOPLE_THEY_HAVE_NEW_MEETINGS'
TELL_PEOPLE_THEY_HAVE_NEW_MEETINGS_RU = """
Привет! У тебя есть новые встречи!
Нажми сюда: /who , чтобы узнать, что нужно подтверждать.

Чтобы узнать все команды бота, нажми сюда: /help
Чтобы отказаться от уведомлений этого бота, нажми сюда: /stop
"""
TELL_PEOPLE_THEY_HAVE_NEW_MEETINGS_EN = """
Hi,
you have new meetings!
Press here: /who to list them.

All bot commands: /help
To stop bot notifications: /stop
"""

ERROR_MESSAGE = 'ERROR_MESSAGE'
ERROR_MESSAGE_RU = ERROR_MESSAGE_EN = """
(English version below)
Что-то очень сильно пошло не так.
Возможно, это проблемы инфрастуктуры, возможно мы меняем версию и тд.

(English)
Something went wrong :(
We might are updating some stuff.
Thank you!
"""

ALL_YOUR_MEETINGS = 'ALL_YOUR_MEETINGS'
ALL_YOUR_MEETINGS_RU = 'Все твои встречи'
ALL_YOUR_MEETINGS_EN = 'All your meetings'

ALL_WAITING_MEETINGS = 'ALL_WAITING_MEETINGS'
ALL_WAITING_MEETINGS_RU = 'Твои незакрытые встречи'
ALL_WAITING_MEETINGS_EN = 'Your waiting meetings'

NAME_IS_UNKNOWN = 'NAME_IS_UNKNOWN'
NAME_IS_UNKNOWN_RU = '<имя неизвестно>'
NAME_IS_UNKNOWN_EN = '<unknown name>'

MEETING_ALREADY_DONE_LABEL = 'MEETING_ALREADY_DONE_LABEL'
MEETING_ALREADY_DONE_LABEL_RU = 'встреча уже состоялась'
MEETING_ALREADY_DONE_LABEL_EN = 'meeting is done'

MEETING_IS_DECLINED_LABEL = 'MEETING_IS_DECLINED_LABEL'
MEETING_IS_DECLINED_LABEL_RU = 'встреча не состоится'
MEETING_IS_DECLINED_LABEL_EN = 'meeting is declined'

TELEGRAM_MENTION = 'TELEGRAM_MENTION'
TELEGRAM_MENTION_RU = 'телеграм: [@{tg_login}](mention:{tg_login})'
TELEGRAM_MENTION_EN = 'telegram: [@{tg_login}](mention:{tg_login})'

CHOOSE_YOUR_INTERESTS = 'CHOOSE_YOUR_INTERESTS'
CHOOSE_YOUR_INTERESTS_RU = 'Выберите свои интересы'
CHOOSE_YOUR_INTERESTS_EN = 'Choose your interests'

INTEREST_ADDED = 'INTEREST_ADDED'
INTEREST_ADDED_RU = 'Добавлен интерес: '
INTEREST_ADDED_EN = 'Interest added: '

INTEREST_REMOVED = 'INTEREST_REMOVED'
INTEREST_REMOVED_RU = 'Удален интерес: '
INTEREST_REMOVED_EN = 'Interest removed: '

INTEREST_SELECTED_SIMBOL = 'INTEREST_SELECTED_SIMBOL'
INTEREST_SELECTED_SIMBOL_RU = '✅'
INTEREST_SELECTED_SIMBOL_EN = '✔️'

INTEREST_UNSELECTED_SIMBOL = 'INTEREST_UNSELECTED_SIMBOL'
INTEREST_UNSELECTED_SIMBOL_RU = '⚪'
INTEREST_UNSELECTED_SIMBOL_EN = ' '

NO_JOINT_INTERESTS = 'NO_JOINT_INTERESTS'
NO_JOINT_INTERESTS_RU = 'Определенно были...)))'
NO_JOINT_INTERESTS_EN = 'Interests were definitely....)))'

MESSAGES: tp.Mapping[str, tp.Mapping[str, str]] = {
    UNAUTHORIZED_MESSAGE: {
        'en': UNAUTHORIZED_MESSAGE_EN,
        'ru': UNAUTHORIZED_MESSAGE_RU,
    },
    FORBIDDEN_MESSAGE: {
        'en': FORBIDDEN_MESSAGE_EN,
        'ru': FORBIDDEN_MESSAGE_RU,
    },
    START_SUCCESS_MESSAGE: {
        'en': START_SUCCESS_MESSAGE_EN,
        'ru': START_SUCCESS_MESSAGE_RU,
    },
    CANCEL_SUCCESS_MESSAGE: {
        'en': CANCEL_SUCCESS_MESSAGE_EN,
        'ru': CANCEL_SUCCESS_MESSAGE_RU,
    },
    STOP_SUCCESS_MESSAGE: {
        'en': STOP_SUCCESS_MESSAGE_EN,
        'ru': STOP_SUCCESS_MESSAGE_RU,
    },
    ADMIN_HELP_MESSAGE: {
        'en': ADMIN_HELP_MESSAGE_EN,
        'ru': ADMIN_HELP_MESSAGE_RU,
    },
    HELP_SUCCESS_MESSAGE: {
        'en': HELP_SUCCESS_MESSAGE_EN,
        'ru': HELP_SUCCESS_MESSAGE_RU,
    },
    STATS_MESSAGE: {
        'en': STATS_MESSAGE_EN,
        'ru': STATS_MESSAGE_RU,
    },
    UNKNOWN_TEXT_MESSAGE: {
        'en': UNKNOWN_TEXT_MESSAGE_EN,
        'ru': UNKNOWN_TEXT_MESSAGE_RU,
    },
    UNKNOWN_COMMAND_MESSAGE: {
        'en': UNKNOWN_COMMAND_MESSAGE_EN,
        'ru': UNKNOWN_COMMAND_MESSAGE_RU,
    },
    MESSAGE_NO_NEW_MEETINGS: {
        'en': MESSAGE_NO_NEW_MEETINGS_EN,
        'ru': MESSAGE_NO_NEW_MEETINGS_RU,
    },
    MESSAGE_NO_MEETINGS_AT_ALL: {
        'en': MESSAGE_NO_MEETINGS_AT_ALL_EN,
        'ru': MESSAGE_NO_MEETINGS_AT_ALL_RU,
    },
    WHO_FULL_MESSAGE: {
        'en': WHO_FULL_MESSAGE_EN,
        'ru': WHO_FULL_MESSAGE_RU,
    },
    WHO_MESSAGE_RECORD: {
        'en': WHO_MESSAGE_RECORD_EN,
        'ru': WHO_MESSAGE_RECORD_RU,
    },
    MEETING_STATUS_TEXTS: {
        'en': str(MEETING_STATUS_TEXTS_EN),
        'ru': str(MEETING_STATUS_TEXTS_RU),
    },
    STATUS_UPDATE_MESSAGE: {
        'en': STATUS_UPDATE_MESSAGE_EN,
        'ru': STATUS_UPDATE_MESSAGE_RU,
    },
    HELP_UPDATE_STATUS_MESSAGE: {
        'en': HELP_UPDATE_STATUS_MESSAGE_EN,
        'ru': HELP_UPDATE_STATUS_MESSAGE_RU,
    },
    UPDATE_MEETING_ERROR_MESSAGE: {
        'en': UPDATE_MEETING_ERROR_MESSAGE_EN,
        'ru': UPDATE_MEETING_ERROR_MESSAGE_RU,
    },
    ADMIN_HELLO_MESSAGE: {
        'en': ADMIN_HELLO_MESSAGE_EN,
        'ru': ADMIN_HELLO_MESSAGE_RU,
    },
    LEADER_BOARD_MESSAGE: {
        'en': LEADER_BOARD_MESSAGE_EN,
        'ru': LEADER_BOARD_MESSAGE_RU,
    },
    ERROR_MESSAGE: {
        'en': ERROR_MESSAGE_EN,
        'ru': ERROR_MESSAGE_RU,
    },
    ALL_YOUR_MEETINGS: {
        'en': ALL_YOUR_MEETINGS_EN,
        'ru': ALL_YOUR_MEETINGS_RU,
    },
    ALL_WAITING_MEETINGS: {
        'en': ALL_WAITING_MEETINGS_EN,
        'ru': ALL_WAITING_MEETINGS_RU,
    },
    NAME_IS_UNKNOWN: {
        'en': NAME_IS_UNKNOWN_EN,
        'ru': NAME_IS_UNKNOWN_RU,
    },
    MEETING_ALREADY_DONE_LABEL: {
        'en': MEETING_ALREADY_DONE_LABEL_EN,
        'ru': MEETING_ALREADY_DONE_LABEL_RU,
    },
    TELEGRAM_MENTION: {
        'en': TELEGRAM_MENTION_EN,
        'ru': TELEGRAM_MENTION_RU,
    },
    MEETING_IS_DECLINED_LABEL: {
        'en': MEETING_IS_DECLINED_LABEL_EN,
        'ru': MEETING_IS_DECLINED_LABEL_RU,
    },
    INTEREST_ADDED: {
        'en': INTEREST_ADDED_EN,
        'ru': INTEREST_ADDED_RU,
    },
    INTEREST_REMOVED: {
        'en': INTEREST_REMOVED_EN,
        'ru': INTEREST_REMOVED_RU,
    },
    CHOOSE_YOUR_INTERESTS: {
        'en': CHOOSE_YOUR_INTERESTS_EN,
        'ru': CHOOSE_YOUR_INTERESTS_RU,
    },
    INTEREST_UNSELECTED_SIMBOL: {
        'en': INTEREST_UNSELECTED_SIMBOL_EN,
        'ru': INTEREST_UNSELECTED_SIMBOL_RU,
    },
    INTEREST_SELECTED_SIMBOL: {
        'en': INTEREST_SELECTED_SIMBOL_EN,
        'ru': INTEREST_SELECTED_SIMBOL_RU,
    },
    NO_JOINT_INTERESTS: {
        'en': NO_JOINT_INTERESTS_EN,
        'ru': NO_JOINT_INTERESTS_RU,
    },
    NEW_MEETING_MESSAGE: {
        'en': NEW_MEETING_MESSAGE_EN,
        'ru': NEW_MEETING_MESSAGE_RU,
    },
}
