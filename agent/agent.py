import os, sys, json
import anthropic
from dotenv import load_dotenv
from config import MODEL, SYSTEM
from tools import TOOLS, TOOL_HANDLERS

load_dotenv()

client = anthropic.Anthropic()


def run(message: str, history: list) -> tuple[str, list]:
    history.append({"role": "user", "content": message})

    while True:
        resp = client.messages.create(
            model=MODEL, max_tokens=2048, system=SYSTEM, tools=TOOLS, messages=history
        )
        history.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn":
            text = next((b.text for b in resp.content if hasattr(b, "text")), "")
            return text, history

        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            print(f"  [tool] {b.name}({json.dumps(b.input)})")
            handler = TOOL_HANDLERS.get(b.name)
            try:
                result = json.dumps(handler(b.input) if handler else {"error": f"Unknown tool: {b.name}"})
            except Exception as e:
                result = json.dumps({"error": str(e)})
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": result})
        history.append({"role": "user", "content": results})


def load_skills() -> dict[str, str]:
    path = os.path.join(os.path.dirname(__file__), "skill.md")
    skills, current = {}, None
    with open(path) as f:
        for line in f:
            if line.startswith("## "):
                current = line[3:].strip()
                skills[current] = ""
            elif current:
                skills[current] += line
    return {k: v.strip() for k, v in skills.items()}


if __name__ == "__main__":
    skills = load_skills()
    print("Market Analyzer ready. Type 'exit' to quit.")
    print("Skills: " + ", ".join(f"/{k}" for k in skills))
    history = []
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in ("exit", "quit"):
            break
        if user_input.startswith("/"):
            name = user_input[1:].lower()
            if name not in skills:
                print(f"  Unknown skill. Available: {', '.join('/' + k for k in skills)}")
                continue
            user_input = skills[name]
        response, history = run(user_input, history)
        print(f"\nAgent: {response}")
