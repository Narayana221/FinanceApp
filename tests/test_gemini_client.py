"""
Tests for Gemini API client (utils/gemini_client.py).

This module tests the GeminiClient class including API integration,
authentication, error handling, retry logic, and timeout behavior.
"""

import pytest
import os
from unittest.mock import patch, Mock, MagicMock
import requests
from utils.gemini_client import GeminiClient


class TestGeminiClientInitialization:
    """Test GeminiClient initialization and configuration."""
    
    def test_init_with_valid_api_key(self):
        """Test client initializes successfully with valid API key."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key-123'}):
            client = GeminiClient()
            assert client.api_key == 'test-api-key-123'
            assert client.is_configured() == True
    
    @patch('utils.gemini_client.load_dotenv')
    def test_init_with_missing_api_key(self, mock_load_dotenv):
        """Test client initializes with None when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            client = GeminiClient()
            assert client.api_key is None
            assert client.is_configured() == False
    
    def test_init_with_empty_api_key(self):
        """Test client treats empty string API key as not configured."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': '   '}):
            client = GeminiClient()
            assert client.is_configured() == False
    
    def test_api_endpoint_configuration(self):
        """Test API endpoint URL is correctly configured."""
        client = GeminiClient()
        assert client.API_ENDPOINT == "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    def test_timeout_configuration(self):
        """Test timeout is set to 15 seconds (NFR-PERF-002)."""
        client = GeminiClient()
        assert client.TIMEOUT == 15
    
    def test_retry_configuration(self):
        """Test retry configuration is correct."""
        client = GeminiClient()
        assert client.MAX_RETRIES == 1
        assert client.RETRY_DELAY == 2


class TestGenerateFinancialAdvice:
    """Test generate_financial_advice method."""
    
    @patch('utils.gemini_client.requests.post')
    def test_successful_advice_generation(self, mock_post):
        """Test successful advice generation with valid API response."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Test financial advice'
                    }]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Analyze my spending")
        
        # Verify
        assert result['success'] == True
        assert result['advice'] == 'Test financial advice'
        assert 'error' not in result
    
    @patch('utils.gemini_client.load_dotenv')
    def test_missing_api_key_error(self, mock_load_dotenv):
        """Test error when API key is not configured."""
        with patch.dict(os.environ, {}, clear=True):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        assert result['success'] == False
        assert result['error'] == 'AI Coach unavailable. Please configure API key.'
        assert 'advice' not in result
    
    def test_empty_api_key_error(self):
        """Test error when API key is empty string."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': '   '}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        assert result['success'] == False
        assert result['error'] == 'AI Coach unavailable. Please configure API key.'
    
    @patch('utils.gemini_client.requests.post')
    def test_timeout_error_handling(self, mock_post):
        """Test timeout error returns appropriate message."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        assert result['success'] == False
        assert result['error'] == 'AI Coach taking longer than expected. Using basic analysis.'
    
    @patch('utils.gemini_client.requests.post')
    def test_rate_limit_error_handling(self, mock_post):
        """Test HTTP 429 rate limit error returns appropriate message."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_post.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        assert result['success'] == False
        assert result['error'] == 'AI Coach busy. Please try again in a moment.'
    
    @patch('utils.gemini_client.requests.post')
    def test_authentication_error_401(self, mock_post):
        """Test HTTP 401 auth error returns appropriate message."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'invalid-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        assert result['success'] == False
        assert result['error'] == 'AI Coach unavailable. Please configure API key.'
    
    @patch('utils.gemini_client.requests.post')
    def test_authentication_error_403(self, mock_post):
        """Test HTTP 403 auth error returns appropriate message."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_post.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'invalid-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        assert result['success'] == False
        assert result['error'] == 'AI Coach unavailable. Please configure API key.'
    
    @patch('utils.gemini_client.requests.post')
    def test_connection_error_handling(self, mock_post):
        """Test connection error returns appropriate message."""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        assert result['success'] == False
        assert result['error'] == 'AI Coach unavailable. Please check connection.'


class TestMakeRequest:
    """Test _make_request method with retry logic."""
    
    @patch('utils.gemini_client.requests.post')
    def test_request_payload_structure(self, mock_post):
        """Test request payload has correct structure."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'advice'}]}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            client.generate_financial_advice("Test prompt")
        
        # Verify request was called with correct structure
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs['json']
        
        assert 'contents' in payload
        assert len(payload['contents']) == 1
        assert 'parts' in payload['contents'][0]
        assert 'text' in payload['contents'][0]['parts'][0]
        assert 'generationConfig' in payload
        assert payload['generationConfig']['temperature'] == 0.7
        assert payload['generationConfig']['maxOutputTokens'] == 4096
    
    @patch('utils.gemini_client.requests.post')
    def test_api_key_in_url(self, mock_post):
        """Test API key is added as query parameter in URL."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'advice'}]}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'my-secret-key'}):
            client = GeminiClient()
            client.generate_financial_advice("Test prompt")
        
        # Verify URL contains API key
        call_args = mock_post.call_args[0]
        url = call_args[0]
        assert '?key=my-secret-key' in url
    
    @patch('utils.gemini_client.requests.post')
    def test_request_headers(self, mock_post):
        """Test request includes correct headers."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'advice'}]}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            client.generate_financial_advice("Test prompt")
        
        # Verify headers
        call_kwargs = mock_post.call_args[1]
        headers = call_kwargs['headers']
        assert headers['Content-Type'] == 'application/json'
    
    @patch('utils.gemini_client.requests.post')
    def test_timeout_configuration(self, mock_post):
        """Test request uses 15-second timeout."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'advice'}]}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            client.generate_financial_advice("Test prompt")
        
        # Verify timeout parameter
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['timeout'] == 15
    
    @patch('utils.gemini_client.time.sleep')
    @patch('utils.gemini_client.requests.post')
    def test_retry_on_network_error(self, mock_post, mock_sleep):
        """Test retry logic on network error."""
        # First call fails, second succeeds
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'advice'}]}}]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [
            requests.exceptions.RequestException("Network error"),
            mock_response
        ]
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        # Verify retry happened
        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1
        assert mock_sleep.call_args[0][0] == 2  # 2-second delay
        assert result['success'] == True
    
    @patch('utils.gemini_client.time.sleep')
    @patch('utils.gemini_client.requests.post')
    def test_no_retry_on_timeout(self, mock_post, mock_sleep):
        """Test no retry on timeout error."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        # Verify no retry for timeout
        assert mock_post.call_count == 1
        assert mock_sleep.call_count == 0
        assert result['success'] == False
    
    @patch('utils.gemini_client.time.sleep')
    @patch('utils.gemini_client.requests.post')
    def test_max_retries_exhausted(self, mock_post, mock_sleep):
        """Test error after max retries exhausted."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test prompt")
        
        # Verify all retries attempted
        assert mock_post.call_count == 2  # Initial + 1 retry
        assert mock_sleep.call_count == 1
        assert result['success'] == False


class TestParseResponse:
    """Test _parse_response method."""
    
    @patch('utils.gemini_client.requests.post')
    def test_parse_valid_response(self, mock_post):
        """Test parsing valid API response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': '  Financial advice with spaces  '
                    }]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test")
        
        # Verify text is stripped
        assert result['advice'] == 'Financial advice with spaces'
    
    @patch('utils.gemini_client.requests.post')
    def test_parse_response_missing_candidates(self, mock_post):
        """Test error handling for missing candidates key."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test")
        
        assert result['success'] == False
        assert 'Using basic analysis' in result['error']
    
    @patch('utils.gemini_client.requests.post')
    def test_parse_response_missing_content(self, mock_post):
        """Test error handling for missing content key."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            result = client.generate_financial_advice("Test")
        
        assert result['success'] == False
        assert 'Using basic analysis' in result['error']


class TestIsConfigured:
    """Test is_configured method."""
    
    def test_is_configured_with_valid_key(self):
        """Test is_configured returns True with valid API key."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient()
            assert client.is_configured() == True
    
    @patch('utils.gemini_client.load_dotenv')
    def test_is_configured_with_missing_key(self, mock_load_dotenv):
        """Test is_configured returns False with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            client = GeminiClient()
            assert client.is_configured() == False
    
    def test_is_configured_with_empty_key(self):
        """Test is_configured returns False with empty API key."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': ''}):
            client = GeminiClient()
            assert client.is_configured() == False
    
    def test_is_configured_with_whitespace_key(self):
        """Test is_configured returns False with whitespace-only API key."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': '   \t\n   '}):
            client = GeminiClient()
            assert client.is_configured() == False
