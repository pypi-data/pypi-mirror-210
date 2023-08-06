import json
import pytest
import urllib3
from ..wtisdk import WtiClient
from unittest.mock import Mock

def test_get_status(mocker):
    # Load the mock response data from the JSON file
    with open('/wtisdk/tests/fixtures/wti_response.json', 'r') as file:
        mock_response_data = json.load(file)
    
    # Mock the requests library and the response object
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mocker.patch('requests.get', return_value=mock_response)
    
    # Create an instance of the WtiClient class
    client = WtiClient("10.60.47.139")
    
    # Call the get_status method
    result = client.get_status()