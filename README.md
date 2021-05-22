# RDClient
[![Build Status](https://travis-ci.org/rtician/rd_client.svg?branch=main)](https://travis-ci.org/rtician/rd_client)
[![codecov](https://codecov.io/gh/rtician/rd_client/branch/main/graph/badge.svg)](https://codecov.io/gh/rtician/rd_client)

Client helper to use RDStation API

### How can I install it?
```
$ pip install rd_client
```

### How to use it?
```python
In [1]: from rd_client import RDClient

In [2]: client = RDClient('client_id', 'client_secret', 'https://foo.bar')
In [3]: client.authorize()
In [4]: client.get('/marketing/account_info')
Out[4]: 
{'name': 'Account Name'}
In [5]: 

```

### Contribute
Poetry it's an easy way no manage dependencies and build a package, you can see more [here](https://python-poetry.org/).

Download the project and install the dependencies

```bash
$ git clone https://github.com/rtician/rd_client
$ cd rd_client
$ poetry install
```

Run the tests
```bash
$ poetry run py.test --cov-report term --cov=rd_client
```
