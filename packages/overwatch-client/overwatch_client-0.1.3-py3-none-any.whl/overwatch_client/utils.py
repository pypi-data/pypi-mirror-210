import random
import string

alphabet = string.ascii_lowercase + string.digits


def generate_uuid(length: int = 8) -> str:
    """Generate a random UUID with length.

    Args:
        length (int, optional): The length of the UUID. Defaults to 8.

    Returns:
        str: A random UUID of the specified length.
    """
    return "".join(random.choices(alphabet, k=length))
