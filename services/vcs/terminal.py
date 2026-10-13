import typer
from pathlib import Path
from rich import print

app = typer.Typer(help="Git-like vcs made by dranisama")

dir_path = Path(".")
skip_list = {'.venv', '.git', '__pycache__', ".pytest_cache", ".env", ".coverage"}

@app.command()
def bark():
    typer.echo("Woof woof")

@app.command()
def listshi():
    def go_through_dir(folder_path: str):
        tree = dict()
        for path in folder_path.iterdir():
            if any(part in skip_list for part in path.parts):
                continue
            if path.is_dir():
                tree[path.name] = go_through_dir(path)
            if path.is_file():
                tree[path.name] = "File"


        return tree

    print(go_through_dir(dir_path))


if __name__ == "__main__":
    app()