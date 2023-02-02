# blast.py
import os

from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast.Applications import NcbimakeblastdbCommandline
from Bio import SearchIO

from crud import add_to_database

"""
TODO: parse_result: correct the value_tresh to float like 1e-20
"""


def create_blast_db(fa_file_path=None, dbtype="nucl"):
    """Creates a new blast db

    As input takes the path of the collection of *.fa files.
    """
    print("Creating the blast DB...")

    create = NcbimakeblastdbCommandline(
        input_file=fa_file_path,
        dbtype=dbtype)

    create()

    print(f"Blast DB created at {fa_file_path}.")


def query_blast(
        fa_path,
        DATA_DIR_PATH,
        OUTPUT_PATH,
        DB_NAME,
        DB_PATH,
        evalue=0.001,
        outfmt=5):
    """Uses the Ncbiblastn to blast the blast DB with the query file

        Returns the path of the result.
        """

    print("Querying the blast db...")

    OUT_FILE_NAME = os.path.basename(os.path.splitext(fa_path)[0]+".xml")
    OUT = os.path.join(OUTPUT_PATH, OUT_FILE_NAME)

    cline = NcbiblastnCommandline(
        cmd='blastn',
        query=fa_path,
        db=DB_PATH,
        evalue=evalue,
        outfmt=outfmt,
        out=OUT)

    cline()

    # Return path and name of the query's result
    query = {"result_path": OUT, "result_name": OUT_FILE_NAME}
    return(query)


def parse_results(
        path,
        file_name,
        FA_FILES_PATH,
        top_k=3,
        add_to_db=bool
):
    """Parses a result of a blast query

    Return top k matches and adds them to the database.
    """

    print(f"Parsing {file_name} at {path}")
    i = 0
    results = list()
    for bresults in SearchIO.parse(path, 'blast-xml'):
        for r in bresults:
            i += 1
            # Select only top k
            if i <= top_k:
                results.append({
                    "rank": i,
                    "id": r.id,
                    "query_id": r.query_id,
                    "full_name": r.description_all,
                    "bitscore": r.hsps[0].bitscore,
                    "evalue": r.hsps[0].bitscore,
                    "query_range": r.hsps[0].query_range,
                    "hit_range": r.hsps[0].hit_range,
                })
            elif i > top_k and add_to_db is True:
                print("Top 3 results saved to database")
                add_to_database(
                    results=results,
                    FA_FILES_PATH=FA_FILES_PATH)
                break
            else:
                return(results)
