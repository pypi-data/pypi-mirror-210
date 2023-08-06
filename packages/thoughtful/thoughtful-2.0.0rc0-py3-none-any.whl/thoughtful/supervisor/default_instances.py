"""
Default instances for dynamic runs.

Typically, developers will only run one digital worker on a Python
runtime, and it is tricky to initialize an object and pass that object
instance down into other files in a project for a custom decorator.
This package provides a set of default instances of objects and contexts
for dynamic runs.

This file initializes a shared `ReportBuilder` and `Recorder` for
individual steps and sub steps to share, then creates:

    - a default ``MainContext`` named ``supervise``,
    - a decorator to annotate steps called ``step``,
    - a ``StepContext`` named ``step_context``,
    - a function to set step statuses called ``set_step_status``,
    - and a function to set record statuses called ``set_record_status``.

See the quickstart for, well, quickstarts on each of these methods.
"""

import logging
import pathlib
from typing import Optional, Union

from thoughtful.environment_variables import EnvironmentVariables
from thoughtful.supervisor.main_context import MainContext
from thoughtful.supervisor.manifest import Manifest
from thoughtful.supervisor.reporting.report_builder import ReportBuilder
from thoughtful.supervisor.step_context import StepContext
from thoughtful.supervisor.step_decorator_factory import create_step_decorator
from thoughtful.supervisor.streaming.callback import StreamingCallback

logger = logging.getLogger(__name__)

# Share a streaming callback variable, but we can't set it until a user
# provides a JWT token.
streamer = StreamingCallback(
    run_id=EnvironmentVariables().run_id,
    callback_url=EnvironmentVariables().callback_url,
    # The JWT token is set by the user later. If steamer is set to None,
    # then the step decorators can't be updated to stream if streamer is
    # changed to a new instance.
    #
    # See CX-2368 for the proper fix by lifting the streamer out of the contexts
    jwt_token="",
)

#: A shared ``ReportBuilder`` for steps and step contexts to add step reports
#: to.
report_builder = ReportBuilder()

#: Use this decorator on your own functions to mark what workflow step each
#: Python function is matched to.
step = create_step_decorator(report_builder, streamer)

#: Use this function to mark a step as failed.
#: This is just a shortcut for ``set_step_status(step_id, "failed")``.
#: Exposes ``report_builder.fail_step``.
fail_step = report_builder.fail_step

#: Expose the report builder's ability to override a step's status as a
#: top-level call. Exposes ``report_builder.set_step_status``.
set_step_status = report_builder.set_step_status

#: Expose the report builder's ability to override a step's record's status as a
#: top-level call. Exposes ``report_builder.set_record_status``.
set_record_status = report_builder.set_record_status

#: Expose the report builder's ability to override a run's status as a
#: top-level call. Exposes ``report_builder.set_run_status``.
set_run_status = report_builder.set_run_status


# noinspection PyPep8Naming
class step_scope(StepContext):
    """
    It's a context manager that provides a scope for a step using the
    aforementioned default instances of ``report_builder`` and ``recorder``.
    """

    def __init__(self, step_id: str):
        """
        A default `StepContext` that uses the root level `report_builder` and
        `recorder`.

        Args:
            *step_id: The list of integers that represent the step ID.
        """
        super().__init__(
            report_builder,
            step_id,
            streaming_callback=streamer,
        )


# noinspection PyPep8Naming
class supervise(MainContext):
    """
    It's a context manager that provides a scope for the main context using the
    aforementioned default instances of ``report_builder`` and ``recorder``.
    """

    def __init__(
        self,
        manifest: Union[Manifest, str, pathlib.Path] = "manifest.yaml",
        output_dir: Union[str, pathlib.Path] = "output/",
        *args,
        **kwargs,
    ):
        """
        A default `MainContext` that uses the root level `report_builder` and
        `recorder`.

        Args:
            *args: Extra arguments to the `MainContext` constructor.
            **kwargs: Extra keyword arguments to the `MainContext` constructor.
            manifest (str): The digital worker's manifest definition
            output_dir (str): Where the work report and drift report will
                be written to
        """
        super().__init__(
            report_builder=report_builder,
            manifest=manifest,
            output_dir=output_dir,
            upload_uri=EnvironmentVariables().s3_bucket_uri,
            streaming_callback=streamer,
            *args,
            **kwargs,
        )
