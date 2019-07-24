from django.utils import timezone

from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters
from django_telegrambot.apps import DjangoTelegramBot

from lotus_dashboard.models import *
from lotus_auth.models import LotusUser

import logging
logger = logging.getLogger(__name__)


def send_message(bot, update, msg):
    kb = [
        [KeyboardButton('/dashboard_takerate'), KeyboardButton('/dashboard_tablet'), KeyboardButton('/dashboard_goal')],
        [KeyboardButton('/alert_step1_rebill_report'), KeyboardButton('/alert_step2_rebill_report')],
        [KeyboardButton('/alert_initial_approval_day'), KeyboardButton('/alert_initial_approval_week')],
        [KeyboardButton('/alert_decline_percentage_day'), KeyboardButton('/alert_decline_percentage_week')],
        [KeyboardButton('/alert_100step1_sales'), KeyboardButton('/alert_30step1_sales'),
         KeyboardButton('/alert_take_rate'), KeyboardButton('/alert_tablet_take_rate')],
        [KeyboardButton('/alert_step1_crm_capped'), KeyboardButton('/alert_password_validdays')],
    ]
    kb_markup = ReplyKeyboardMarkup(kb)

    bot.sendMessage(update.message.chat_id, text=msg, reply_markup=kb_markup)


def send_register_message(bot, update):
    msg = 'Hi, How are you?\r\nUnfortunately, this chat id(' + \
          str(update.message.chat_id) + \
          ') is not registered on API Lotus site.\r\nPlease register this one on it.'
    bot.sendMessage(update.message.chat_id, text=msg)


def exist_chat_id(bot, update):
    if LotusUser.objects.filter(bot=str(update.message.chat_id)).exists():
        return True
    send_register_message(bot, update)
    return False


def check_this_chat_info(bot, update):
    if not exist_chat_id(bot, update):
        return
    msg = 'This Chat Information\r\n\r\n'
    msg += 'Chat ID : ' + str(update.message.chat_id) + '\r\n'
    send_message(bot, update, msg)


def dashboard_takerate(bot, update):
    if not exist_chat_id(bot, update):
        return

    active_crms = CrmAccount.objects.active_crm_accounts()
    if not active_crms:
        msg = "There are no active CRMs, please try to enable in account page."
    else:
        to_date = timezone.datetime.now().date()
        from_date = to_date + timezone.timedelta(-to_date.weekday())
        crm_results = CrmResult.objects.filter(from_date=from_date, to_date=to_date, label=None).order_by('crm')
        if not crm_results:
            msg = "There are no result, please try again after some minutes later."
        else:
            msg = 'CRM Name\t[TAKE RATE %]\r\n\r\n'
            msg += 'Timestamp : {}\r\n\r\n'.format(str(crm_results[0].updated_at)[:-13])
            for idx, result in enumerate(crm_results):
                msg += '{id}. {crm_name}\t[{take_rate}%]\r\n'.format(
                    id=idx + 1,
                    crm_name=result.crm.crm_name,
                    take_rate='%.2f' % ((result.tablet_step2 + result.step2_nonpp) * 100 / (result.tablet_step1 + result.step1_nonpp)) if result.tablet_step1 + result.step1_nonpp > 0 else 0,
                )

    msg += '\r\n\r\nRelated commands:\r\n'
    msg += '/dashboard_tablet\r\n'
    msg += '/dashboard_goal\r\n'

    send_message(bot, update, msg)


def dashboard_tablet(bot, update):
    if not exist_chat_id(bot, update):
        return

    active_crms = CrmAccount.objects.active_crm_accounts()
    if not active_crms:
        msg = "There are no active CRMs, please try to enable in account page."
    else:
        to_date = timezone.datetime.now().date()
        from_date = to_date + timezone.timedelta(-to_date.weekday())
        crm_results = CrmResult.objects.filter(from_date=from_date, to_date=to_date, label=None).order_by('crm')
        if not crm_results:
            msg = "There are no result, please try again after some minutes later."
        else:
            msg = 'CRM Name\t[TABLET %]\r\n\r\n'
            msg += 'Timestamp : {}\r\n\r\n'.format(str(crm_results[0].updated_at)[:-13])
            for idx, result in enumerate(crm_results):
                msg += '{id}. {crm_name}\t[{tablet}%]\r\n'.format(
                    id=idx + 1,
                    crm_name=result.crm.crm_name,
                    tablet='%.2f' % (result.tablet_step1 * 100 / (result.tablet_step1 + result.step2_nonpp)) if result.tablet_step1 + result.step2_nonpp > 0 else 0,
                )

    msg += '\r\n\r\nRelated commands:\r\n'
    msg += '/dashboard_takerate\r\n'
    msg += '/dashboard_goal\r\n'

    send_message(bot, update, msg)


def dashboard_goal(bot, update):
    if not exist_chat_id(bot, update):
        return

    active_crms = CrmAccount.objects.active_crm_accounts()
    if not active_crms:
        msg = "There are no active CRMs, please try to enable in account page."
    else:
        to_date = timezone.datetime.now().date()
        from_date = to_date + timezone.timedelta(-to_date.weekday())
        crm_results = CrmResult.objects.filter(from_date=from_date, to_date=to_date, label=None).order_by('crm')
        if not crm_results:
            msg = "There are no result, please try again after some minutes later."
        else:
            msg = 'CRM Name\t[STEP1 / GOAL]\r\n\r\n'
            msg += 'Timestamp : {}\r\n\r\n'.format(str(crm_results[0].updated_at)[:-13])
            for idx, result in enumerate(crm_results):
                msg += '{id}. {crm_name}\t[{step1} / {goal}] ({percent}%)\r\n'.format(
                    id=idx + 1,
                    crm_name=result.crm.crm_name,
                    step1=result.step1,
                    goal=result.crm.sales_goal,
                    percent='%.2f' % (result.step1 * 100 / result.crm.sales_goal) if result.crm.sales_goal else 0,
                )

    msg += '\r\n\r\nRelated commands:\r\n'
    msg += '/dashboard_takerate\r\n'
    msg += '/dashboard_tablet\r\n'

    send_message(bot, update, msg)


def alert_step1_rebill_report(bot, update):
    if not exist_chat_id(bot, update):
        return

    active_crms = CrmAccount.objects.active_crm_accounts()
    if not active_crms:
        msg = "There are no active CRMs, please try to enable in account page."
    else:
        to_date = timezone.datetime.now().date()
        from_date = to_date + timezone.timedelta(-to_date.weekday())
        crm_results = CrmResult.objects.filter(from_date=from_date, to_date=to_date, label=None).order_by('crm')
        if not crm_results:
            msg = "There are no result, please try again after some minutes later."
        else:
            msg = 'CRM Name\t[STEP1 / GOAL]\r\n\r\n'
            msg += 'Timestamp : {}\r\n\r\n'.format(str(crm_results[0].updated_at)[:-13])
            for idx, result in enumerate(crm_results):
                msg += '{id}. {crm_name}\t[{step1} / {goal}] ({percent}%)\r\n'.format(
                    id=idx + 1,
                    crm_name=result.crm.crm_name,
                    step1=result.step1,
                    goal=result.crm.sales_goal,
                    percent='%.2f' % (result.step1 * 100 / result.crm.sales_goal) if result.crm.sales_goal else 0,
                )

    msg += '\r\n\r\nRelated commands:\r\n'
    msg += '/dashboard_takerate\r\n'
    msg += '/dashboard_tablet\r\n'

    send_message(bot, update, msg)


def echo(bot, update):
    if not exist_chat_id(bot, update):
        return
    msg = 'Hi, How are you?\r\nPlease select the command for API Lotus.'
    send_message(bot, update, msg)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.DJANGO_TELEGRAMBOT['BOTS'])
    dp = DjangoTelegramBot.dispatcher
    # To get Dispatcher related to a specific bot
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_token')     #get by bot token
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_username')  #get by bot username

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("check_this_chat_info", check_this_chat_info))

    dp.add_handler(CommandHandler("dashboard_takerate", dashboard_takerate))
    dp.add_handler(CommandHandler("dashboard_tablet", dashboard_tablet))
    dp.add_handler(CommandHandler("dashboard_goal", dashboard_goal))

    dp.add_handler(CommandHandler("alert_step1_rebill_report", alert_step1_rebill_report))
    dp.add_handler(CommandHandler("alert_step2_rebill_report", dashboard_goal))

    dp.add_handler(CommandHandler("alert_initial_approval_day", dashboard_goal))
    dp.add_handler(CommandHandler("alert_initial_approval_week", dashboard_goal))

    dp.add_handler(CommandHandler("alert_decline_percentage_day", dashboard_goal))
    dp.add_handler(CommandHandler("alert_decline_percentage_week", dashboard_goal))

    dp.add_handler(CommandHandler("alert_100step1_sales", dashboard_goal))
    dp.add_handler(CommandHandler("alert_30step1_sales", dashboard_goal))
    dp.add_handler(CommandHandler("alert_take_rate", dashboard_goal))
    dp.add_handler(CommandHandler("alert_tablet_take_rate", dashboard_goal))

    dp.add_handler(CommandHandler("alert_step1_crm_capped", dashboard_goal))
    dp.add_handler(CommandHandler("alert_password_validdays", dashboard_goal))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler((Filters.text | Filters.command), echo))

    # log all errors
    dp.add_error_handler(error)
