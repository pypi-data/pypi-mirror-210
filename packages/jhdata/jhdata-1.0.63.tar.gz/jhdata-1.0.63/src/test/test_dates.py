from src.main.dates import *


def test_timestamp_to_epoch():
    assert timestamp_to_epoch("19700101_000000") == 0
