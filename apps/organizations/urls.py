from rest_framework_nested import routers
from .views import OrganizationViewSet, OrgMemberViewSet
from apps.repositories.views import OrgRepositoryViewSet


router = routers.DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")

org_router = routers.NestedDefaultRouter(router, "organizations", lookup="org")
org_router.register("members", OrgMemberViewSet, basename="organization-members")
org_router.register("repositories", OrgRepositoryViewSet, basename="organization-repositories")


urlpatterns = [
    *router.urls,
    *org_router.urls,
]