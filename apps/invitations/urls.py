from rest_framework_nested import routers
from .views import InvitationViewSet

router = routers.DefaultRouter()
router.register(r"invitations", InvitationViewSet, basename="invitation")

urlpatterns = [
    *router.urls,
]