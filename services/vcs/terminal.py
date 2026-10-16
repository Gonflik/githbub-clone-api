import typer
import json
import hashlib
from pathlib import Path
from rich import print

app = typer.Typer(help="Git-like vcs made by dranisama")

CONFIG_FILE = Path(".dranik_config.json")
#IGNORE_FILE = Path(".dranikignore")
INDEX_FILE = Path(".dranik_index.json")
skip_list = {'.dranik_index.json', '.dranik_config.json','.venv', '.git', '__pycache__', ".pytest_cache", ".env", ".coverage", ".egg-info"}

def get_init_path():
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return Path(data.get("init_path"))
        except json.JSONDecodeError:
            return None
    typer.echo("You need to 'dranik init' in root folder before using other commands!")
    raise typer.Exit(code=1)

def hash_file_and_name(file_path: Path):
    hasher = hashlib.sha256()

    file_name = file_path.name
    hasher.update(file_name.encode('utf-8'))

    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)

    return hasher.hexdigest()

def update_json(new_data):
    current_data = json.loads(INDEX_FILE.read_text())

    has_changes = False
    for key, value in new_data.items():
        if key not in current_data or current_data[key] != value:
            current_data[key] = value  
            has_changes = True

    if has_changes:
        INDEX_FILE.write_text(json.dumps(current_data, indent=4))
        return True
    else:
        return False

@app.command()
def bark():
    init_path = get_init_path()
    typer.echo(f"Woof woof! Working inside initialized path: {init_path}")

@app.command()
def init():
    absolute_path = Path(".").resolve()

    config_data = {"init_path": str(absolute_path)}
    CONFIG_FILE.write_text(json.dumps(config_data, indent=4))

    typer.echo(f"You initialized in '{absolute_path}'")

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

    root_path = get_init_path()
    print(go_through_dir(root_path))

@app.command()
def add(filename: str):
    init_path = get_init_path()
    index = dict()
    
    def go_through_dir(folder_path, target_file = None):
        for item in folder_path.iterdir():
            if any(part in skip_list for part in item.parts):
                continue
            if target_file is not None:
                if item.is_file() and item.name == target_file:
                    relative = item.relative_to(init_path)
                    index[str(relative)] = hash_file_and_name(item)
            else:
                if item.is_file():
                    relative = item.relative_to(init_path)
                    index[str(relative)] = hash_file_and_name(item)
            if item.is_dir():
                go_through_dir(item, target_file)

        return index

    if filename in skip_list:
        typer.echo("The file is in skip list! Cant stage it.")
        raise typer.Abort()
    if filename == ".":
        index = go_through_dir(init_path)
    else:
        index = go_through_dir(init_path, filename)


    if INDEX_FILE.exists():
        updated = update_json(index)
        if updated:
            typer.echo(f"Wrote to index file at {INDEX_FILE.absolute()}")
            raise typer.Exit()
        
        typer.echo("No changes detected.")
        raise typer.Exit()
    
    INDEX_FILE.write_text(json.dumps(index, indent=4))
    typer.echo(f"Created index file at {INDEX_FILE.absolute()}")
    

    




if __name__ == "__main__":
    app()