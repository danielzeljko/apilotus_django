from lotus_alert.serializers import *
from rest_framework.viewsets import ModelViewSet


class AlertTypeViewSet(ModelViewSet):
    queryset = AlertType.objects.all()
    serializer_class = AlertTypeSerializer


class AlertStatusViewSet(ModelViewSet):
    queryset = AlertStatus.objects.all()
    serializer_class = AlertStatusSerializer

    def get_queryset(self):
        self.queryset = AlertStatus.objects.filter(status=False)
        return self.queryset
