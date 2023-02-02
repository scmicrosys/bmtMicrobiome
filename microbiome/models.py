# models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Date
from sqlalchemy.sql.sqltypes import Float, Integer

Base = declarative_base()


class Record(Base):
    """Record class of xml and fa files.

    This is the main and only class for the records that
    will be inserted into the database.
    """
    __tablename__ = 'records'

    # Info on record
    auto_id = Column(Integer, primary_key=True)
    created = Column(Date)

    # Info on match
    id = Column(String)
    full_name = Column(String)
    bitscore = Column(Float)
    evalue = Column(Float)
    order_match = Column(String)
    query_range = Column(String)
    hit_range = Column(String)

    # Files
    smbl_xml = Column(String)
    fasta = Column(String)
