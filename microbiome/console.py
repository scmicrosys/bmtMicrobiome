import os
from os import makedirs
from pathlib import Path
import time
from configparser import ConfigParser

import typer
import subprocess

from crud import drop_tables, create_tables
from blast import create_blast_db, parse_results, query_blast

app = typer.Typer()

APP_NAME = "microbiome"
APP_DIR = typer.get_app_dir(APP_NAME)
APP_CONFIG: Path = Path(APP_DIR) / "config.ini"

config = ConfigParser()

# Utils
done = typer.style("Done!", fg=typer.colors.GREEN, bold=True)


@app.command("setup")
def setup_path():
    """Setup and verify paths. Do this first."""
    confirm = typer.confirm(
        "Do you want to specify again the configuration variables?")
    if confirm is True:
        blast_name = typer.prompt(
            "Give a name to the blast database")
        if not blast_name.endswith(".fa"):
            blast_name = blast_name+".fa"
        main_path = typer.prompt(
            "What is the full path of the project folder?")
        data_path = typer.prompt(
            "What is the full path of the 'data' folder containing subfolders 'queries'"
            " 'database' and 'results?")
        fa_files_path = typer.prompt("What is the full path of the folder containin"
                                     " the results from gapseq?")
        postgres_name = typer.prompt(
            "What is the name of the postgres database?")
        postgres_username = typer.prompt(
            "What is the username with access to the postgres database?")
        uri = f"postgres+psycopg2://{postgres_username}@localhost:5432/{postgres_name}"
        config.add_section('NAMES')
        config.set('NAMES', 'database_name', str(blast_name))
        config.add_section('PATHS')
        config.set('PATHS', 'main_path', str(main_path))
        config.set('PATHS', 'data_dir_path', str(data_path))
        config.set('PATHS', 'fa_files_path', str(fa_files_path))
        config.add_section('DATABASE')
        config.set('DATABASE', 'uri', str(uri))
        with open(APP_CONFIG, 'w') as configfile:
            config.write(configfile)
    if not APP_CONFIG.is_file():
        typer.secho("Config file cancelled or doesn't exist yet",
                    fg=typer.colors.YELLOW)
        blast_name = typer.prompt(
            "Give a name to the blast database")
        if not blast_name.endswith(".fa"):
            blast_name = blast_name+".fa"
        main_path = typer.prompt(
            "What is the full path of the project folder?")
        data_path = typer.prompt("What is the full path of the 'data' folder"
                                 " containing subfolders queries', 'database' and"
                                 " 'results?")
        fa_files_path = typer.prompt("What is the full path of the folder containing"
                                     " the results from gapseq?")
        postgres_name = typer.prompt(
            "What is the name of the postgres database?")
        postgres_username = typer.prompt(
            "What is the username with access to the postgres database?")
        uri = f"postgres+psycopg2://{postgres_username}@localhost:5432/{postgres_name}"
        config.add_section('NAMES')
        config.set('NAMES', 'database_name', blast_name)
        config.add_section('PATHS')
        config.set('PATHS', 'main_path', str(main_path))
        config.set('PATHS', 'data_dir_path', str(data_path))
        config.set('PATHS', 'fa_files_path', str(fa_files_path))
        config.add_section('DATABASE')
        config.set('DATABASE', 'uri', str(uri))
        try:
            makedirs(APP_DIR)
        except OSError:
            print(
                f"Creation of the directory failed (or already existing) at {APP_DIR}")
        else:
            print(f"Successfully created the directory at {APP_DIR}")
        with open(APP_CONFIG, 'w') as configfile:
            config.write(configfile)
    else:
        config.read_file(open(APP_CONFIG))
        typer.echo("Please check whether the following configuration are correct."
                   " If they are not correct the program will fail.")
        main_path = config.get("PATHS", "main_path")
        typer.secho(f"The main folder path is {main_path}",
                    fg=typer.colors.YELLOW)
        data_path = config.get("PATHS", "data_dir_path")
        typer.secho(f"The data folder, within the main folder, is {data_path}",
                    fg=typer.colors.YELLOW)
        files_path = config.get("PATHS", "fa_files_path")
        typer.secho(
            f"The output of gapseq files are contained in the folder {files_path}",
            fg=typer.colors.YELLOW)
        database_uri = config.get("DATABASE", "uri")
        typer.secho(f"The database URI is {database_uri}",
                    fg=typer.colors.YELLOW)
    typer.echo(done)


@ app.command("blast-create-database")
def create_db_blast():
    """Create the Blast database.

    Follow the instructions after calling `create-blast-databse` to setup
    the blast database. Afterwards you will use the `query-blast-database`
    command to query this database.
    """
    if not APP_CONFIG.is_file():
        typer.secho("Please, first setup the variables using `microbiome setup`",
                    fg=typer.colors.YELLOW)
        raise typer.Abort()
    config.read_file(open(APP_CONFIG))
    PATH_FA_FILES = config.get("PATHS", "fa_files_path")
    DATABASE_NAME = config.get("NAMES", "database_name")
    DATA_DIR_PATH = config.get("PATHS", "data_dir_path")

    typer.secho(f"The database name is set to {DATABASE_NAME}",
                fg=typer.colors.YELLOW)

    if os.path.isdir(PATH_FA_FILES):
        typer.secho("The path of the gapseq .fa and .xml files"
                    f" is set to {PATH_FA_FILES}",
                    fg=typer.colors.YELLOW)
    else:
        typer.secho("The path for the .fa and .xml files set in config.ini does"
                    " not exist. Please correct it manually modifying"
                    " the config.ini file.",
                    fg=typer.colors.YELLOW)
        raise typer.Abort()

    delete = typer.confirm(
        "Do you want to continue in the creation of the blast database?")
    if not delete:
        typer.echo("Not continuing")
        raise typer.Abort()
    typer.echo("Continuing")

    # Run the
    bashCommandCreate = f"cd {PATH_FA_FILES} && cat *.fa > {DATABASE_NAME}"
    typer.echo(
        "Creating a unique .fa file from all the .fa files contained in the folder"
        " selected...")
    try:
        subprocess.call(bashCommandCreate, shell=True)
    except Exception as e:
        print(e.message, e.args)

    typer.echo(done)

    # Wait for 2 seconds
    time.sleep(2)

    old_database_path = os.path.join(PATH_FA_FILES, DATABASE_NAME)
    database_dir = os.path.join(DATA_DIR_PATH, "database")
    new_database_path = os.path.join(
        database_dir, DATABASE_NAME)
    # Move database .fa without renaming
    bashCommandMove = f"mv {old_database_path} {new_database_path}"
    typer.echo("Moving the blast database to the working directory...")
    try:
        subprocess.call(bashCommandMove, shell=True)
    except Exception as e:
        print(e.message, e.args)
    typer.echo(done)

    # Wait for 2 seconds
    time.sleep(2)

    # Create blast database from newly created file
    create_blast_db(
        fa_file_path=new_database_path,
        dbtype="nucl")

    typer.echo(done)


@ app.command("blast-query")
def queryBlast(
    all: bool = typer.Option(
        False,
        "--all",
        prompt="Do you have more than one file that you want to query?",
        help="True is you have more than one file to query"),
    evalue: float = typer.Argument(
        0.001,
        show_default=True,
        help="Value to assing to the `evalue` parameter"),
    outfmt: int = typer.Argument(
        5,
        show_default=True,
        help="Value to assing to the `outfmt` parameter")
):
    """Query the Blast database"""
    config.read_file(open(APP_CONFIG))
    if not APP_CONFIG.is_file():
        typer.secho("Please, first setup the variables using `microbiome setup`",
                    fg=typer.colors.YELLOW)
        raise typer.Abort()

    DATA_DIR_PATH = config.get("PATHS", "data_dir_path")
    OUTPUT_PATH = os.path.join(DATA_DIR_PATH, "results")
    DB_NAME = config.get("NAMES", "database_name")
    if not DB_NAME.endswith(".fa"):
        DB_NAME = DB_NAME+".fa13"
    DB_PATH = os.path.join(DATA_DIR_PATH, "database", DB_NAME)
    queries_path = os.path.join(DATA_DIR_PATH, "queries")

    if all is True:
        if os.listdir(queries_path):
            for file in os.listdir(queries_path):
                file_name = os.path.basename(file)
                file_path = os.path.join(queries_path, file_name)

                if os.path.isfile(file_path) and file_name.endswith(".fa"):
                    typer.secho(
                        f"Querying file: {file_name}", fg=typer.colors.YELLOW)
                    query_blast(
                        fa_path=file_path,
                        evalue=evalue,
                        outfmt=outfmt,
                        DATA_DIR_PATH=DATA_DIR_PATH,
                        OUTPUT_PATH=OUTPUT_PATH,
                        DB_NAME=DB_NAME,
                        DB_PATH=DB_PATH)
                else:
                    continue
            typer.secho("Queries completed and saved in `results`",
                        fg=typer.colors.YELLOW)
        else:
            typer.secho("No file found!", fg=typer.colors.YELLOW)
            raise typer.Abort()
    else:
        file_name = typer.prompt("What is the full name of the .fa file you want to"
                                 " query? It needs to be in the `queries` folder.")
        file_path = os.path.join(queries_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".fa"):
            typer.secho(
                f"The file path is {file_path}", fg=typer.colors.YELLOW)
        else:
            typer.secho(
                f"Could not find any file with filename: {file_name}",
                fg=typer.colors.YELLOW)
            raise typer.Abort()

        query = query_blast(
            fa_path=file_path,
            evalue=evalue,
            outfmt=outfmt,
            DATA_DIR_PATH=DATA_DIR_PATH,
            OUTPUT_PATH=OUTPUT_PATH,
            DB_NAME=DB_NAME,
            DB_PATH=DB_PATH)

        typer.secho(
            "Query completed and saved in " + query["result_path"],
            fg=typer.colors.YELLOW)


@ app.command("blast-parse")
def parse_result(
    all: bool = typer.Option(
        False,
        "--all",
        prompt="Do you have more than one file that you want to parse?",
        help="True is you have more than one file to parse"),
    add_to_db: bool = typer.Argument(
        True,
        help="Add the parsed results to the existing database"),
    top_k: int = typer.Argument(
        3,
        help="The number of top results to parse")):
    """Parse an already existing blast result."""
    config.read_file(open(APP_CONFIG))
    if not APP_CONFIG.is_file():
        typer.secho("Please, first setup the variables using `microbiome setup`",
                    fg=typer.colors.YELLOW)
        raise typer.Abort()

    DATA_DIR_PATH = config.get("PATHS", "data_dir_path")
    FA_FILES_PATH = config.get("PATHS", "fa_files_path")
    results_path = os.path.join(DATA_DIR_PATH, "results")

    if all is True:
        if os.listdir(results_path):
            for file in os.listdir(results_path):
                file_name = os.path.basename(file)
                file_path = os.path.join(results_path, file_name)

                if os.path.isfile(file_path) and file_name.endswith(".xml"):
                    typer.secho(
                        f"Parsing file: {file_name}", fg=typer.colors.YELLOW)
                    parse_results(
                        path=file_path,
                        file_name=file_name,
                        FA_FILES_PATH=FA_FILES_PATH,
                        top_k=top_k,
                        add_to_db=add_to_db,
                    )
                else:
                    continue
            typer.echo(done)
        else:
            typer.secho("No file found!", fg=typer.colors.YELLOW)
            raise typer.Abort()

    else:
        file_name = typer.prompt("What is the full name of the .xml file you want to"
                                 " parse? It needs to be in the `results` folder.")
        if not file_name.endswith(".xml"):
            file_name = f"{file_name}.xml"
        file_path = os.path.join(results_path, file_name)
        if os.path.isfile(file_path):
            typer.secho(
                f"The file path is {file_path}", fg=typer.colors.YELLOW)
        else:
            typer.secho("Could not find any file", fg=typer.colors.YELLOW)
            raise typer.Abort()

        parse_results(
            path=file_path,
            file_name=file_name,
            FA_FILES_PATH=FA_FILES_PATH,
            top_k=top_k,
            add_to_db=add_to_db)

        typer.echo(done)


@ app.command("results-recreate-database")
def recreate_db(
        confirm: bool = typer.Option(
            False,
            "--confirm",
            help="Confirm to recreate the database. Data will be lost.",
            prompt="Do you want to recreate the database? Data will be lost"
        )):
    """Recreate the database"""

    if confirm:
        drop_tables()
        create_tables()
    else:
        raise typer.Abort()


@ app.command("test-app")
def test_app(
        confirm: bool = typer.Argument(
            False,
            help="Confirm to test the app."
        )):
    """Test the app"""

    if confirm:
        print(True)
    else:
        print(False)


if __name__ == "__main__":
    app()
