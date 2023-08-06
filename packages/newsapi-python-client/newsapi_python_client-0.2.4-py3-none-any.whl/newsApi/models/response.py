from typing import List, Optional
import dataclasses


@dataclasses.dataclass
class Source:
    id: str
    name: str


@dataclasses.dataclass
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
    def from_dict(cls, data: dict) -> "Article":
        return cls(
            source=Source(**data.get("source", {})),
            author=data.get("author"),
            title=data.get("title"),
            description=data.get("description"),
            url=data.get("url"),
            urlToImage=data.get("urlToImage"),
            publishedAt=data.get("publishedAt"),
            content=data.get("content"),
        )


@dataclasses.dataclass
class TopHeadlinesResponseModel:
    status: str
    totalResults: int
    articles: List[Article]

    @classmethod
    def from_dict(cls, data: dict) -> "TopHeadlinesResponseModel":
        articles = [Article.from_dict(article) for article in data.get("articles", [])]
        return cls(
            status=data.get("status", ""),
            totalResults=data.get("totalResults", 0),
            articles=articles,
        )


@dataclasses.dataclass
class ResponseModel:
    status: str

    @classmethod
    def from_dict(cls, data: dict) -> "ResponseModel":
        raise NotImplementedError()


@dataclasses.dataclass
class EverythingResponseModel(ResponseModel):
    totalResults: int
    articles: List[Article]

    @classmethod
    def from_dict(cls, data: dict) -> "EverythingResponseModel":
        articles = [Article.from_dict(article) for article in data["articles"]]
        return cls(
            status=data["status"], totalResults=data["totalResults"], articles=articles
        )


@dataclasses.dataclass
class SourcesResponseModel(ResponseModel):
    sources: List[Source]

    @classmethod
    def from_dict(cls, data: dict) -> "SourcesResponseModel":
        sources = [Source(**source) for source in data.get("sources", [])]
        return cls(
            status=data["status"],
            sources=sources,
        )
