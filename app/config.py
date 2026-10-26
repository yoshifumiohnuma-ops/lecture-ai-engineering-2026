"""講座全体で共通の設定。

APIキーやモデル名はコードに書かず、環境変数から読み込む。
"""

import os

# APIプロバイダー。キーが設定されていれば Groq を既定にする。
# AIE_PROVIDER=gemini/claude/groq で切り替えられる。
if os.getenv("AIE_PROVIDER"):
    DEFAULT_PROVIDER = os.getenv("AIE_PROVIDER").lower()
elif os.getenv("GROQ_API_KEY"):
    DEFAULT_PROVIDER = "groq"
elif os.getenv("CLAUDE_API_KEY"):
    DEFAULT_PROVIDER = "claude"
else:
    DEFAULT_PROVIDER = "gemini"
PROVIDER = os.getenv("AIE_PROVIDER", DEFAULT_PROVIDER).lower()

DEFAULT_MODELS = {
    "groq": "openai/gpt-oss-20b",
    "claude": "claude-sonnet-4-5",
    "gemini": "gemini-3.5-flash-lite",
}
MODEL = os.getenv("AIE_MODEL", DEFAULT_MODELS.get(PROVIDER, DEFAULT_MODELS["gemini"]))


def api_error_message(status: int, detail: str = "") -> str:
    """HTTPステータスコードを、受講生向けの日本語の説明にする（ask.py と agent.py で共用）。"""
    if status == 429:
        return "レート制限に達しました。1分ほど待ってから再実行してください。"
    if status == 503:
        return "モデルが混み合っています（503）。少し待ってから再実行してください。"
    if status in (400, 401, 403, 404):
        return f"APIキーかモデル名に問題があります（{status}）: {detail}"
    return f"APIエラー（{status}）: {detail}"


def get_api_key() -> str:
    """環境変数 GEMINI_API_KEY を返す。未設定なら手順を表示して終了する。"""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise SystemExit(
            "環境変数 GEMINI_API_KEY が見つかりません。\n"
            "1. GitHub の Settings → Codespaces → Secrets に GEMINI_API_KEY を登録し、\n"
            "   使う repository に自分の fork を選んでください。\n"
            "2. Codespaces を起動したあとに登録した場合は、Codespaces を再起動してください。\n"
            "   （左下の「Codespaces」→「Stop Current Codespace」→ 再度開く）"
        )
    return key


def get_groq_api_key() -> str:
    """環境変数 GROQ_API_KEY を返す。未設定なら手順を表示して終了する。"""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise SystemExit(
            "環境変数 GROQ_API_KEY が見つかりません。\n"
            "GitHub の Settings → Codespaces → Secrets に GROQ_API_KEY を登録し、\n"
            "Codespaces を再起動してください。"
        )
    return key


def get_claude_api_key() -> str:
    """CLAUDE_API_KEY を優先して Anthropic APIキーを返す。"""
    key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit(
            "環境変数 CLAUDE_API_KEY が見つかりません。\n"
            "GitHub の Settings → Codespaces → Secrets に CLAUDE_API_KEY を登録し、\n"
            "Codespaces を再起動してください。"
        )
    return key
