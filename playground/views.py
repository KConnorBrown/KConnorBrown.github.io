import json
import time
from decimal import Decimal
from datetime import date, datetime

from django.conf import settings
from django.db import connections
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .tutorial_examples import SCHEMA_REFERENCE, TUTORIAL_EXAMPLES
from .validators import validate_select_only


def _serialize(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def sql_playground(request):
    if request.method == "GET":
        return render(
            request,
            "playground/sql_playground.html",
            {
                "title": "SQL Playground",
                "examples": TUTORIAL_EXAMPLES,
                "schema": SCHEMA_REFERENCE,
            },
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
        sql = validate_select_only(payload.get("query", ""))
    except (json.JSONDecodeError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    row_limit = settings.PLAYGROUND_ROW_LIMIT
    timeout_ms = settings.PLAYGROUND_STATEMENT_TIMEOUT_MS
    wrapped_sql = f"SELECT * FROM ({sql}) AS playground_query LIMIT {row_limit}"

    started = time.perf_counter()
    try:
        with connections["playground"].cursor() as cursor:
            cursor.execute(f"SET statement_timeout = {timeout_ms}")
            cursor.execute(wrapped_sql)
            columns = [col[0] for col in cursor.description]
            rows = [
                [_serialize(value) for value in row]
                for row in cursor.fetchall()
            ]
    except Exception as exc:
        return JsonResponse({"error": str(exc).split("\n")[0]}, status=400)

    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return JsonResponse(
        {
            "columns": columns,
            "rows": rows,
            "elapsed_ms": elapsed_ms,
            "row_limit": row_limit,
        }
    )
