import typer
import json
import hashlib
import gzip
from pathlib import Path
from rich import print
from datetime import datetime, timezone

app = typer.Typer(help="Git-like vcs made by dranisama")

CONFIG_FILE = Path(".dranik/config.json")
INDEX_FILE = Path(".dranik/index.json")
IGNORE_FILE = Path(".dranikignore")
HEAD_FILE = Path(".dranik/HEAD")
DEFAULT_BRANCH_FILE = Path(".dranik/refs/heads/main")
default_ignore_list = {".dranik"}

def get_ignore_list() -> set[str]:
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

def get_index_data() -> dict:
    init_path = get_init_path()
    index_file = init_path / INDEX_FILE
    
    try:
        data = json.loads(index_file.read_text())
        return data
    except (json.JSONDecodeError):
        typer.echo("Invalid index file!")
        raise typer.Exit(code=1)

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


#this too bruv
def get_head_commit():
    init_path = get_init_path()
    head_file = init_path / HEAD_FILE

    head_content = head_file.read_text().strip()
    current_branch = head_content.removeprefix("ref: ")

    branch_file = init_path / current_branch

    head_commit_hash = branch_file.read_text().strip()

    return head_commit_hash or None

#change this for branching
def write_head(commit_hash):
    init_path = get_init_path()
    head_file = init_path / HEAD_FILE

    head_content = head_file.read_text().strip()
    current_branch = head_content.removeprefix("ref: ")

    branch_file = init_path / current_branch
    branch_file.write_text(commit_hash)
    
def serialize_dik(data: dict) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        indent=4
    ).encode()

def read_commit(file_hash: str):
    if file_hash is None or len(file_hash) < 64:
        return {}

    init_path = get_init_path()
    commit_file = init_path / ".dranik" / "objects" / file_hash
    
    try:
        data = json.loads(commit_file.read_text())
        return data
    except (json.JSONDecodeError):
        typer.echo("Invalid index file!")
        raise typer.Exit(code=1)


def hash_file(file_path: Path):
    hasher = hashlib.sha256()

    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)

    return hasher.hexdigest()

def store_file(file_path: Path, file_hash: str):
    init_path = get_init_path()

    object_file = init_path / Path(f".dranik/objects/{file_hash}")
    object_file.parent.mkdir(parents=True, exist_ok=True)

    if object_file.exists():
        return

    with file_path.open("rb") as src, object_file.open("wb") as raw_dst:
        with gzip.GzipFile(fileobj=raw_dst, mode="wb") as dst:
            while chunk := src.read(65536):
                dst.write(chunk)


    

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

def index_into_nested_dict(current_data):
    result = dict()

    for key in current_data.keys():
        current = result
        splitted = key.split('/')
        
        for i in splitted:
            if i == splitted[-1]:
                current[i] = current_data[key]
            else:
                if i not in current:
                    current[i] = {}
                current = current[i] 

    return result


def nested_to_tree_objects(nested_dik: dict, write_files: bool = True):
    res = dict()
    for key in nested_dik.keys():
        if not isinstance(nested_dik[key], dict):
            res[key] = {"type": "blob", "hash": nested_dik[key]}
        else:
            res[key] = {"type": "tree", "hash": nested_to_tree_objects(nested_dik[key], write_files)}


    serialized = serialize_dik(res)
    tree_hash = hashlib.sha256(serialized).hexdigest()
    if write_files:
        object_file = get_init_path() / Path(f".dranik/objects/{tree_hash}")
        if not object_file.exists():
            object_file.write_bytes(serialized)
    

    return tree_hash

@app.command()
def bark():
    init_path = get_init_path()
    typer.echo(f"Woof woof! Working inside initialized path: {init_path}")


@app.command()
def init():
    absolute_path = Path(".").resolve()
    basic_ignore_str = ".git\n.venv\n__pycache__\n.pytest_cache\n.env"
    config_data = {"init_path": str(absolute_path)}

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_BRANCH_FILE.parent.mkdir(parents=True, exist_ok=True)

    CONFIG_FILE.write_text(json.dumps(config_data, indent=4))
    IGNORE_FILE.write_text(basic_ignore_str)
    INDEX_FILE.write_text(json.dumps({}))
    DEFAULT_BRANCH_FILE.touch()
    HEAD_FILE.write_text(f"ref: {DEFAULT_BRANCH_FILE}")

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

    if filename == ".":
        path = Path.cwd().resolve()
    else:
        path = (Path.cwd() / filename).resolve()

    if not path.is_relative_to(init_path.resolve()):
        typer.echo("Cannot stage files outside of repository!")
        raise typer.Exit(code=1)

    index = dict()
    
    def go_through_dir(folder_path, target_file = None):
        for item in folder_path.iterdir():
            if any(part in get_ignore_list() for part in item.parts):
                continue
            if target_file is not None:
                if item.is_file() and item.name == target_file:
                    relative = item.relative_to(init_path)
                    file_hash = hash_file(item)
                
                    store_file(item.absolute(), file_hash)
                    index[str(relative)] = file_hash

                if item.is_dir() and item.name == target_file:
                    go_through_dir(item)
            else:
                if item.is_file():
                    relative = item.relative_to(init_path)
                    file_hash = hash_file(item)

                    store_file(item.absolute(), file_hash)
                    index[str(relative)] = file_hash
                    
                if item.is_dir():
                    go_through_dir(item)

        return index

    if filename == ".":
        index = go_through_dir(path)
    elif filename in get_ignore_list():
        typer.echo("The file is in '.dranikignore' or cannot be staged!")
        raise typer.Abort()
    elif "/" in filename:
        path = Path(filename)
        index = go_through_dir(path.parent.absolute(), path.name)
    else:
        index = go_through_dir(Path.cwd(), filename)

    #before here type beat
    index_file = get_init_path() / INDEX_FILE
    # for key in get_index_data().keys():
    #     for kekey in index.keys():
    #         if filename in key.split("/") and not filename in kekey.split("/"):
    #             pass #do something
    if index == {}:
        typer.echo(f"No stageable files found for '{filename}'.")
        raise typer.Exit(code=1)

   
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
def commit(message: str):
    if len(message) == 0:
        typer.echo("You need to write a commit message!")
        raise typer.Exit(code=1)

    index_path = get_init_path() / ".dranik" / "index.json"
    if not index_path.exists():
        typer.echo("Nothing to commit. Use 'dranik add' first!")
        raise typer.Exit(code=1)

    current_data = get_index_data()
    if not current_data:
        typer.echo("Nothing to commit! The staging area is empty!!1")
        raise typer.Exit(code=1)

    tree_hash = nested_to_tree_objects(index_into_nested_dict(current_data))
    if tree_hash == read_commit(get_head_commit()).get("tree"):
        typer.echo("Cant commit with no changes!")
        raise typer.Exit(code=1)


    commit_data = {
        "tree": tree_hash,
        "parent": get_head_commit(),
        "message": message,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    serialized = serialize_dik(commit_data)

    commit_hash = hashlib.sha256(serialized).hexdigest()
    object_file = get_init_path() / Path(f".dranik/objects/{commit_hash}")
    object_file.write_bytes(serialized)

    write_head(commit_hash)

    typer.echo("Commited succesfully!")

@app.command()
def log(graph: bool = typer.Option(False, "--graph", help="Show as commit graph")):
    head = get_head_commit()
    if head is None:
        typer.echo("No head commit! Cant build a history.")
        raise typer.Exit(code=1)

    history = []
    current = head
    while current:
        commit_data = read_commit(current)
        history.append((current, commit_data))
        next_parent = commit_data.get("parent")
        current = next_parent

    for i, (commit_hash, info) in enumerate(history):
        raw_data = info.get("created_at", "")
        try:
            dt = datetime.fromisoformat(raw_data)
            date_str = dt.strftime("%a %b %d %H:%M:%S %Y %z")
        except ValueError:
            date_str = raw_data

        if graph:
            print(f"* [yellow]{commit_hash}[/yellow] [bright_black]{date_str}[/bright_black]")
            print(f"|  {info.get("message")}")
            if len(history) <= i:
                return
            print("|")
        else:
            print(f"commit [yellow]{commit_hash}[/yellow]  (tree: {info.get("tree")})")
            print(f"Date:   [bright_black]{date_str}[/bright_black]\n")
            print(f"    {info.get("message")}\n")


@app.command()
def branch(name: str = typer.Argument(None, help="Pass name to create a branch")):
    init_path = get_init_path()
    if name is None:
        head_file = init_path / HEAD_FILE
        head_content = head_file.read_text().strip()
        current_branch = head_content.removeprefix("ref: ").split("/")
        print(f"Currently on branch [green]{current_branch[-1]}[/green]")
        raise typer.Exit(code=1)
    
    branch_file = init_path / ".dranik" / "refs" / "heads" / name

    if branch_file.exists():
        print(f"[red]Branch [bold]{name}[/bold] already exists![/red]")
        raise typer.Exit(code=1)

    branch_file.write_text(get_head_commit() or "")

    print(f"Succesfully created branch [green]'{name}'[/green]\nUse [bright_black]dranik switch[/bright_black] to switch between branches.")
    raise typer.Exit(code=0)

@app.command()
def switch(branch_name):
    init_path = get_init_path()

    if read_commit(get_head_commit()).get("tree", nested_to_tree_objects({}, False)) != nested_to_tree_objects(index_into_nested_dict(get_index_data()), write_files=False):
        print(f"[red]Cant switch until staged changes are commited![/red]")
        raise typer.Exit(code=1)

    branch_file = init_path / ".dranik" / "refs" / "heads" / branch_name

    if not branch_file.is_file():
        print(f"[red]No branch named [bold]'{branch_name}'[/bold]![/red]")
        raise typer.Exit(code=1)
    

    head_file = init_path / HEAD_FILE
    head_file.write_text(f"ref: {branch_file.relative_to(init_path)}")
    print(f"Switched to branch [green]{branch_name}[/green]")
    raise typer.Exit(code=0)
    
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