from django.urls import path
from .views import MCPExecuteView

urlpatterns = [
    path("execute/", MCPExecuteView.as_view(), name="copilot-mcp-execute"),
]