from dataclasses import dataclass

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
    q: str
    searchIn: str = 'title,content'
    sources: str = None
    domains: str = None
    excludeDomains: str = None
    from_param: str = None
    to: str = None
    language: str = 'en'
    sortBy: str = 'publishedAt'
    pageSize: int = 100
    page: int = 1

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}
