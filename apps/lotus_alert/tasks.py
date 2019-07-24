from celery.schedules import crontab
from celery.task import periodic_task

from lotus_alert.models import *
from lotus_auth.models import *
from lotus_dashboard.models import *

from utils.telegram import TelegramBot


# * Step1 / CRM Caps
@periodic_task(
    run_every=(crontab(minute=0, hour='*/1')),
    name="apps.lotus_alert.tasks.task_step1_sales",
    ignore_result=True,
)
def task_step1_sales():
    alert_type = AlertType.objects.get(alert_name="Step1 / CRM Caps")
    current_hour = timezone.datetime.now().hour
    if str(current_hour) not in alert_type.alert_hour.split(','):
        return
    # today
    to_date = timezone.datetime.now().date()
    # week_start
    from_date = to_date + timezone.timedelta(-to_date.weekday())

    crm_results = CrmResult.objects.filter(from_date=from_date, to_date=to_date, goal=0).order_by('crm_id')

    if crm_results:
        text = '*CRM Goal Progress*\r\n\r\n'
        for idx, crm_result in enumerate(crm_results):
            text += '{id}. {crm_name} [{step1} / {goal}] [{percent}%]'.format(
                id=idx + 1, crm_name=crm_result.crm.crm_name, step1=crm_result.step1, goal=crm_result.crm.sales_goal,
                percent=int((crm_result.step1 / crm_result.crm.sales_goal) * 100) if crm_result.crm.sales_goal else 0,
            ) + '\r\n'

        telegram_bot = TelegramBot()
        telegram_bot.send_message(text)


# * description
# * Get the data for Prospect report and then send the alerts of some alerts by condition.
# * -    Step1 CRM Capped
# * -    100, 50, 10 Step1 Sales Away From Cap
# * -    10, 25, 50, 75, 100, 125, 150, 200, 250 Step1 Sales Over Cap
@periodic_task(
    run_every=(crontab(minute=0, hour='*/1')),
    name="apps.lotus_alert.tasks.task_prospect_report",
    ignore_result=True,
)
def task_prospect_report():
    # today
    to_date = timezone.datetime.now().date()
    # week_start
    from_date = to_date + timezone.timedelta(-to_date.weekday())

    capped_result = []
    away_result = []
    over_result = []

    crm_list = CrmAccount.objects.active_crm_accounts()
    for crm in crm_list:
        crm_result = CrmResult.objects.filter(crm=crm, from_date=from_date, to_date=to_date, goal=0).first()
        if not crm_result:
            continue

        sales_step1 = crm_result.step1

        alert_type = AlertType.objects.get(alert_name='Step 1 CRM Capped')
        if sales_step1 == crm_result.crm.sales_goal:
            capped_result.append(crm_result)

        alert_type = AlertType.objects.get(alert_name='100 Step1 Sales Away From Cap')
        current_hour = timezone.datetime.now().hour
        if str(current_hour) in alert_type.alert_hour.split(','):
            if sales_step1 < crm_result.crm.sales_goal and (sales_step1 >= crm_result.crm.sales_goal - 100 or
                                                            sales_step1 >= crm_result.crm.sales_goal - 50 or
                                                            sales_step1 >= crm_result.crm.sales_goal - 10):
                away_result.append(crm_result)

        alert_type = AlertType.objects.get(alert_name='10 Step1 Sales Over Cap')
        current_hour = timezone.datetime.now().hour
        if str(current_hour) in alert_type.alert_hour.split(','):
            if sales_step1 >= crm_result.crm.sales_goal + 10 or \
                    sales_step1 >= crm_result.crm.sales_goal + 25 or \
                    sales_step1 >= crm_result.crm.sales_goal + 50 or \
                    sales_step1 >= crm_result.crm.sales_goal + 75 or \
                    sales_step1 >= crm_result.crm.sales_goal + 100 or \
                    sales_step1 >= crm_result.crm.sales_goal + 125 or \
                    sales_step1 >= crm_result.crm.sales_goal + 150 or \
                    sales_step1 >= crm_result.crm.sales_goal + 200 or \
                    sales_step1 >= crm_result.crm.sales_goal + 250:
                over_result.append(crm_result)

    telegram_bot = TelegramBot()

    if capped_result:
        text = '*OVER CAP ALERT*\r\nStep1 CRM Capped\r\n\r\n'
        text += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        text += 'Timestamp : {}\r\n\r\n'.format(str(timezone.datetime.now())[:-7])
        for result in capped_result:
            text += '[{crm_name}] {step1} (= {goal})'.format(
                crm_name=result.crm.crm_name, step1=result.step1, goal=result.crm.sales_goal,
            ) + '\r\n'

        telegram_bot.send_message(text)

    if away_result:
        text = '*Step1 Sales Away From Cap Alert*\r\n\r\n'
        text += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        text += 'Timestamp : {}\r\n\r\n'.format(str(timezone.datetime.now())[:-7])
        for result in away_result:
            text += '[{crm_name}] {step1} / {goal}({away} Away)'.format(
                crm_name=result.crm.crm_name, step1=result.step1, goal=result.crm.sales_goal,
                away=result.crm.sales_goal - result.step1,
            ) + '\r\n'

        telegram_bot.send_message(text)

    if over_result:
        text = '*Step1 Sales Over Cap Alert*\r\n\r\n'
        text += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        text += 'Timestamp : {}\r\n\r\n'.format(str(timezone.datetime.now())[:-7])
        for result in over_result:
            text += '[{crm_name}] {step1} / {goal}({over} Over)'.format(
                crm_name=result.crm.crm_name, step1=result.step1, goal=result.crm.sales_goal,
                over=result.step1 - result.crm.sales_goal,
            ) + '\r\n'

        telegram_bot.send_message(text)


@periodic_task(
    run_every=(crontab(minute=0, hour='*/1')),
    name="apps.lotus_alert.tasks.task_cap_update_report",
    ignore_result=True,
)
def task_cap_update_report():
    # today
    to_date = timezone.datetime.now().date()
    # week_start
    from_date = to_date + timezone.timedelta(-to_date.weekday())

    capped_result = []
    away_result = []
    over_result = []

    crm_list = CrmAccount.objects.active_crm_accounts()
    affiliate_offers = AffiliateOffer.objects.all()
    for crm in crm_list:
        result_by_crm = CapUpdateResult.objects.filter(crm=crm, from_date=from_date, to_date=to_date).first()
        if not result_by_crm:
            continue

        result = eval(result_by_crm.result)
        updated_at = result_by_crm.updated_at

        for affiliate_offer in affiliate_offers:
            if crm.id == affiliate_offer.offer.crm_id:
                count = 0
                afids = affiliate_offer.affiliate.afid.split(',')
                campaign_ids = affiliate_offer.offer.step1.all()
                for campaign_prospects in result:
                    for campaign_id in campaign_ids:
                        if campaign_prospects[0] == campaign_id.campaign_id:
                            for campaign_prospect in campaign_prospects[1]:
                                for afid in afids:
                                    if campaign_prospect['id'] == afid.split('(')[0]:
                                        count += campaign_prospect['initial_customers']

                if count > 0:
                    print(affiliate_offer)
                goal = affiliate_offer.goal

                alert_type = AlertType.objects.get(alert_name='Step 1 CRM Capped')
                if count == goal:
                    capped_result.append([affiliate_offer, count, updated_at])

                alert_type = AlertType.objects.get(alert_name='100 Step1 Sales Away From Cap')
                current_hour = timezone.datetime.now().hour
                if str(current_hour) in alert_type.alert_hour.split(','):
                    if count < goal and (count >= goal - 99 or count >= goal - 50 or count >= goal - 10):
                        away_result.append([affiliate_offer, count, updated_at])

                alert_type = AlertType.objects.get(alert_name='10 Step1 Sales Over Cap')
                current_hour = timezone.datetime.now().hour
                if str(current_hour) in alert_type.alert_hour.split(','):
                    if count >= goal + 10 or \
                            count >= goal + 25 or \
                            count >= goal + 50 or \
                            count >= goal + 75 or \
                            count >= goal + 100 or \
                            count >= goal + 125 or \
                            count >= goal + 150 or \
                            count >= goal + 200 or \
                            count >= goal + 250:
                        over_result.append([affiliate_offer, count, updated_at])

    telegram_bot = TelegramBot()

    if capped_result:
        text = '*Cap Update Level Capped Alert\r\n\r\n'
        text += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        text += 'Timestamp : {}\r\n\r\n'.format(str(capped_result[0][2])[:-10])
        for result in capped_result:
            text += '{affiliate_name} is Capped [{offer_name}] [{count} / {goal}]'.format(
                affiliate_name=result[0].affiliate.name,
                offer_name=result[0].offer.name,
                count=result[1], goal=result[0].goal,
            ) + '\r\n'

        telegram_bot.send_message(text)

    if away_result:
        text = '*Cap Update Level Away Alert*\r\n\r\n'
        text += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        text += 'Timestamp : {}\r\n\r\n'.format(str(away_result[0][2])[:-10])
        for result in away_result:
            text += '{affiliate_name} is {difference} Away From Capping [{offer_name}] [{count} / {goal}]'.format(
                affiliate_name=result[0].affiliate.name,
                difference=result[0].goal - result[1],
                offer_name=result[0].offer.name,
                count=result[1], goal=result[0].goal,
            ) + '\r\n'

        telegram_bot.send_message(text)

    if over_result:
        text = '*Cap Update Level Over Alert*\r\n\r\n'
        text += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        text += 'Timestamp : {}\r\n\r\n'.format(str(over_result[0][2])[:-10])
        for result in over_result:
            text += '{affiliate_name} is {difference} Sales Over Cap [{offer_name}] [{count} / {goal}]'.format(
                affiliate_name=result[0].affiliate.name,
                difference=result[1] - result[0].goal,
                offer_name=result[0].offer.name,
                count=result[1], goal=result[0].goal,
            ) + '\r\n'

        telegram_bot.send_message(text)

    if capped_result:
        title = '*Cap Update Level Capped Alert\r\n\r\n'
        title += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        for result in capped_result:
            if not result[0].affiliate.bot:
                continue
            timestamp = 'Timestamp : {}\r\n\r\n'.format(str(result[2])[:-10])
            text = '{affiliate_name} is Capped [{offer_name}] [{count} / {goal}]'.format(
                affiliate_name=result[0].affiliate.name,
                offer_name=result[0].offer.name,
                count=result[1], goal=result[0].goal,
            ) + '\r\n'
            telegram_bot.send_message_by_id(title + timestamp + text, result[0].affiliate.bot)

    if away_result:
        title = '*Cap Update Level Away Alert*\r\n\r\n'
        title += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        for result in away_result:
            if not result[0].affiliate.bot:
                continue
            timestamp = 'Timestamp : {}\r\n\r\n'.format(str(result[2])[:-10])
            text = '{affiliate_name} is {difference} Away From Capping [{offer_name}] [{count} / {goal}]'.format(
                affiliate_name=result[0].affiliate.name,
                difference=result[0].goal - result[1],
                offer_name=result[0].offer.name,
                count=result[1], goal=result[0].goal,
            ) + '\r\n'
            telegram_bot.send_message_by_id(title + timestamp + text, result[0].affiliate.bot)

    if over_result:
        title = '*Cap Update Level Over Alert*\r\n\r\n'
        title += 'Date Range : {} ~ {}\r\n\r\n'.format(from_date, to_date)
        for result in over_result:
            if not result[0].affiliate.bot:
                continue
            timestamp = 'Timestamp : {}\r\n\r\n'.format(str(result[2])[:-10])
            text = '{affiliate_name} is {difference} Sales Over Cap [{offer_name}] [{count} / {goal}]'.format(
                affiliate_name=result[0].affiliate.name,
                difference=result[1] - result[0].goal,
                offer_name=result[0].offer.name,
                count=result[1], goal=result[0].goal,
            ) + '\r\n'
            telegram_bot.send_message_by_id(title + timestamp + text, result[0].affiliate.bot)
