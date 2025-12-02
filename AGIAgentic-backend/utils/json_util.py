
import re
import json
import logging


from typing import Dict, Any


def json_match(content: str) -> Dict[str, Any]:
    """ A robust JSON parser that can extract JSON objects from messy text.
    Args:
        content (str): The input string potentially containing JSON data.
    Returns:  
        Dict[str, Any]: The parsed JSON object, or an empty dict if parsing fails.
    """
    if not content:
        return dict()
    
    try:
        result_data = json.loads(content)
        return result_data
    except json.JSONDecodeError:
        pass
    
    try:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result_data = json.loads(json_match.group())
            return result_data
    except json.JSONDecodeError:
        pass
    
    try:
        json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        for match in json_matches:
            try:
                result_data = json.loads(match)
                return result_data
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    
    try:
        json_pattern = r'\{[^{}]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}[^{}]*)*\}'
        json_matches = re.findall(json_pattern, content, re.DOTALL)
        for match in json_matches:
            try:
                result_data = json.loads(match)
                return result_data
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    
    logging.error(f"JSON parsing failed, original content: {content[:200]}...")
    return dict()