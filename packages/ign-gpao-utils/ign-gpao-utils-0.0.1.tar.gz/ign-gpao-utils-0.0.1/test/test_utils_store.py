
from gpao_utils import utils_store

store = utils_store.Store("K:/", "//store.ign.fr/store-lidarhd/", "/var/data/store-lidarhd/")

def test_to_unix():
    assert store.to_unix("K:/toto.txt") == "/var/data/store-lidarhd/toto.txt"

def test_replace_lettre():
    assert store.replace_letter("K:/toto.txt") == "//store.ign.fr/store-lidarhd/toto.txt"

def test_to_win():
    assert store.to_win("") == ""
    assert store.to_win("/var/data/store-lidarhd/toto.txt") == "//store.ign.fr/store-lidarhd/toto.txt"
