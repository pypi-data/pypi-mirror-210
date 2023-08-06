"""
Config Module for generic purposes.
"""
import logging

LOGGER = logging.getLogger('Klops')
LOGGER.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)-15s %(levelname)-8s %(message)s'))
LOGGER.addHandler(handler)
