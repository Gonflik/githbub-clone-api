from rest_framework_nested import routers
from .views import OrganizationViewSet


router = routers.DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")


urlpatterns = [
    *router.urls,
]