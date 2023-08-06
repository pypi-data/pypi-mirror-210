from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Source:
    id: Optional[str]
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Source':
        return cls(id=data.get('id'), name=data['name'])

@dataclass
class Article:
    source: Source
    author: Optional[str]
    title: str
    description: Optional[str]
    url: str
    urlToImage: Optional[str]
    publishedAt: str
    content: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        source = Source.from_dict(data['source'])
        return cls(
            source=source,
            author=data.get('author'),
            title=data['title'],
            description=data.get('description'),
            url=data['url'],
            urlToImage=data.get('urlToImage'),
            publishedAt=data['publishedAt'],
            content=data.get('content')
        )


@dataclass
class ResponseModel:
    """
    A data class that represents the response from News API.

    Attributes:
        - status (str): If the request was successful or not. Options: ok, error.
        - totalResults (int): The total number of results available for your request.
        - articles (List[Article]): The results of the request.
    """
    status: str
    totalResults: int
    articles: List[Article]

    @classmethod
    def from_dict(cls, data: dict) -> 'ResponseModel':
        articles = [Article.from_dict(article) for article in data['articles']]
        return cls(
            status=data['status'],
            totalResults=data['totalResults'],
            articles=articles
        )
