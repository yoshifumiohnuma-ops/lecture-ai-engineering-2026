"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
import time

from anthropic import Anthropic, APIConnectionError, APIStatusError
from groq import Groq, APIConnectionError as GroqConnectionError, APIStatusError as GroqStatusError
from google import genai
from google.genai import errors, types

from app.config import (
    MODEL,
    PROVIDER,
    api_error_message,
    get_api_key,
    get_claude_api_key,
    get_groq_api_key,
)

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str, history: list[dict[str, str]] | None = None) -> str:
    messages = history.copy() if history is not None else []
    messages.append({"role": "user", "content": question})

    started_at = time.perf_counter()
    if PROVIDER == "groq":
        client = Groq(api_key=get_groq_api_key())
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        elapsed_seconds = time.perf_counter() - started_at
        answer = response.choices[0].message.content or ""
        usage = response.usage
        if usage is not None:
            print(f"[トークン] 入力: {usage.prompt_tokens}, 出力: {usage.completion_tokens}")
    elif PROVIDER == "claude":
        client = Anthropic(api_key=get_claude_api_key())
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": item["role"], "content": item["content"]} for item in messages],
        )
        elapsed_seconds = time.perf_counter() - started_at
        answer = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        print(f"[トークン] 入力: {response.usage.input_tokens}, 出力: {response.usage.output_tokens}")
    else:
        client = genai.Client(api_key=get_api_key())
        contents = []
        for item in messages:
            role = "model" if item["role"] == "assistant" else item["role"]
            contents.append(types.Content(role=role, parts=[types.Part(text=item["content"])]))
        response = client.models.generate_content(model=MODEL, contents=contents)
        elapsed_seconds = time.perf_counter() - started_at
        answer = response.text
        usage = response.usage_metadata
        if usage is not None:
            print(f"[トークン] 入力: {usage.prompt_token_count}, 出力: {usage.candidates_token_count}")

    print(f"[時間] {elapsed_seconds:.2f}秒")

    if history is not None:
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[provider] {PROVIDER}")
    print(f"[model] {MODEL}")

    history: list[dict[str, str]] = []
    question = args.question

    try:
        while True:
            print(f"[質問] {question}\n")
            answer = ask(question, history)
            print(answer)

            try:
                question = input("\n[続ける] 質問を入力（終了: exit）> ").strip()
            except EOFError:
                break
            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                continue
    except APIStatusError as e:
        print(f"Claude APIエラー（{e.status_code}）: {e.message}")
        raise SystemExit(1)
    except APIConnectionError as e:
        print(f"Claude APIへの接続に失敗しました: {e}")
        raise SystemExit(1)
    except GroqStatusError as e:
        print(f"Groq APIエラー（{e.status_code}）: {e.message}")
        raise SystemExit(1)
    except GroqConnectionError as e:
        print(f"Groq APIへの接続に失敗しました: {e}")
        raise SystemExit(1)
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
