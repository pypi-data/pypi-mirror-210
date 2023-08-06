# pshlib

Causal embedding of shell commands into python code.

## Example

You can break single long bash lines into nested python like multi-line statements:

```python
    res = psh(
    'VAR=world',
    """
        echo This is
            a multiline hello
            $VAR!
    """,
    ).output
    print(res)
    excepted = 'This is a multiline hello world!\n'
    assert excepted == res
```

## Installation

with pip:

    pip install pshlib

with poetry:

    poetry add git+https://gitlab.com:ewiger/pshlib.git

## License

Licensed under MIT. See LICENSE for details.


## Publish

    poetry publish --build
