from rest_framework.routers import DefaultRouter
from jira_sync.views import JiraConnectionViewSet, JiraProjectViewSet, JiraTaskViewSet, JiraSubtaskViewSet

router = DefaultRouter()
router.register(r"jira/connections", JiraConnectionViewSet, basename="jira-connection")
router.register(r"jira/projects", JiraProjectViewSet, basename="jira-project")
#router.register(r"jira/issues", JiraIssueViewSet, basename="jira-issue")
router.register(r"jira/tasks", JiraTaskViewSet, basename="jira-task")
router.register(r"jira/subtasks", JiraSubtaskViewSet, basename="jira-subtask")


urlpatterns = router.urls
