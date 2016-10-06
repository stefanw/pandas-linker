import pytest
import pandas as pd

from pandas_linker.linker import window, get_linker
from pandas_linker.comparison import one_contains_other


def test_window():
    l = []
    with pytest.raises(ValueError):
        [list(x) for x in window(l, size=-1)]

    with pytest.raises(ValueError):
        [list(x) for x in window(l, size=0)]

    l = []
    with pytest.raises(ValueError):
        [list(x) for x in window(l, size=1)]

    l = []
    with pytest.raises(ValueError):
        [list(x) for x in window(l)]

    l = [1]
    with pytest.raises(ValueError):
        [list(x) for x in window(l)]

    l = [1, 2]
    assert [list(x) for x in window(l)] == [[1, 2]]

    l = [1, 2, 3, 4, 5]
    assert [list(x) for x in window(l)] == [[1, 2], [2, 3], [3, 4], [4, 5]]

    l = [1, 2, 3, 4, 5]
    window_list = [list(x) for x in window(l, size=3)]
    assert window_list == [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

    l = [1, 2, 3, 4, 5]
    window_list = [list(x) for x in window(l, size=1)]
    assert window_list == [[1], [2], [3], [4], [5]]


def test_linker():
    original = pd.DataFrame([
        {'name': 'Snowden', 'address': 'Hawai'},
        {'name': 'Manning', 'address': 'Hawbar, USA'},
        {'name': 'Angela Merkel', 'address': 'Germany'},
        {'name': 'Snowden, Edward', 'address': 'USA'},
        {'name': 'Manning, Chelsea', 'address': 'USA'}
    ])

    def cmp(a, b):
        return one_contains_other(a['name'], b['name'])

    df = original.copy()
    with get_linker(df, progress=False) as linker:
        linker(sort_cols=['address', 'name'], window_size=2, cmp=cmp)

    assert 'uid' in df.columns
    assert len(df.groupby('uid').size()) == 4
    assert len(df[df['name'].str.contains('Manning')].groupby('uid')) == 1
    assert len(df[df['name'].str.contains('Snowden')].groupby('uid')) == 2

    df = original.copy()
    with get_linker(df, progress=False) as linker:
        linker(sort_cols=['name'], window_size=2, cmp=cmp)

    assert 'uid' in df.columns
    assert len(df.groupby('uid').size()) == 3
    assert len(df[df['name'].str.contains('Manning')].groupby('uid')) == 1
    assert len(df[df['name'].str.contains('Snowden')].groupby('uid')) == 1

    df = original.copy()
    with get_linker(df, progress=False) as linker:
        linker(sort_cols=['address', 'name'], window_size=4, cmp=cmp)

    assert 'uid' in df.columns
    assert len(df.groupby('uid').size()) == 3
    assert len(df[df['name'].str.contains('Manning')].groupby('uid')) == 1
    assert len(df[df['name'].str.contains('Snowden')].groupby('uid')) == 1
