# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
第1回の素のLLMでは、質問をLLMに1回渡して、LLMが直接回答していた。
一方、第3回のエージェントでは、質問に応じてLLMが適切なツールを選び、プログラムがそのツールを実行する。その結果を再びLLMへ渡して、最終的な回答を生成していた。
今回の質問では、エージェントが `make_quiz` を呼び出して第2回の内容から問題を作成し、その結果をもとに確認問題を回答した。そのため、素のLLMよりも、講座の用語集や講義内容などの外部情報を利用した回答になっていた。

- `--trace` で見えたツール呼び出し（ツール名と引数）：
以下のツール呼び出しが確認できた。
```text
[tool call] make_quiz({'lecture': 2})
第2回の講義内容を指定するため、引数 lecture に 2 が渡されていた。

- 1つの質問での LLM 呼び出し回数（`requests`）：
--trace の出力に、
[usage] RunUsage(... requests=2, ... tool_calls=1)
と表示された。
したがって、今回の1つの質問では、LLMが2回呼び出された。1回目にツールの選択と引数の指定を行い、make_quiz の実行結果を受け取った後、2回目に最終的な回答を生成したと考えられる。

- 追加したツールと、docstring に書いた説明：
追加したツールは make_quiz である。
make_quiz は、指定した講義回の内容から確認問題を1問作成するツールである。引数として講義回を表す整数 lecture を受け取り、問題文と答えを返す。
docstringには、確認問題・復習問題・クイズを求められたときに使うツールであり、講義の要約ではなく問題を出題するためのツールであることを説明した。

## 宿題

- 取り組んだレベル：発展
- やったこと：
演習版で作成したエージェントと同じ `INSTRUCTIONS` およびツールを利用し、
エージェントを組み立てる部分を Google ADK で実装した。

新しく次のファイルを作成した。

- `adk_agent/glossary_agent/__init__.py`
- `adk_agent/glossary_agent/agent.py`

`adk_agent/glossary_agent/agent.py` では、`google.adk.agents.Agent` を使って
`root_agent` を作成した。演習版の `INSTRUCTIONS` と、以下のツールを再利用した。
- `search_glossary`
- `get_lecture_summary`
- `make_quiz`
ADK版では、演習版の `agent.tool_plain(...)` の代わりに、
`Agent` の生成時に `tools=[...]` としてツールのリストを渡した。
ADK版は、次のコマンドで起動した。

PYTHONPATH=. uv run --with google-adk adk run adk_agent/glossary_agent

- 結果：
ADKの対話画面で、演習版と同じ質問を実行した。
「第2回の内容から確認問題を1問出して」
その結果、次のような確認問題が生成された。
「エポック」とは何ですか？
ADK版でも、第2回に関する確認問題を生成できることを確認した。
また、ADKのログには、次のようにモデルへのリクエストとレスポンスが2組記録された。
Sending out request ... gemini-3.1-flash-lite
Response received from the model.
Sending out request ... gemini-3.1-flash-lite
Response received from the model.
演習版では、--trace に次のツール呼び出しが表示された。
[tool call] make_quiz({'lecture': 2})
一方、ADK版の通常の対話画面では、演習版のような [tool call] の表示は確認できなかった。ただし、ADK版でも同じ質問に対して 確認問題を生成できた。

- 気づき・疑問：
演習版では、pydantic_ai.Agent を作成したあと、 agent.tool_plain(...) を使ってツールを個別に登録していた。
一方、ADK版では、google.adk.agents.Agent の生成時に、
tools=[
    tools.search_glossary,
    tools.get_lecture_summary,
    tools.make_quiz,
]
のように、ツールをリストで渡していた。
また、演習版では独自に実装した --trace によって、
[tool call] make_quiz({'lecture': 2})
のように、ツール名と引数を確認できた。
ADK版では同じ形式のトレース表示はなかったが、ADKのログからモデルへの リクエストが2回行われたことは確認できた。これは、ツールを使うための モデル呼び出しと、ツール実行後の最終回答生成が行われたためだと考えられる。
今回の比較から、ADKではエージェントの起動や対話部分をフレームワークが 用意してくれる一方、演習版ではエージェントのループやトレース表示を 自分で実装していることが分かった。
また、どちらの実装でも、モデルが指示文とツールの説明をもとにツールを 選択している点は共通している。ADK版でも、make_quiz を含む同じツール群と INSTRUCTIONS を渡すことで、確認問題を生成できた。

