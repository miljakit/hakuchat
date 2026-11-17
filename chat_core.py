from openai import OpenAI
import os
import json
from search import web_search
from dotenv import load_dotenv

load_dotenv()

WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information using DuckDuckGo.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPEN_ROUTER_API_KEY"],
)

MODEL = "nvidia/nemotron-3.5-super-vl:free"
MAX_ROUNDS = 5


def chat(messages: list[dict]) -> str:
    for round_num in range(MAX_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[WEB_SEARCH_TOOL],
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message.model_dump())
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"[Tool call] {func_name}({args})")

                if func_name == "web_search":
                    results = web_search(args.get("query", ""), args.get("max_results", 5))
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(results, ensure_ascii=False),
                    })
            continue

        return message.content or ""

    return "Max rounds exceeded"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python chat_core.py \"your question\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    messages = [{"role": "user", "content": query}]
    answer = chat(messages)
    print("\n--- Answer ---\n")
    print(answer)