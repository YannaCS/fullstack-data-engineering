import pytest
from app.external_api import WeatherAPIClient
from unittest.mock import MagicMock, patch


class TestWeatherApi():
    
    @pytest.fixture
    def api_client(self):
        return WeatherAPIClient(api_key="apikey")
    
    @patch('app.external_api.requests.get')
    def test_get_current_weather(self, mock_get, api_client):
        #arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "Tokyo",
            "main": {"temp": 8.0, "humidity": 70},
            "weather": [{"description": 'clear'}]
        }
        
        mock_get.return_value = mock_response
        
        # action
        result = api_client.get_current_weather('Tokyo')
        
        assert result["name"] == "Tokyo"
        assert result["main"]["temp"] == 8.0
        
        mock_get.assert_called_once()
        
        