

import jwt
import time
 

def generate_token(apikey: str, exp_seconds: int = 100000000000000) -> str:
    """ Generate a JWT token.
    Args:
        apikey (str): The API key in the format "id.secret".
        exp_seconds (int): Expiration time in seconds.  
    Returns:
        str: The generated JWT token.
    """
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)
 
    return jwt.encode(
        {
          "api_key": id,
          "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
          "timestamp": int(round(time.time() * 1000)),
        },
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )