"""This module contains the constants used in the project"""

BASE_URL = "https://api.clouding.io/v1"
"""The base URL of the API"""

WAIT_TIME = 15
"""The time to wait between each request to the API when archiving or unarchiving servers"""

MAX_TOTAL_WAIT_TIME = 300
"""The maximum total time to wait for all servers to be unarchived or archived"""

API_ALREADY_ARCHIVED_ERROR_MESSAGE = "Command 'shelve' cannot be issued while server is in the current state"
"""The error message returned by the API when trying to archive a server that is already archived"""

API_ALREADY_UNARCHIVED_ERROR_MESSAGE = "Command 'unshelve' cannot be issued while server is in the current state"
"""The error message returned by the API when trying to unarchive a server that is already unarchived"""
