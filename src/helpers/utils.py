import random
import string
import logging

logger = logging.getLogger('uvicorn.error')

def generate_random_string(length: int = 10) -> str:
    """Generates a random alphanumeric string of a given length."""
    try:
        characters = string.ascii_lowercase + string.digits
        random_string = ''.join(random.choice(characters) for i in range(length))
        # logger.debug(f"Generated random string: {random_string}") # Optional debug log
        return random_string
    except Exception as e:
        logger.error(f"Error generating random string: {e}", exc_info=True)
        # Fallback in case of error (though unlikely with this simple logic)
        return "fallback" + str(random.randint(1000, 9999)) 