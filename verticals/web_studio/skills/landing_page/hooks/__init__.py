"""Hooks скилла landing_page: post_execute чистит markdown-обёртки и debug-следы."""
import re


def pre_execute(ctx):
    return ctx


def post_execute(ctx, artifact):
    a = artifact.strip()
    a = re.sub(r"^```[a-zA-Z]*\n?", "", a)
    a = re.sub(r"```$", "", a).strip()
    a = re.sub(r"<script[^>]*>\s*console\.log[^<]*</script>", "", a, flags=re.I)
    return a
