from __future__ import annotations
from typing import Any
from django.utils import timezone
from contratos.models import CopilotRun, CopilotActionLog, Contrato

def start_run(*, contrato: Contrato, user, user_message: str, mode: str, model: str = None, prompt_version: str = None):
    return CopilotRun.objects.create(
        contrato=contrato,
        cliente=contrato.cliente,
        usuario=user,
        mode=mode,
        status=CopilotRun.Status.OK,
        user_message=user_message,
        model=model,
        prompt_version=prompt_version,
    )

def log_action(*, run: CopilotRun, action_name: str, action_input: dict[str, Any], ok: bool,
               action_output: dict[str, Any] | None = None, error: str | None = None):
    CopilotActionLog.objects.create(
        run=run,
        action_name=action_name,
        action_input=action_input,
        action_output=action_output,
        ok=ok,
        error=error,
    )

def finish_run_ok(run: CopilotRun, *, answer: str | None = None, latency_ms: int | None = None, token_usage: dict | None = None):
    run.status = CopilotRun.Status.OK
    run.answer = answer
    run.latency_ms = latency_ms
    run.token_usage = token_usage
    run.save(update_fields=["status", "answer", "latency_ms", "token_usage"])

def finish_run_error(run: CopilotRun, *, error: str):
    run.status = CopilotRun.Status.ERROR
    run.error = error
    run.save(update_fields=["status", "error"])