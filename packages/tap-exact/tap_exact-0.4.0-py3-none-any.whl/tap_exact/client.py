"""REST client handling, including ExactOnlineStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import Stream

from exactonline.api import ExactApi
from exactonline.storage.ini import IniStorage
from exactonline.storage.base import ExactOnlineConfig 
from singer_sdk.tap_base import Tap
from singer_sdk.pagination import BaseHATEOASPaginator

from exactonline.resource import GET
from datetime import datetime
from time import sleep

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ExactOnlineStream(Stream):
    # The fields that have /Date(unixmilliseconds)/ objects that should be converted into datetime objects
    date_fields = []

    """ExactOnline stream class."""
    def __init__(self, tap: Tap) -> None:
        super().__init__(tap)
        storage = IniStorage(self.config.get("config_file_location"))
        self.division = storage.get_division()
        self.conn = ExactApi(storage=storage)

    def get_new_paginator(self) -> BaseHATEOASPaginator:
        return ExactOnlinePaginator()
    
    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""
        return NotImplementedError

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator or row-type dictionary objects"""
        
        # Create paginator instance
        paginator = self.get_new_paginator()

        # Construct the url
        url = 'v1/%d/%s' % (self.division, self.get_path(context))

        # Loop until paginator is finished
        while not paginator.finished and url is not None:
            # Execute the request
            resp = self.conn.rest(GET( url ))

            for row in resp:
                
                # We loop through the keys that should be modified
                for date_field in self.date_fields:
                    row[date_field] = datetime.fromtimestamp( int(row[date_field][6:-2]) / 1000.0 )

                yield row

            # Get the next page url
            url = paginator.get_next_url(resp)

            # Sleep 1 second to prevent too many requests per minute
            sleep(1)


class ExactOnlinePaginator(BaseHATEOASPaginator):
    def get_next_url(self, response):
        # Parse __next from response
        next_url = response.json().get("__next")

        # Remove url and preceding slash from url, else return None
        return next_url.remove(self.storage.get_rest_url() + '/', '') if next_url else None