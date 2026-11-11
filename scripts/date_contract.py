"""Shared persisted-year and published-work admission contract."""
import datetime
import json
from pathlib import Path
CONTRACT = json.loads((Path(__file__).resolve().parents[1] / 'data/date-contract.json').read_text())


def is_recorded_year(year):
    return year is None or type(year) is int and CONTRACT['minimumYear'] <= year <= CONTRACT['maximumYear']


def is_published_year(year, current_year=None):
    return year is not None and is_recorded_year(year) and year <= (current_year or datetime.date.today().year)
