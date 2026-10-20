import typer
import json
import hashlib
from pathlib import Path
from rich import print

app = typer.Typer(help="Git-like vcs made by dranisama")

CONFIG_FILE = Path(".dranik_config.json")
INDEX_FILE = Path(".dranik_index.json")
IGNORE_FILE = Path(".dranikignore")
default_ignore_list = {".dranik_index.json", ".dranik_config.json"}

def get_ignore_list() -> list:
    init_path = get_init_path()
    ignore_file = init_path / IGNORE_FILE
    ignore_list = ignore_file.read_text().splitlines()
    return {line.strip() for line in ignore_list if line.strip() and not line.strip().startswith("#")} | default_ignore_list

def fing_config_file():
    current_path = Path.cwd().resolve()

    for directory in (current_path, *current_path.parents):
        config_path = directory / CONFIG_FILE
        if config_path.is_file():
            return config_path
        
    return None

def get_init_path():
    config_file = fing_config_file()

    if config_file is None:
        typer.echo("You need to 'dranik init' in root folder before using other commands!")
        raise typer.Exit(code=1)
    
    try:
        data = json.loads(config_file.read_text())
        return Path(data.get("init_path"))
    except (json.JSONDecodeError, KeyError, TypeError):
        typer.echo("Invalid Dranik config file!")
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
    index_file = get_init_path() / INDEX_FILE
    current_data = json.loads(index_file.read_text())

    has_changes = False
    for key, value in new_data.items():
        if key not in current_data or current_data[key] != value:
            current_data[key] = value  
            has_changes = True

    if has_changes:
        index_file.write_text(json.dumps(current_data, indent=4))
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
    basic_ignore_str = ".git\n.venv\n__pycache__\n.pytest_cache\n.env"

    config_data = {"init_path": str(absolute_path)}
    CONFIG_FILE.write_text(json.dumps(config_data, indent=4))
    IGNORE_FILE.write_text(basic_ignore_str)

    typer.echo(f"You initialized in '{absolute_path}', also created a default ignore file  '{IGNORE_FILE.absolute()}'")

@app.command()
def listshi():
    def go_through_dir(folder_path: str):
        tree = dict()
        for path in folder_path.iterdir():
            if any(part in get_ignore_list() for part in path.parts):
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
            if any(part in get_ignore_list() for part in item.parts):
                continue
            if target_file is not None:
                if item.is_file() and item.name == target_file:
                    relative = item.relative_to(init_path)
                    index[str(relative)] = hash_file_and_name(item)
                if item.is_dir() and item.name == target_file:
                    go_through_dir(item)
            else:
                if item.is_file():
                    relative = item.relative_to(init_path)
                    index[str(relative)] = hash_file_and_name(item)
                if item.is_dir():
                    go_through_dir(item)

        return index

    if filename == ".":
        index = go_through_dir(init_path)
    if filename in get_ignore_list():
        typer.echo("The file is in '.dranikignore' or cannot be staged!")
        raise typer.Abort()
    else:
        index = go_through_dir(Path.cwd(), filename)

    if index == {}:
        typer.echo(f"Target {filename} was not found in this directory!")
        raise typer.Exit(code=1)

    index_file = get_init_path() / INDEX_FILE
    if index_file.exists():
        updated = update_json(index)
        if updated:
            typer.echo(f"Wrote to index file at {index_file.absolute()}")
            raise typer.Exit()
        
        typer.echo("No changes detected.")
        raise typer.Exit()
    
    index_file.write_text(json.dumps(index, indent=4))
    typer.echo(f"Created index file at {index_file.absolute()}")
    

    
@app.command()
def shyshalnik():
    typer.echo("""
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⣛⣫⣭⣭⣭⣛⣛⣛⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢩⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡦⡁⢀⣉⣛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⢟⣁⠀⣾⣿⡿⠟⣻⣿⣿⣿⣿⣿⣿⠿⢿⣷⣶⣶⣿⣿⣷⣮⡛⢿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠟⠡⣚⠻⠿⣦⡍⣀⡿⠿⠿⠿⢿⣿⠏⢁⣾⣿⣿⣿⣿⣿⣧⡙⣿⣿⣦⠻⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠏⢀⣴⣿⣿⡟⡀⢠⣬⣭⣭⣭⣽⣿⠏⢀⣾⡏⢱⣶⠭⠭⣭⣭⣵⠘⠿⣿⠆⢻⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⠏⣴⣿⣿⣿⠏⣴⢁⣿⣿⢃⣾⣿⣿⠏⠀⣸⠟⣀⠀⠉⠀⠸⣿⣿⣿⣇⢰⡘⣷⡄⢿⣿⣿⣿⣿
⣿⣿⣿⣿⡏⢰⡿⢛⣿⣷⣾⡇⣼⣿⠃⣼⠻⣿⡟⠀⢀⡟⣠⣥⣶⣷⣍⠂⣿⡇⡟⣿⠈⡇⢉⠓⠈⢿⣿⣿⣿
⣿⣿⣿⣿⠁⢿⠁⢸⣿⣿⢿⠀⣿⢃⡄⡿⠀⣿⠃⠐⢸⢡⣿⣿⣿⣿⣿⡇⢹⢁⠇⣿⡇⡇⢸⣧⡁⠀⢿⣿⣿
⣿⣿⣿⡏⠀⠀⠀⢸⣿⡇⠘⠀⠃⣨⣅⠀⣀⠘⢠⡀⠀⣼⡿⠿⠿⠿⢿⡇⠀⠸⠀⣿⠃⡃⢘⣻⠃⠀⠘⣿⣿
⣿⣿⣿⡇⢸⠀⢀⠘⣿⡇⠀⡦⠸⠿⠿⡀⠻⢆⠘⢷⢠⣿⠿⠿⠿⣷⣶⠄⡘⠀⢰⣿⠟⠁⠻⠁⠀⠀⠀⣿⣿
⣿⣿⣿⣷⢸⠀⠈⠀⢹⡇⠀⠀⡄⠆⠀⠀⣁⣴⣦⣄⣈⣷⡄⠈⣉⠉⠉⠀⢛⠄⣼⡟⠀⡀⢀⡄⠀⠀⢸⣿⣿
⣿⣿⣿⣿⣬⡆⠀⠀⢀⢃⢸⣦⣽⡀⠂⣀⣿⣿⣿⣿⣿⣿⣿⣿⠀⢀⡀⠰⠀⣰⡿⠃⠀⡇⢸⠀⠀⣀⠸⣿⣿
⣿⣿⣿⣿⣿⣧⠀⠀⠘⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣈⣵⡧⠀⠋⡴⠀⠂⡇⡜⠀⢀⣿⣶⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⢠⡈⢿⣿⣿⣿⣿⣿⣽⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠴⠇⠊⣸⡇⡇⣀⣼⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣧⠀⠸⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣋⣴⠁⣴⠀⠀⣿⡇⠇⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡆⢰⠀⠘⢿⣿⣿⣿⣿⣛⣿⣿⡿⢿⣿⣿⣿⣿⡿⠃⣸⠇⣀⠀⣿⡇⠀⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⠀⢰⣄⠉⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋⠀⢀⡿⠀⣹⠀⣿⡇⠀⣿⣿⣿⣿⣿⣿                      ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⠁⣸⠀⢸⣿⠄⠀⡀⠉⡛⠿⡿⠿⠛⠉⡄⠀⢠⡆⢸⡇⣸⡇⠀⢿⣇⠀⣿⣿⣿⣿⣿⣿                      ⣿⣿SHYSHALNIK LOX⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡏⠀⡇⠀⣾⣿⡆⢸⠃⡀⠀⠀⠀⠉⠉⢀⣠⠀⢸⠁⣼⠀⣿⣧⠀⠘⣿⠀⣿⣿⣿⣿⣿⣿                      ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡟⠀⢸⡇⠀⠻⠿⠟⠂⣀⣅⣀⠀⠀⣀⣘⣿⡿⠀⠀⠀⡿⠀⠿⠛⠂⠀⠹⣧⢸⣿⣿⣿⣿⣿
⣿⣿⣿⣿⠟⣩⣶⡏⢸⠇⣾⠖⠀⣀⣾⣿⣿⠅⠀⠠⣽⠿⣋⣵⢆⣆⠀⠃⠰⡞⢁⣾⣿⣶⣅⢸⣿⣿⣿⣿⣿
⣿⣿⣿⢃⣾⣿⣿⠃⣿⠀⡠⣪⣾⡿⠋⣁⠤⣤⣤⡤⢀⠩⡛⢿⣿⡌⠆⠀⠀⣰⣿⣿⣿⣿⣿⣆⢻⣿⣿⣿⣿
⣿⣿⡇⣼⣿⣿⠟⢸⠏⠸⠾⣿⠋⠀⣾⠄⠂⣸⣏⠀⠀⠾⡆⠈⣿⣿⡄⠀⢸⣿⣿⣿⣿⣿⣿⣿⡂⢿⣿⣿⣿
⣿⣿⢀⡌⢿⣿⠆⢾⠀⠀⠀⠹⠗⢠⡈⠠⢼⣿⡧⠄⠛⠁⢀⣴⡏⠉⠁⠀⠀⣿⣿⠿⣿⣿⣿⣿⡆⢸⣿⣿⣿
⣿⣿⢸⣿⣤⠭⠀⠀⠀⣹⣷⣦⣵⣶⣭⡂⠀⠉⠀⢀⣠⣤⣔⠭⡥⠀⠀⢠⡀⡿⣋⣴⣿⣿⣿⢟⠁⣿⣿⣿⣿
⣿⡟⠸⠛⠡⠀⠀⠃⣰⣿⣿⣿⣿⣿⣿⣿⣷⣶⣾⣿⣿⣿⣿⣷⣾⣧⡀⢸⡇⠈⢿⢡⣦⣉⣡⡟⠀⢹⣿⣿⣿
⡿⠀⠀⡀⠄⠀⡄⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠐⠃⠀⠀⠘⢿⣿⣿⠃⢸⡀⣿⣿⣿
⡇⠀⠈⠀⠐⠀⡇⣤⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⢀⠠⠀⠠⡀⠙⠟⠀⠀⣇⢸⣿⣿
⣇⠐⠀⢀⠀⠀⠇⣩⡄⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣣⡆⢛⠀⠀⠀⠈⠀⠀⢠⠀⢹⡈⣿⣿
⣿⠄⠐⠀⠀⠀⢠⣿⣷⣬⡻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢛⣰⣮⠡⠰⠐⣦⡀⢀⠀⠀⢺⣇⠀⠇⢸⣿
⣿⠠⣄⠀⡀⠀⠸⠍⠛⠻⣿⣷⣮⣭⣙⣛⣛⣛⣛⣛⣛⣫⣥⡶⠿⠟⣛⣿⠀⡇⢿⠃⠀⠀⠀⠈⠹⠀⠘⡄⢿
⣿⣿⡆⠀⠇⠀⣤⠀⠀⠈⠛⠿⢿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣦⠀⠘⠛⠋⡁⠘⣤⠂⠀⢸⣋⡄⠀⠀⠀⠀⢸
""")



if __name__ == "__main__":
    app()