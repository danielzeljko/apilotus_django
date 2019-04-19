from django.db import connection
from django.http import JsonResponse
from django.utils import timezone

from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from lotus_dashboard.serializers import *


class DashboardColumnViewSet(ModelViewSet):
    queryset = DashboardColumn.objects.all()
    serializer_class = DashboardColumnSerializer


class CapUpdateResultViewSet(ModelViewSet):
    queryset = CapUpdateResult.objects.all()
    serializer_class = CapUpdateResultSerializer

    def get_queryset(self):
        crm_id = self.request.query_params.get('crm_id', 0)
        from_date = self.request.query_params.get('from_date', '')
        to_date = self.request.query_params.get('to_date', '')
        if crm_id:
            from_date = timezone.datetime.strptime(from_date, "%m/%d/%Y").date()
            to_date = timezone.datetime.strptime(to_date, "%m/%d/%Y").date()
            self.queryset = CapUpdateResult.objects.filter(crm_id=crm_id, from_date=from_date, to_date=to_date)
            return self.queryset
        else:
            return self.queryset


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer


class AffiliateViewSet(ModelViewSet):
    queryset = Affiliate.objects.all()
    serializer_class = AffiliateSerializer


def dict_fetchall(cursor):
    # Returns all rows from a cursor as a dict
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


class CapUpdateList(APIView):
    """
        List all cap_update results.
    """

    def get(self, request, format=None):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                pag.*,
                pa.NAME AS affiliate_name,
                pa.afid,
                po.NAME AS offer_name,
                po.crm_id,
                po.crm_name,
                po.sales_goal,

                po.label_id
            FROM
                lotus_dashboard_affiliateoffer pag
                LEFT JOIN lotus_dashboard_affiliate pa ON pag.affiliate_id = pa.id
                LEFT JOIN (
            SELECT
                po.*,
                pca.crm_name,
                pca.sales_goal 
            FROM
                lotus_dashboard_offer po
                LEFT JOIN lotus_dashboard_crmaccount pca ON po.crm_id = pca.id
                ) po ON pag.offer_id = po.id 
            ORDER BY
                5,
                6
        ''')
        results = dict_fetchall(cursor)
        for result in results:
            result['step1'] = [a.campaign_id for a in Offer.objects.get(id=result['offer_id']).step1.all()]

        return JsonResponse(results, safe=False)


class AffiliationList(APIView):
    """
        List all affiliates with concerning values.
    """

    def get(self, request, format=None):
        affiliates = Affiliate.objects.all()
        offers = Offer.objects.all()
        affiliate_offers = AffiliateOffer.objects.all()

        results = []
        for affiliate in affiliates:
            sub_result = []
            for offer in offers:
                for affiliate_offer in affiliate_offers:
                    if affiliate.id == affiliate_offer.affiliate_id and offer.id == affiliate_offer.offer_id:
                        sub_result.append({
                            'affiliate_offer_id': affiliate_offer.id,
                            'affiliate_offer_goal': affiliate_offer.goal,
                            'offer_id': offer.id,
                            'offer_name': offer.name,
                            'offer_crm_id': offer.crm_id,
                            'offer_crm_name': offer.crm.crm_name + '(' + str(offer.crm.sales_goal) + ')',
                            'offer_label_id': offer.label_id,
                            'affiliate_offer_s1_payout': affiliate_offer.s1_payout,
                            'affiliate_offer_s2_payout': affiliate_offer.s2_payout,
                        })
            results.append({
                'affiliate_id': affiliate.id,
                'affiliate_name': affiliate.name,
                'affiliate_afid': affiliate.afid,
                'affiliate_code': affiliate.code,
                'affiliate_bot': affiliate.bot,
                'sub_result': sub_result,
            })

        return JsonResponse(results, safe=False)
