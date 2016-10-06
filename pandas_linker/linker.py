from collections import deque
from contextlib import contextmanager
from functools import partial
import itertools
import uuid

import pyprind


DEFAULT_MATCH_FIELD = 'uid'


def none_func(a, b):
    return None


@contextmanager
def get_linker(df, field=DEFAULT_MATCH_FIELD, **kwargs):
    df[field] = None
    yield partial(run_linker, df, field=field, **kwargs)
    df[field] = df[field].apply(lambda x: x if x else str(uuid.uuid4()))


def run_linker(df, sort_cols=None, **kwargs):
    if not df.index.is_unique:
        raise ValueError('Index of dataframe is not unique')

    rolling_df = df
    if sort_cols is not None:
        rolling_df = rolling_df.sort_values(sort_cols)

    match_field = kwargs.pop('field', DEFAULT_MATCH_FIELD)
    kwargs.setdefault('match', make_same_marker(df, field=match_field))
    kwargs.setdefault('size', len(df))

    iterator = rolling_df.iterrows()
    return compare_window(iterator, **kwargs)


def window(seq, size=2):
    if size < 1:
        raise ValueError('Bad value for window size')

    it = iter(seq)
    win = deque((next(it) for _ in range(size)), maxlen=size)
    if len(win) < size:
        raise ValueError('Sequence smaller than window')
    yield win
    for e in it:
        win.append(e)
        yield win


def compare_window(seq, window_size=2, cmp=none_func, size=None,
                   match=none_func, progress=True):
    if progress:
        progress = pyprind.ProgPercent(size)

    def cmp_seq(win, cmp):
        first = win[0]
        for item in itertools.islice(win, 1, None):
            if cmp(first[1], item[1]):
                match(first[0], item[0])

    for win in window(seq, size=window_size):
        cmp_seq(win, cmp)
        try:
            if progress:
                progress.update()
        except ValueError:
            pass

    while len(win) > 2:
        win.popleft()
        cmp_seq(win, cmp)


def mark_same(df, ia, ib, field=DEFAULT_MATCH_FIELD):
    a = df.ix[ia][field]
    b = df.ix[ib][field]
    if a and not b:
        df.set_value(ib, field, a)
    elif not a and b:
        df.set_value(ia, field, b)
    elif a and b and a != b:
        df.loc[df[field] == b, field] = a
    elif not a and not b:
        uid = str(uuid.uuid4())
        df.set_value(ia, field, uid)
        df.set_value(ib, field, uid)


def make_same_marker(df, field=DEFAULT_MATCH_FIELD):
    return partial(mark_same, df, field=field)
