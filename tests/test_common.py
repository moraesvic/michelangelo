import os, sys, re

NUMBER_OF_TESTS = 50
VERBOSE = any([re.search(r"-v", arg) for arg in sys.argv])

def printv(s: str):
    """Prints string s if running in verbosity mode"""
    if VERBOSE:
        print(s)

def rel_path(path):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_dir, path)