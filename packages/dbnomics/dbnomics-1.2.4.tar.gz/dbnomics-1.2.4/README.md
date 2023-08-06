# DBnomics Python client

Download time series from DBnomics and access it as a [Pandas](https://pandas.pydata.org/) DataFrame.

This package is compatible with Python >= 3.8. (TODO vermin)

## Documentation

### Quick start

### Tutorial

A tutorial showing how to download series as a DataFrame and plot them is available as a [notebook](https://git.nomics.world/dbnomics/dbnomics-python-client/-/blob/master/index.ipynb).

## Install

```bash
pip install dbnomics
```

See also: <https://pypi.org/project/DBnomics/>

## Configuration

### Use with a proxy

This Python package uses [requests](https://requests.readthedocs.io/), which is able to work with a proxy (HTTP/HTTPS, SOCKS). For more information, please check [its documentation](https://requests.readthedocs.io/en/master/user/advanced/#proxies).

### Customize the API base URL

If you plan to use a local Web API, running on the port 5000, you'll need to use the `api_base_url` parameter of the `fetch_*` functions, like this:

```python
df = fetch_series(
    api_base_url='http://localhost:5000',
    provider_code='AMECO',
    dataset_code='ZUTN',
)
```

Or globally change the default API URL used by the `dbnomics` module, like this:

```python
import dbnomics
dbnomics.default_api_base_url = "http://localhost:5000"
```

## Development

To work on dbnomics-python-client source code:

```bash
git clone https://git.nomics.world/dbnomics/dbnomics-python-client.git
cd dbnomics-python-client
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### Open the demo notebook

Install jupyter if not already done, in a virtualenv:

```bash
pip install jupyter
jupyter notebook index.ipynb
```

## Tests

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -e .

pytest

# Specify an alternate API URL
API_URL=http://localhost:5000 pytest
```
