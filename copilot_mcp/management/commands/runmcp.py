from django.core.management.base import BaseCommand
import django

class Command(BaseCommand):
    help = "Run MCP server for contratos copilot"

    def handle(self, *args, **options):
        django.setup()

        from copilot_mcp.server import mcp

        # transporte depende do host MCP que você vai usar.
        # Em dev, geralmente stdio é o caminho mais comum.
        mcp.run()