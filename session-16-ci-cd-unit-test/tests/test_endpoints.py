
import pytest
from fastapi.testclient import TestClient
from app.main import app, get_weather_service
from unittest.mock import MagicMock, patch
from app.services import WeatherService

class TestApiEndPoints():
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_service(self):
        return MagicMock(spec=WeatherService)
    
    
    def test_get_weather_point(self, client, mock_service):
        # arrange
        mock_service.get_weather.return_value = {
            "temperature": 8.0,
            "description": 'clear',
            "humidity": 70,
            "city": 'Tokyo'
        }
        
        app.dependency_overrides[get_weather_service] = lambda: mock_service
        
        # action
        response = client.get('/weather/Tokyo')
        
        # assert
        assert response.status_code == 200
        assert response.json()['city'] == 'Tokyo'
        
        mock_service.get_weather.assert_called_once_with("Tokyo")
        
        app.dependency_overrides.clear()
        
        