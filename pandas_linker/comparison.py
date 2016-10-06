"""
Example string comparison functions
"""
import pandas as pd

import difflib


def fuzzy_string_compare(a, b, threshold=0.9):
    if pd.isnull(a) or pd.isnull(b):
        return False
    sm = difflib.SequenceMatcher(None, a, b)
    return sm.ratio() >= threshold


def one_contains_other(a, b):
    if pd.isnull(a) or pd.isnull(b):
        return False
    a = a.lower()
    b = b.lower()
    return a in b or b in a
