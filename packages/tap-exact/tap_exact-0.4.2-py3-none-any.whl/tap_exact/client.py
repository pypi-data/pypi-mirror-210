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

from exactonline.resource import GET
from datetime import datetime

import abc

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ExactOnlineStream(Stream):
    __metaclass__ = abc.ABCMeta
    
    # The fields that have /Date(unixmilliseconds)/ objects that should be converted into datetime objects
    date_fields = []

    """ExactOnline stream class."""
    def __init__(self, tap: Tap) -> None:
        super().__init__(tap)
        self.conn = self.create_connection()

    def create_connection(self) -> ExactApi:
        # We want to make sure the ini file is updated during runtime
        storage = IniStorage(self.config.get("config_file_location"))
        self.division = storage.get_division()
        return ExactApi(storage=storage)

    def refresh_connection(self) -> None:
        # We want to refresh the connection to make sure we're always using the latest ini file during runtime
        self.conn = self.create_connection()

    @abc.abstractmethod
    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""
        raise NotImplementedError("Please implement this method")

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator or row-type dictionary objects"""
        
        # Construct the url
        url = 'v1/%d/%s' % (self.division, self.get_path(context))

        # Refresh the connection
        self.refresh_connection()

        # Execute the request
        resp = self.conn.rest(GET( url ))

        for row in resp:
            
            # We loop through the keys that should be modified
            for date_field in self.date_fields:
                row[date_field] = datetime.fromtimestamp( int(row[date_field][6:-2]) / 1000.0 )

            yield row