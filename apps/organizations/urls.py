from rest_framework_nested import routers
from .views import OrganizationViewSet, OrgMemberViewSet


router = routers.DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")

org_member_router = routers.NestedDefaultRouter(router, "organizations", lookup="organization")
org_member_router.register("members", OrgMemberViewSet, basename="organization-members")


urlpatterns = [
    *router.urls,
]