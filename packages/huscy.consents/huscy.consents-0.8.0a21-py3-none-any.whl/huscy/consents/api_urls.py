from rest_framework.routers import DefaultRouter

from .viewsets import ConsentCategoryViewSet, ConsentViewSet


router = DefaultRouter()
router.register('consentcategories', ConsentCategoryViewSet, basename='consentcategory')
router.register('consents', ConsentViewSet, basename='consent')


urlpatterns = router.urls
