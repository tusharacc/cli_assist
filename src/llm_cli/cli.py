import typer, os
from rich.console import Console
from .client import LLMRouter
from .embeddings import EmbeddingDB
from .prompts import PLAN_INSTRUCTION, EDIT_INSTRUCTION, LANG_PROMPTS

app = typer.Typer()
console = Console()

chat_history = []
MAX_TOKENS = 2000

def maybe_summarize(router: LLMRouter):
    global chat_history
    if sum(len(m.get("content","")) for m in chat_history) > MAX_TOKENS:
        console.print("[yellow]Summarizing chat history...[/yellow]")
        summary = router.chat([
            {"role": "system", "content": "Summarize the following conversation briefly."},
            {"role": "user", "content": str(chat_history)}
        ])
        chat_history = [{"role": "system", "content": f"Conversation so far: {summary}"}]

@app.command()
def plan(goal: str, backend: str = "rest"):
    router = LLMRouter(backend)
    db = EmbeddingDB()
    ctx = db.search(goal, top_k=5)
    snippets = "\n\n".join(c for _,c,_ in ctx)
    lang_prompt = ""
    user = f"GOAL:\n{goal}\n\nCONTEXT:\n{snippets}\n\n{lang_prompt}\n{PLAN_INSTRUCTION}"
    chat_history.append({"role": "user", "content": user})
    maybe_summarize(router)
    resp = router.chat(chat_history)
    console.print(resp)

@app.command()
def edit(path: str, instruction: str, backend: str = "rest"):
    router = LLMRouter(backend)
    db = EmbeddingDB()
    with open(path) as f:
        contents = f.read()
    ctx = db.search(instruction, top_k=3)
    snippets = "\n\n".join(c for _,c,_ in ctx)
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    lang_prompt = LANG_PROMPTS.get(ext, "")
    prompt = f"""{EDIT_INSTRUCTION}

LANGUAGE SPECIFIC GUIDELINES:
{lang_prompt}

FILE PATH: {path}
CURRENT CONTENTS:
<<<
{contents}
>>>
INSTRUCTION:
{instruction}

RELATED SNIPPETS:
{snippets}
"""
    chat_history.append({"role": "user", "content": prompt})
    maybe_summarize(router)
    resp = router.chat(chat_history)
    with open(path, "w") as f:
        f.write(resp)
    console.print(f"[green]Updated {path}[/green]")

@app.command()
def index(path: str = "."):
    db = EmbeddingDB()
    changed = db.get_changed_files()
    files = changed if changed else []
    for root, _, fnames in os.walk(path):
        for fn in fnames:
            if fn.endswith((".py",".js",".ts",".go",".ps1",".psm1")):
                full = os.path.join(root, fn)
                if not changed or full in files:
                    with open(full) as f:
                        content = f.read()
                    db.add_or_update(full, content)
                    console.print(f"Indexed {full}")

if __name__ == "__main__":
    app()
