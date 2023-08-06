# FastAPI inferring Depends

[![PyPI version](https://badge.fury.io/py/fastapi-inferring-depends.svg)](https://badge.fury.io/py/fastapi-inferring-depends)
[![GitHub license](https://img.shields.io/github/license/jvllmr/fastapi-inferring-depends)](https://github.com/jvllmr/fastapi-inferring-depends/blob/master/LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dd/fastapi-inferring-depends)
![Tests](https://github.com/jvllmr/fastapi-inferring-depends/actions/workflows/test.yml/badge.svg)

A wrapper around FastAPI's Depends function that infers its return type from its input

## Example

```python
from fastapi_inferring_depends import Depends
from fastapi import FastAPI

router = FastAPI()


async def answer_to_everything_dependency():
    return 42


@app.get("/answer")
async def get_answer_to_everything(
    answer_to_everything=Depends(answer_to_everything_dependency),
):
    # type of answer_to_everything is 'int' (inferred from dependency)
    return {"answer": answer_to_everything}
```

For more examples, look at the test/example [file](https://github.com/jvllmr/fastapi-inferring-depends/blob/dev/test_example.py) for all supported inferences.
