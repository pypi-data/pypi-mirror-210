"""
This module holds the logic for the runtime storage and generation of the
run report. It contains metadata about the two main entities in the run report:
the run as a whole and its children, the steps.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from thoughtful.__version__ import __version__
from thoughtful.supervisor.reporting.record_report import RecordReport
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.reporting.step_report import StepReport
from thoughtful.supervisor.reporting.timed_report import TimedReport


@dataclass
class Report(TimedReport):
    """
    Report: A report is a representation of a run's execution. This dataclass
    contains all the information that will be stored in the run report,
    including a list of the steps that were executed. This is the parent
    class of the run report, and as such will only ever be one per run report.
    """

    supervisor_version = str(__version__)
    """
    str: The version of the supervisor that generated the report.
    """

    workflow: List[Union[StepReport, RecordReport]] = field(default_factory=list)
    """
    List[StepReport]: The list of steps that were executed.
    """

    status: Optional[Status] = None
    """
    Status, optional: The status of the run.
    """

    def __json__(self) -> Dict[str, Any]:
        return {
            **super().__json__(),
            "supervisor_version": self.supervisor_version,
            "workflow": [step.__json__() for step in self.workflow],
            "status": self.status.value,
        }

    def write(self, filename: Union[str, pathlib.Path]) -> None:
        """
        Write the report as a JSON object to a file.

        Args:
            filename: Where to write the file.
        """
        path = (
            filename if isinstance(filename, pathlib.Path) else pathlib.Path(filename)
        )

        with path.open("w") as out:
            report_dict = self.__json__()
            json.dump(report_dict, out)
