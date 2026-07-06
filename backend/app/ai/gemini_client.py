import time
import google.generativeai as genai
import google.api_core.exceptions as g_exceptions
from app.core.settings import settings
from app.utils.exceptions import FinReliefException

class GeminiClient:
    """
    Centralized Google Gemini API Client wrapper.
    Handles auth configuration, exponential backoff retries, timeouts,
    and supports mock injection keys for test coverage testing.
    """

    @staticmethod
    def get_model(api_key: str = None) -> genai.GenerativeModel:
        """
        Configures and retrieves the GenerativeModel handler instance.
        """
        key = api_key or settings.GEMINI_API_KEY
        
        # Guard for placeholder default values
        if not key or key == "your_gemini_api_key_here":
            raise FinReliefException(
                message="Gemini API Key is invalid or not configured. Register your key in the environment.",
                code="GEMINI_AUTHENTICATION_ERROR",
                status_code=401
            )
            
        try:
            genai.configure(api_key=key)
            return genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            raise FinReliefException(
                message=f"Failed to initialize Gemini engine: {str(e)}",
                code="GEMINI_API_ERROR",
                status_code=500
            )

    @staticmethod
    def generate_content_with_retry(prompt: str, api_key: str = None, timeout: float = 10.0) -> str:
        """
        Submits prompt to Gemini API with exponential retry logic.
        Detects mock keys and simulates failure cases for tests.
        """
        key = api_key or settings.GEMINI_API_KEY
        
        # Mock Key Hooks Simulation
        if key and isinstance(key, str) and key.startswith("mock_key_"):
            if key == "mock_key_timeout":
                raise FinReliefException(
                    message="Gemini API request timed out (Simulated).",
                    code="GEMINI_TIMEOUT",
                    status_code=504
                )
            elif key == "mock_key_empty":
                raise FinReliefException(
                    message="Received empty response from Gemini API (Simulated).",
                    code="GEMINI_EMPTY_RESPONSE",
                    status_code=500
                )
            elif key == "mock_key_invalid":
                raise FinReliefException(
                    message="Gemini authentication or argument error (Simulated).",
                    code="GEMINI_AUTHENTICATION_ERROR",
                    status_code=401
                )
            elif key == "mock_key_success":
                # Returns high quality mock content based on prompt
                lower_p = prompt.lower()
                if "settlement proposal letter" in lower_p:
                    return (
                        "Formal Settlement Proposal Letter\n\n"
                        "To: Creditor Relations\n"
                        "Subject: Settlement Proposal for Account\n\n"
                        "Dear Lender,\n"
                        "Please accept this letter as a request to settle my outstanding balance. "
                        "Due to severe financial hardship, I propose a single payment settlement. "
                        "I look forward to your agreement.\n\n"
                        "Sincerely,\nBorrower"
                    )
                elif "negotiation strategy" in lower_p:
                    return (
                        "### Negotiation Strategy Guide\n"
                        "1. Call creditor relations directly.\n"
                        "2. Explain hardship factors.\n"
                        "3. Offer the recommended settlement amount.\n"
                        "4. Get agreement in writing."
                    )
                elif "email proposal to the creditor" in lower_p:
                    return (
                        "Subject: Settlement Proposal Offer\n"
                        "---\n"
                        "Dear Creditor,\n"
                        "I am writing to offer a settlement compromise on my account due to financial hardship."
                    )
                elif "explain the user's financial health" in lower_p:
                    return (
                        "Your financial health analysis indicates high risk. "
                        "Your health score of 55.5 reflects significant debt burdens. "
                        "Please prioritize high-interest accounts first."
                    )
                return "Mock generated response text."
        
        # Verify real model setup
        model = GeminiClient.get_model(key)
        
        retries = 3
        backoff = 1.0
        last_error = None
        
        for attempt in range(retries):
            try:
                # generate_content supports dict options configurations in recent client updates
                response = model.generate_content(
                    prompt,
                    request_options={"timeout": timeout}
                )
                
                # Check for empty response text
                if not response or not response.text or not response.text.strip():
                    raise FinReliefException(
                        message="Received empty response from Gemini API.",
                        code="GEMINI_EMPTY_RESPONSE",
                        status_code=500
                    )
                    
                return response.text
                
            except g_exceptions.InvalidArgument as e:
                raise FinReliefException(
                    message=f"Gemini API invalid argument or key configuration error: {str(e)}",
                    code="GEMINI_AUTHENTICATION_ERROR",
                    status_code=401
                )
            except g_exceptions.PermissionDenied as e:
                raise FinReliefException(
                    message=f"Gemini API permission denied: {str(e)}",
                    code="GEMINI_AUTHENTICATION_ERROR",
                    status_code=401
                )
            except g_exceptions.ResourceExhausted as e:
                raise FinReliefException(
                    message="Gemini API rate limit exceeded. Try again later.",
                    code="GEMINI_RATE_LIMIT_EXCEEDED",
                    status_code=429
                )
            except (g_exceptions.DeadlineExceeded, TimeoutError) as e:
                last_error = FinReliefException(
                    message="Gemini API request timed out.",
                    code="GEMINI_TIMEOUT",
                    status_code=504
                )
            except Exception as e:
                err_str = str(e).lower()
                if "deadline" in err_str or "timeout" in err_str:
                    last_error = FinReliefException(
                        message="Gemini API request timed out.",
                        code="GEMINI_TIMEOUT",
                        status_code=504
                    )
                elif "api key" in err_str or "api_key" in err_str or "unauthorized" in err_str or "forbidden" in err_str:
                    raise FinReliefException(
                        message=f"Gemini authentication error: {str(e)}",
                        code="GEMINI_AUTHENTICATION_ERROR",
                        status_code=401
                    )
                else:
                    last_error = FinReliefException(
                        message=f"Gemini API failure: {str(e)}",
                        code="GEMINI_API_ERROR",
                        status_code=500
                    )
            
            # Backoff delay if retry remains
            if attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2.0
                
        raise last_error or FinReliefException(
            message="Gemini API call failed after multiple attempts.",
            code="GEMINI_API_ERROR",
            status_code=500
        )
