# NewsAPI Python Client

## Description

This project provides a Python client for accessing the NewsAPI. It aims to make it easier for developers to integrate news searching capabilities into their applications. Whether you are building a news aggregation service, a stock trading platform that needs financial news, or a social media app that needs to show relevant news to users, this library is for you.

## Features

- Simple and intuitive Python interface to the NewsAPI.
- Uses the `requests` library for making HTTP requests.
- Object-oriented models for request and response data.
- Supports all parameters of the NewsAPI, including advanced search queries and filtering.
- Built with flexibility and extensibility in mind, allowing developers to customize it according to their needs.

## Installation

```bash
pip install newsapi-python-client
```

## Usage

```python
from services.news_service import get_finance_news
from models.request_model import RequestModel

request_model = RequestModel(
    q='finance',
    searchIn='title,content',
    sources='source1,source2',
    domains='domain1.com,domain2.com',
    excludeDomains='excludedomain1.com,excludedomain2.com',
    from_param='2023-05-01T00:00:00',
    to='2023-05-27T23:59:59',
    language='en',
    sortBy='popularity',
    pageSize=100,
    page=1
)

response_model = get_finance_news(request_model)

for article in response_model.articles:
    print(f"Title: {article.title}")
    print(f"URL: {article.url}")
    print("---")
```

Note: Remember to replace placeholder values in the `RequestModel` with actual values.

## Requirements

- Python 3.6 or later
- `requests` package

## Future Plans

- Improve error handling and validation.
- Add more examples and use cases.
- Create more comprehensive documentation.

## Contributing

We welcome contributions from the community. Please refer to the CONTRIBUTING.md file for more details.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
