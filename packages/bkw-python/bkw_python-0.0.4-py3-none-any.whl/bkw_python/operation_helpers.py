import time
from typing import Optional, List
from pydantic import parse_obj_as, ValidationError
from .exceptions import BkwException
from .rest_adapter import RestAdapter
from .data_models import Case, Party
import logging

def combine_paginated_results(operation)