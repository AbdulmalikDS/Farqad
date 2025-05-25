"""API utility functions to reduce code duplication."""

import logging
import httpx
from typing import Dict, Any, Optional, Union
from fastapi.responses import JSONResponse

async def forward_internal_request(
    endpoint: str,
    json_data: Dict[str, Any],
    base_url: str = "http://localhost:8000"
) -> Union[Dict[str, Any], JSONResponse]:
    """Forward a request to an internal API endpoint.
    
    Args:
        endpoint: The API endpoint path
        json_data: The JSON data to send in the request
        base_url: The base URL for internal API (default: http://localhost:8000)
        
    Returns:
        The JSON response data or a JSONResponse error
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/{endpoint.lstrip('/')}",
                json=json_data
            )
            
            if response.status_code != 200:
                logging.error(f"Internal API error: {response.status_code}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={"answer": f"Error processing your request. Status: {response.status_code}"}
                )
                
            return response.json()
            
    except Exception as e:
        logging.error(f"Error forwarding request to {endpoint}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"answer": f"I'm sorry, an error occurred while processing your request: {str(e)}"}
        )

def create_error_response(
    error: Exception,
    status_code: int = 500,
    extra_fields: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response.
    
    Args:
        error: The exception that occurred
        status_code: The HTTP status code to return
        extra_fields: Optional additional fields to include in the response
        
    Returns:
        A JSONResponse with error details
    """
    content = {
        "answer": f"I'm sorry, an error occurred while processing your request: {str(error)}"
    }
    
    if extra_fields:
        content.update(extra_fields)
        
    return JSONResponse(status_code=status_code, content=content) 