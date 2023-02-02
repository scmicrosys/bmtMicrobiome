# # crud.py

import os
from datetime import datetime
from pathlib import Path
from configparser import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from models import Base, Record

import typer

app = typer.Typer()
APP_NAME = "microbiome"
APP_DIR = typer.get_app_dir(APP_NAME)
APP_CONFIG: Path = Path(APP_DIR) / "config.ini"

config = ConfigParser()


@contextmanager
def session_scope():
    config.read_file(open(APP_CONFIG))
    DATABASE_URI = config.get("DATABASE", "uri")
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def drop_tables():
    print("Dropping all tables")
    config.read_file(open(APP_CONFIG))
    DATABASE_URI = config.get("DATABASE", "uri")
    engine = create_engine(DATABASE_URI)
    Base.metadata.drop_all(engine)


def create_tables():
    print("Creating all tables")
    config.read_file(open(APP_CONFIG))
    DATABASE_URI = config.get("DATABASE", "uri")
    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(engine)


def add_to_database(results, FA_FILES_PATH):
    """Using blast results, add files to the database.

    The function compares with the .fa files used in the blast database
    and takes the SMBL xml resulting from the gapseq.
    """
    list_fas = [file for file in os.listdir(FA_FILES_PATH)]

    for result in results:
        id = result["id"]
        if (f"{id}.xml" in list_fas and f"{id}.fa" in list_fas):
            smbl_file_path = os.path.join(FA_FILES_PATH, f"{id}.xml")
            fa_file_path = os.path.join(FA_FILES_PATH, f"{id}.fa")
            record = Record(
                id=id,
                full_name=result["full_name"][0],
                bitscore=result["bitscore"],
                evalue=result["evalue"],
                order_match=result["rank"],
                query_range=str(result["query_range"]),
                hit_range=str(result["hit_range"]),
                smbl_xml=smbl_file_path,
                fasta=fa_file_path,
                created=datetime.now()
            )
            with session_scope() as s:
                s.add(record)
            print(f"Added {id}")
        else:
            print(f"No .fa file found in {FA_FILES_PATH}")
