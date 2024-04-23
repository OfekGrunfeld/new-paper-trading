import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from . import communications
from .encrypt import encrypt