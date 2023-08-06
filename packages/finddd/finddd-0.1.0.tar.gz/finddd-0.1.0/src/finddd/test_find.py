from finddd.find import *
from finddd.match import FT_DIRECTORY, FT_FILE


def test_finder():
    fder = Finder()

    files = fder.find(
        r".",
        filetypes=[FT_DIRECTORY],
    )
    print(files)
