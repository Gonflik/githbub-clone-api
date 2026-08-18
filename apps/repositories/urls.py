from rest_framework_nested import routers
from apps.issues.views import IssueViewSet, CommentViewSet
from .views import RepositoryViewSet, CollaboratorViewSet


router = routers.DefaultRouter()
router.register(r"repositories", RepositoryViewSet, basename="repository")


repo_router = routers.NestedDefaultRouter(router, "repositories", lookup="repository")
repo_router.register("issues", IssueViewSet, basename="repository-issues")
repo_router.register("collaborators", CollaboratorViewSet, basename="repository-collaborators")

issue_router = routers.NestedDefaultRouter(repo_router, "issues", lookup="issue")
issue_router.register("comments", CommentViewSet, basename="issue-comments")



urlpatterns = [
    *router.urls,
    *repo_router.urls,
    *issue_router.urls,
]