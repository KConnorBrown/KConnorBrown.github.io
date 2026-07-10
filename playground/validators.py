import re

FORBIDDEN_KEYWORDS = re.compile(
    r"\b("
    r"insert|update|delete|drop|alter|create|truncate|grant|revoke|"
    r"copy|execute|call|merge|replace|into|set|begin|commit|rollback|"
    r"savepoint|lock|vacuum|analyze|refresh|comment|security|"
    r"do|notify|listen|unlisten|discard|reindex|cluster|"
    r"load|import|export|attach|detach|pragma"
    r")\b",
    re.IGNORECASE,
)


def validate_select_only(sql: str) -> str:
    cleaned = _strip_sql_comments(sql).strip()
    if not cleaned:
        raise ValueError("Query cannot be empty.")

    if ";" in cleaned.rstrip(";"):
        raise ValueError("Only a single SQL statement is allowed.")

    cleaned = cleaned.rstrip(";").strip()
    if not re.match(r"^select\b", cleaned, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed in the playground.")

    if FORBIDDEN_KEYWORDS.search(cleaned):
        raise ValueError("Only SELECT queries are allowed in the playground.")

    return cleaned


def _strip_sql_comments(sql: str) -> str:
    without_block = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return re.sub(r"--.*?$", " ", without_block, flags=re.MULTILINE)
