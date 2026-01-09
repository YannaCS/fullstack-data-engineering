import pytest
from app.services import WeatherService
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.external_api import WeatherAPIClient

class TestWeatherService():
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)
    
    @pytest.fixture
    def mock_api_client(self):
        return MagicMock(spec=WeatherAPIClient)

    @pytest.fixture
    def service(self, mock_db, mock_api_client):
        # db = self.mock_db()
        # api_client = self.mock_api_client()
        return WeatherService(mock_db, mock_api_client)
    

    def test_get_weather(self, service, mock_db, mock_api_client):
        # arrange
        mock_api_client.get_current_weather.return_value = {
            "name": "Tokyo",
            "main": {"temp": 8.0, "humidity": 70},
            "weather": [{"description": 'clear'}]
        }
        mock_api_client.parse_weather_data.return_value = {
            "temperature": 8.0,
            "description": 'clear',
            "humidity": 70,
            "city": 'Tokyo'
        }
        
        # Action
        result = service.get_weather('Tokyo')
        
        # assert
        assert result['city'] == 'Tokyo'
        assert result['temperature'] == 8.0
        
        mock_api_client.get_current_weather.assert_called_once_with('Tokyo')
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        
        
        