
from abc import abstractmethod
from dataclasses import dataclass, field, fields

@dataclass
class RequestModel:
    """
    A data class that represents the request parameters for News API.

    Attributes:
        q (str): Keywords or phrases to search for in the article title and body.
        searchIn (str): The fields to restrict your `q` search to.
        sources (str): A comma-separated string of identifiers for the news sources or blogs you want headlines from.
        domains (str): A comma-separated string of domains to restrict the search to.
        excludeDomains (str): A comma-separated string of domains to remove from the results.
        from_param (str): A date and optional time for the oldest article allowed. This should be in ISO 8601 format.
        to (str): A date and optional time for the newest article allowed. This should be in ISO 8601 format.
        language (str): The 2-letter ISO-639-1 code of the language you want to get headlines for.
        sortBy (str): The order to sort the articles in. Possible options: relevancy, popularity, publishedAt.
        pageSize (int): The number of results to return per page.
        page (int): Use this to page through the results.
    """

    @abstractmethod
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}



@dataclass
class EverythingRequestModel(RequestModel):
    q: str = None
    searchIn: str = None
    sources: str = None
    domains: str = None
    excludeDomains: str = None
    from_param: str = field(default=None, metadata={'name': 'from'})
    to: str = None
    language: str = None
    sortBy: str = None
    pageSize: int = None
    page: int = None

    def to_dict(self):
        return {f.metadata.get('name', f.name): getattr(self, f.name) 
                for f in fields(self) 
                if getattr(self, f.name) is not None}


@dataclass
class TopHeadlinesRequestModel(RequestModel):
    country: str = None
    category: str = None
    sources: str = None
    q: str = None
    pageSize: int = None
    page: int = None

    def to_dict(self):
        return {f.metadata.get('name', f.name): getattr(self, f.name) 
                for f in fields(self) 
                if getattr(self, f.name) is not None}


from enum import Enum

class Country(Enum):
    UNITED_ARAB_EMIRATES = "ae"
    ARGENTINA = "ar"
    AUSTRIA = "at"
    AUSTRALIA = "au"
    BELGIUM = "be"
    BULGARIA = "bg"
    BRAZIL = "br"
    CANADA = "ca"
    SWITZERLAND = "ch"
    CHINA = "cn"
    COLOMBIA = "co"
    CUBA = "cu"
    CZECH_REPUBLIC = "cz"
    GERMANY = "de"
    EGYPT = "eg"
    FRANCE = "fr"
    UNITED_KINGDOM = "gb"
    GREECE = "gr"
    HONG_KONG = "hk"
    HUNGARY = "hu"
    INDONESIA = "id"
    IRELAND = "ie"
    ISRAEL = "il"
    INDIA = "in"
    ITALY = "it"
    JAPAN = "jp"
    SOUTH_KOREA = "kr"
    LITHUANIA = "lt"
    LATVIA = "lv"
    MOROCCO = "ma"
    MEXICO = "mx"
    MALAYSIA = "my"
    NIGERIA = "ng"
    NETHERLANDS = "nl"
    NORWAY = "no"
    NEW_ZEALAND = "nz"
    PHILIPPINES = "ph"
    POLAND = "pl"
    PORTUGAL = "pt"
    ROMANIA = "ro"
    SERBIA = "rs"
    RUSSIA = "ru"
    SAUDI_ARABIA = "sa"
    SWEDEN = "se"
    SINGAPORE = "sg"
    SLOVENIA = "si"
    SLOVAKIA = "sk"
    THAILAND = "th"
    TURKEY = "tr"
    TAIWAN = "tw"
    UKRAINE = "ua"
    UNITED_STATES = "us"
    VENEZUELA = "ve"
    SOUTH_AFRICA = "za"

from enum import Enum

class Language(Enum):
    AR = "ar"
    DE = "de"
    EN = "en"
    ES = "es"
    FR = "fr"
    HE = "he"
    IT = "it"
    NL = "nl"
    NO = "no"
    PT = "pt"
    RU = "ru"
    SV = "sv"
    UD = "ud"
    ZH = "zh"

class Category(Enum):
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    GENERAL = "general"
    HEALTH = "health"
    SCIENCE = "science"
    SPORTS = "sports"
    TECHNOLOGY = "technology"


@dataclass
class SourcesRequestModel(RequestModel):
    category: Category = None
    language: Language = None
    country: Country = None

    def to_dict(self):
        return {f.metadata.get('name', f.name): getattr(self, f.name) 
                for f in fields(self) 
                if getattr(self, f.name) is not None}
