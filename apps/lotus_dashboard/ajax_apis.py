from django.http import HttpResponse
from lotus_dashboard.models import *


def ajax_add_affiliate(request):
    name = request.GET['name']
    afid = request.GET['afid']
    offer_ids = request.GET['offer_ids'].split(',')
    offer_goals = request.GET['offer_goals'].split(',')
    s1_payouts = request.GET['s1_payouts'].split(',')
    s2_ids = request.GET['s2_ids']
    s2_payouts = request.GET['s2_payouts']

    affiliate = Affiliate(name=name, afid=afid)
    affiliate.save()

    for idx, offer_id in enumerate(offer_ids):
        affiliate_offer = AffiliateOffer(
            affiliate=affiliate,
            offer_id=int(offer_id),
            goal=int(offer_goals[idx]),
            s1_payout=int(s1_payouts[idx]),
            s2_payout=0,
        )
        affiliate_offer.save()

    return HttpResponse('OK')


def ajax_edit_affiliate(request):
    affiliate_id = int(request.GET['affiliate_id'])
    name = request.GET['name']
    afid = request.GET['afid']
    offer_ids = request.GET['offer_ids'].split(',')
    offer_goals = request.GET['offer_goals'].split(',')
    s1_payouts = request.GET['s1_payouts'].split(',')
    s2_ids = request.GET['s2_ids']
    s2_payouts = request.GET['s2_payouts']

    affiliate = Affiliate.objects.get(id=affiliate_id)
    affiliate.name = name
    affiliate.afid = afid
    affiliate.save()

    AffiliateOffer.objects.filter(affiliate=affiliate).delete()
    for idx, offer_id in enumerate(offer_ids):
        affiliate_offer = AffiliateOffer(
            affiliate=affiliate,
            offer_id=int(offer_id),
            goal=int(offer_goals[idx]),
            s1_payout=int(s1_payouts[idx]),
            s2_payout=0,
        )
        affiliate_offer.save()

    return HttpResponse('OK')


def ajax_delete_affiliate(request):
    affiliate_id = int(request.GET['affiliate_id'])
    affiliate = Affiliate.objects.get(id=affiliate_id)
    AffiliateOffer.objects.filter(affiliate=affiliate).delete()
    affiliate.delete()

    return HttpResponse('OK')


def ajax_affiliate_special_code(request):
    affiliate_id = int(request.GET['affiliate_id'])
    special_code = request.GET['special_code']

    affiliate = Affiliate.objects.get(id=affiliate_id)
    affiliate.code = special_code
    affiliate.save()

    return HttpResponse('OK')
