# playwright-python-pytest-async

This repository is example implementation of test for pytest-playwright async api. Currently the pytest-playwright plugin doesn't provide async APIs, so we need to  implement like official repository does.

* https://github.com/microsoft/playwright-pytest/issues/74#issuecomment-916001720

You need to implement ``authenticate`` method in ``tests/conftest.py``.

```shell
$ pytest --asyncio-mode=auto
```