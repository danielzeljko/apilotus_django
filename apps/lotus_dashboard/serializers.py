from rest_framework import serializers
from lotus_dashboard.models import *


class DashboardColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardColumn
        fields = ('id', 'site', 'columns')


class CapUpdateResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapUpdateResult
        fields = ('id', 'from_date', 'to_date', 'crm', 'result', 'updated_at')


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'crm', 'name', 'label', 'type', 's1_payout', 's2_payout', 'step1')


class AffiliateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliate
        fields = ('id', 'name', 'afid', 'code', 'bot')
