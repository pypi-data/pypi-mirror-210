import os
import sqlite3

from firepit.schemas import COLUMNS_SCHEMA
from firepit.schemas import CONTAINS_SCHEMA
from firepit.schemas import IDENTITY_SCHEMA
from firepit.schemas import INTERNAL_SCHEMAS
from firepit.schemas import METADATA_SCHEMA
from firepit.schemas import OBSERVED_DATA_SCHEMA
from firepit.schemas import QUERIES_SCHEMA
from firepit.schemas import SYMTABLE_SCHEMA


def test_create_columns():
    assert COLUMNS_SCHEMA.create_stmt('FOO') == ('CREATE FOO TABLE IF NOT EXISTS "__columns" '
                                                 '(otype TEXT, path TEXT, shortname TEXT, dtype TEXT,'
                                                 ' UNIQUE(otype, path))')


def test_create_contains():
    assert CONTAINS_SCHEMA.create_stmt() == ('CREATE TABLE IF NOT EXISTS "__contains" '
                                             '(source_ref TEXT, target_ref TEXT, x_firepit_rank INTEGER,'
                                             ' UNIQUE(source_ref, target_ref) ON CONFLICT IGNORE)')


def test_create_metadata():
    assert METADATA_SCHEMA.create_stmt() == ('CREATE TABLE IF NOT EXISTS "__metadata" '
                                             '(name TEXT, value TEXT)')


def test_create_queries():
    assert QUERIES_SCHEMA.create_stmt() == ('CREATE TABLE IF NOT EXISTS "__queries" '
                                             '(sco_id TEXT, query_id TEXT)')


def test_create_symtable():
    assert SYMTABLE_SCHEMA.create_stmt() == ('CREATE TABLE IF NOT EXISTS "__symtable" '
                                             '(name TEXT, type TEXT, appdata TEXT,'
                                             ' UNIQUE(name))')


def test_create_id():
    ID_TABLE = ('CREATE UNLOGGED TABLE IF NOT EXISTS "identity" '
                '(id TEXT UNIQUE,'
                ' identity_class TEXT,'
                ' name TEXT,'
                ' created TEXT,'
                ' modified TEXT'
                ')')
    assert IDENTITY_SCHEMA.create_stmt(mod='UNLOGGED') == ID_TABLE


def test_create_od():
    OD_TABLE = ('CREATE TABLE IF NOT EXISTS "observed-data" '
                '(id TEXT UNIQUE,'
                ' created_by_ref TEXT,'
                ' created TEXT,'
                ' modified TEXT,'
                ' first_observed TEXT,'
                ' last_observed TEXT,'
                ' number_observed INTEGER'
                ')')
    type_map = {'BIGINT': 'INTEGER'}
    assert OBSERVED_DATA_SCHEMA.create_stmt(type_map=type_map) == OD_TABLE


def test_create_all_tables():
    # Make sure our generate SQL is accepted by sqlite3, at least
    type_map = {'BIGINT': 'INTEGER'}
    try:
        os.remove('test_create_schema.db')
    except FileNotFoundError:
        pass
    conn = sqlite3.connect('test_create_schema.db')
    cursor = conn.cursor()
    for schema in INTERNAL_SCHEMAS:
        stmt = schema.create_stmt(type_map=type_map)
        cursor.execute(stmt)
    cursor.close()
    conn.commit()
    conn.close()
    os.remove('test_create_schema.db')
