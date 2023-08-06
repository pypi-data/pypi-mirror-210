# Klu.AI Python SDK

[![pypi](https://img.shields.io/pypi/v/klu.svg)](https://pypi.org/project/klu/)
[![python](https://img.shields.io/pypi/pyversions/klu.svg)](https://pypi.org/project/klu/)
[![Build Status](https://github.com/klu-ai/klu-sdk/actions/workflows/dev.yml/badge.svg)](https://github.com/klu-ai/klu-sdk/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/klu-ai/klu-sdk/branch/main/graphs/badge.svg)](https://codecov.io/github/klu-ai/klu-sdk)

## Description

SDK for building AI Enabled apps

-   Documentation: <https://docs.klu.ai>
-   GitHub: <https://github.com/klu-ai/klu-sdk>
-   PyPI: <https://pypi.org/project/klu/>
-   Free software: MIT

The Klu.AI Python SDK is a library that provides access to the Klu.AI API, allowing users to interact with their workspace, applications, actions, data, models, and data indices.

## Requirements

The Klu.AI Python SDK requires Python version 3.7 or later.

## Installation

To install the Klu.AI Python SDK, simply run:

```
pip install klu
```

## Getting Started

To use the Klu.AI Python SDK, you must first obtain an API key from the Klu.AI website. Once you have your API key, you can create a `KluClient` object:

```python
from klu import KluClient

client = KluClient("YOUR_API_KEY")
```

Once you have a `KluClient` object, you can access the different models available in the Klu API:

```python
from klu import KluClient

client = KluClient("YOUR_API_KEY")
models = await client.models.get("model_guid")

```

There is also a separate function to stream action prompt

Each of these objects provides methods for interacting with the corresponding model in the Klu API. For example, to list all applications in your workspace, you can use:

```python
from klu import KluClient

client = KluClient("YOUR_API_KEY")
applications = client.applications.list()
```

In a similar manner, in order to get a list of data points for an action, you can do the following

```python
from klu import KluClient

client = KluClient("YOUR_API_KEY")
data = client.data.get_action_data("action_id")
```

There is a special client that allows to stream action prompts.
The streaming url can be received from the action creation response.

```python
from klu import KluClient

client = KluClient("YOUR_API_KEY")

prompt_response = await client.actions.run_action_prompt("action_guid", "prompt", streaming=True)
async for message in client.sse_client.get_streaming_data(prompt_response.streaming_url):
    print(message)
```

## Documentation
For more detailed information on how to use the Klu.AI Python SDK, please refer to the [API documentation](https://docs.klu.ai/).

## Credits
This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.
