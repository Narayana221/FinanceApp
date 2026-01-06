"""
Gemini API client for financial advice generation.

This module provides a client for interacting with Google's Gemini 2.5 Flash API
to generate personalized financial coaching and recommendations.
"""

import os
import time
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv


class GeminiClient:
    """Client for Gemini 2.5 Flash API interactions."""
    
    # API endpoint for Gemini 2.5 Flash
    API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    # Request timeout in seconds (NFR-PERF-002)
    TIMEOUT = 15
    
    # Retry configuration
    MAX_RETRIES = 1
    RETRY_DELAY = 2  # seconds
    
    def __init__(self):
        """
        Initialize Gemini API client with authentication.
        
        Loads API key from GEMINI_API_KEY environment variable.
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        # Note: We don't raise an error here to allow graceful degradation
        # Error handling happens when actually making requests
    
    def generate_financial_advice(self, prompt: str) -> Dict[str, Any]:
        """
        Generate financial advice from Gemini API.
        
        Args:
            prompt: Structured prompt containing financial data and context
            
        Returns:
            dict: Result dictionary with keys:
                - success (bool): True if advice generated successfully
                - advice (str): Generated advice text (if success=True)
                - error (str): Error message (if success=False)
                
        Examples:
            >>> client = GeminiClient()
            >>> result = client.generate_financial_advice("Analyze my spending...")
            >>> if result['success']:
            ...     print(result['advice'])
            ... else:
            ...     print(result['error'])
        """
        # Validate API key is configured
        if not self.api_key or self.api_key.strip() == '':
            return {
                'success': False,
                'error': 'AI Coach unavailable. Please configure API key.'
            }
        
        # Prepare request payload
        payload = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': prompt
                        }
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.7,
                'maxOutputTokens': 500
            }
        }
        
        try:
            # Make API request with retry logic
            response = self._make_request(payload)
            
            # Parse successful response
            advice_text = self._parse_response(response)
            
            return {
                'success': True,
                'advice': advice_text
            }
            
        except Exception as e:
            # Handle any errors
            error_message = self._handle_error(e)
            return {
                'success': False,
                'error': error_message
            }
    
    def _make_request(self, payload: Dict) -> requests.Response:
        """
        Make HTTP POST request to Gemini API with retry logic.
        
        Implements single retry with exponential backoff for transient errors.
        
        Args:
            payload: Request body with prompt and configuration
            
        Returns:
            requests.Response: Successful API response
            
        Raises:
            requests.exceptions.RequestException: On network/timeout errors
            requests.exceptions.Timeout: On timeout errors
            ValueError: On HTTP error responses
        """
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add API key as query parameter
        url = f"{self.API_ENDPOINT}?key={self.api_key}"
        
        # Attempt request with retry logic
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                # Make POST request with timeout
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.TIMEOUT
                )
                
                # Check for HTTP errors
                response.raise_for_status()
                
                # Success - return response
                return response
                
            except requests.exceptions.Timeout:
                # Don't retry on timeout (already waited 15 seconds)
                raise
                
            except requests.exceptions.RequestException as e:
                # Check if we should retry
                if attempt < self.MAX_RETRIES:
                    # Wait before retrying
                    time.sleep(self.RETRY_DELAY)
                    continue
                else:
                    # All retries exhausted
                    raise
        
        # This should never be reached, but included for completeness
        raise requests.exceptions.RequestException("Request failed after retries")
    
    def _parse_response(self, response: requests.Response) -> str:
        """
        Parse advice text from Gemini API response.
        
        Args:
            response: Successful API response
            
        Returns:
            str: Extracted advice text
            
        Raises:
            ValueError: If response format is invalid
        """
        try:
            data = response.json()
            
            # Navigate JSON structure to extract advice text
            advice_text = data['candidates'][0]['content']['parts'][0]['text']
            
            return advice_text.strip()
            
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Invalid response format: {str(e)}")
    
    def _handle_error(self, error: Exception) -> str:
        """
        Classify error and return user-friendly message.
        
        Args:
            error: Exception from API call or response parsing
            
        Returns:
            str: User-friendly error message
        """
        # Timeout errors
        if isinstance(error, requests.exceptions.Timeout):
            return "AI Coach taking longer than expected. Using basic analysis."
        
        # HTTP error responses
        if isinstance(error, requests.exceptions.HTTPError):
            status_code = error.response.status_code if error.response else None
            
            # Rate limiting (429)
            if status_code == 429:
                return "AI Coach busy. Please try again in a moment."
            
            # Authentication errors (401, 403)
            if status_code in [401, 403]:
                return "AI Coach unavailable. Please configure API key."
            
            # Other HTTP errors
            return "AI Coach unavailable. Using basic analysis."
        
        # Network/connection errors
        if isinstance(error, requests.exceptions.ConnectionError):
            return "AI Coach unavailable. Please check connection."
        
        # Response parsing errors
        if isinstance(error, ValueError):
            return "AI Coach unavailable. Using basic analysis."
        
        # Generic error
        return "AI Coach unavailable. Using basic analysis."
    
    def is_configured(self) -> bool:
        """
        Check if API key is configured.
        
        Returns:
            bool: True if API key is set and not empty
        """
        return bool(self.api_key and self.api_key.strip())
