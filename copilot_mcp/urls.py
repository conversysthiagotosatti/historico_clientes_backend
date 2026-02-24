from django.urls import path
from .views import MCPExecuteView, CopilotChatView

urlpatterns = [
    path("execute/", MCPExecuteView.as_view(), name="copilot-mcp-execute"),
    path("chat/", CopilotChatView.as_view(), name="copilot-chat"),
]