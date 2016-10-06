# pandas-linker

`pandas-linker` runs comparison windows over different sortings of a pandas DataFrame and links the rows via assigned UUIDs. This library does not actually do any duplicate detection. Instead it provides a harness to run your own comparison functions on your data.

This library is meant for datasets of a size where comparing every row with every other is undesirable. Instead you can decide on a sorting order of the DataFrame and only compare every row with every other inside a sliding window.

## Install

```
pip install pandas-linker
```

## Example

Let's say you have a DataFrame like this:

 [ix] | name | country
------|------|--------
   0  | Pete | Spain
   1  | Mary | USA
   2  | Bart | US
   3  | Mary | US

and you want to detect similar rows and mark them as such. Here's how to do that:

```python
from pandas_linker import get_linker


def compare_rows(a, b):
    ''' Example function that decides if two rows represent same entity.'''
    return a['name'] in b['name'] or b['name'] in a['name']

# df is a pandas.DataFrame with a unique index

with get_linker(df, field='uid') as linker:

    print('Comparing in 10 row window sorted by name')
    linker(sort_cols=['name'], window_size=10, cmp=compare_rows)

    print('Comparing in 15 row window sorted by country')
    linker(sort_cols=['country'], window_size=15, cmp=compare_rows)

```

After running the linker the process is complete

 [ix] | name | country | uid
------|------|---------|----
   0  | Pete | Spain   | 7509781940fc471cad5dc32944652d70
   1  | Mary | USA     | 8f8dccd91568472daf740e9160349d6c
   2  | Bart | US      | 12b55fbe80f64d378193acd727b0e051
   3  | Mary | US      | 8f8dccd91568472daf740e9160349d6c

Note that both "Mary" rows in the DataFrame have been identified as representing
the same entity and were assigned the same UUID.
