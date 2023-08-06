from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

from .models import Consent, ConsentCategory
from .serializer import ConsentSerializer, ConsentCategorySerializer


class ConsentCategoryViewSet(ModelViewSet):
    permission_classes = DjangoModelPermissions,
    queryset = ConsentCategory.objects.all()
    serializer_class = ConsentCategorySerializer


class ConsentViewSet(ModelViewSet):
    permission_classes = DjangoModelPermissions,
    queryset = Consent.objects.all()
    serializer_class = ConsentSerializer
