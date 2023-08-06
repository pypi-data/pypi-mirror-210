"""
This module contains the ``Record`` class, a non-user facing class that is used
to store information about a step's record. This class is represented in the
run report as a json object.

.. code-block:: json

    {
        "workflow": [
            {
                "step_id": "1.1",
                "step_status": "succeeded",
                "record": {
                    "id": "1",
                    "status": "succeeded",
                    "message": "Message can provide additional information",
                    "metadata": {
                        "internal_reason": "record amount is too low",
                        "amount": 15
                    }
                }
            }
        ]
    }

"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from thoughtful.supervisor.reporting.status import Status


@dataclass
class Record:
    """
    A record can refer to any object that is being processed by a step. It
    is here represented by its ID and its status.
    """

    record_id: str
    """
    str: The status of the record.
    """

    status: Status
    """
    Status: The status of the record.
    """

    message: Optional[str] = field(default_factory=str)
    """
    Message: Place to store a message about the record. limit 120 characters
    """

    # make required default = {} ?
    metadata: Optional[dict] = field(default_factory=dict)
    """
    Metadata: Place to store metadata about the record.
    """

    def __post_init__(self):
        """
        Validate the record message length
        """
        if len(self.message) > 120:
            raise ValueError("Record Message Field - 120 Character limit exceeded")

        validate_metadata_json_helper(self.metadata)

    def __json__(self):
        return {
            "id": self.record_id,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata,
        }


def validate_metadata_json_helper(item: Dict):
    """
    Validates that the metadata field is a valid JSON object and that it is less
    than 5 KB
    """
    try:
        json_str = json.dumps(item)
        if len(json_str) / 1024 > 5:
            raise ValueError(
                "Metadata validation failed - Object cannot exceed 5 KB - please reduce size of record payload"
            )
    except TypeError as e:
        raise TypeError(f"Record Message Field - Unsupported Type detected : ${e}")
    except ValueError as e:
        raise ValueError(f"Record Message Field - Must be JSON serializable : ${e}")
