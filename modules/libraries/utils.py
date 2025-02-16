import os
import logging
from typing import Dict


def read_tokens() -> Dict[str, str]:
    """
    Reading tokens with this format:
        telegram:waeqw3123
        crypto:salkdju32o4u214
    """
    file_path = "/home/atheop1337/Tokens/pbot"
    tokens = {}

    if not os.path.exists(file_path):
        logging.error("Token file not found: %s", file_path)
        return tokens

    try:
        with open(file_path, "r") as file:
            for line in file:
                if ":" in line:
                    key, value = line.strip().split(":", maxsplit=1)
                    tokens[key] = value

        return tokens
    except Exception as e:
        logging.exception("Error reading tokens from file: %s", e)
        return {}
    
