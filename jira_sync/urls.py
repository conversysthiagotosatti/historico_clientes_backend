from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import JiraConnectionViewSet, JiraIssueViewSet
from .views_sync import JiraSyncProjectsView, JiraSyncIssuesView
from .views import JiraProjectsView

router = DefaultRouter()
router.register(r"jira/connections", JiraConnectionViewSet, basename="jira-connections")
router.register(r"jira/issues", JiraIssueViewSet, basename="jira-issues")

urlpatterns = [
    # endpoints de sync
    path("jira/sync/projects/", JiraSyncProjectsView.as_view(), name="jira-sync-projects"),
    path("jira/sync/issues/", JiraSyncIssuesView.as_view(), name="jira-sync-issues"),
    path("jira/projects/", JiraProjectsView.as_view(), name="jira-projects")
]

urlpatterns += router.urls
