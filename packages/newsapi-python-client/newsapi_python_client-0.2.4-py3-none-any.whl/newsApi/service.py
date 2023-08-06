import requests
from models.request_model import RequestModel
from models.response_model import EverythingResponseModel, ResponseModel, TopHeadlinesResponseModel, SourcesResponseModel

class _NewsAPIClient:  # Single underscore indicates for internal use
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://newsapi.org/v2/'

    def make_request(self, endpoint: str, request_model: RequestModel, response_model_cls: type) -> 'ResponseModel':
        headers = {'X-Api-Key': self.api_key}
        response = requests.get(self.base_url + endpoint, headers=headers, params=request_model.to_dict())
        response.raise_for_status()
        return response_model_cls.from_dict(response.json())

class NewsAPIService:
    def __init__(self, api_key):
        self.client = _NewsAPIClient(api_key)  # Instantiate client within service class

    def everything(self, request_model: RequestModel) -> EverythingResponseModel:
        return self.client.make_request('everything', request_model, EverythingResponseModel)

    def top_headlines(self, request_model: RequestModel) -> TopHeadlinesResponseModel:
        return self.client.make_request('top-headlines', request_model, TopHeadlinesResponseModel)

    def sources(self, request_model: RequestModel) -> SourcesResponseModel:
        return self.client.make_request('sources', request_model, SourcesResponseModel)
