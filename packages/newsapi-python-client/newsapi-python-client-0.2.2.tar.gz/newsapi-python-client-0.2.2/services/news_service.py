import os
import json
import requests
from models.request_model import RequestModel
from models.response_model import ResponseModel

# Get the absolute path of the secrets.json file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_PATH = os.path.join(BASE_DIR, 'secrets.json')


def get_finance_news(request_model: RequestModel) -> ResponseModel:
    """
    Fetches finance news from the News API based on the parameters provided in the request model.

    Args:
        request_model (RequestModel): The parameters for the News API request.

    Returns:
        ResponseModel: The response from the News API.
    """
    with open(SECRETS_PATH) as f:
        secrets = json.load(f)

    API_KEY = secrets['NEWS_API_KEY']

    response = requests.get(
        'https://newsapi.org/v2/everything',
        headers={'X-Api-Key': API_KEY},
        params=request_model.to_dict()
    )

    response.raise_for_status()

    return ResponseModel.from_dict(response.json())