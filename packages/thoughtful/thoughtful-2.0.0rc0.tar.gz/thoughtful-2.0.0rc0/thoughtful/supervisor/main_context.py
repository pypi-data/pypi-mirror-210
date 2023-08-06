"""
This module contains the code for the MainContext class. This class is
a context manager that supervises the execution of the main body of the process.

On entrance, it will verify the process manifest.

Upon exit, it will convert the step report into the run report. It will also
evaluate the ultimate status of the process—success if no exceptions were
raised, failure otherwise.

Without this context, the output manifest and run report would not be
generated at the end of the process.
"""

from __future__ import annotations

import datetime
import logging
import os
import pathlib
from types import TracebackType
from typing import Callable, Optional, Type, Union
from urllib.parse import urlparse

import boto3

from thoughtful.supervisor.manifest import Manifest
from thoughtful.supervisor.reporting.report_builder import ReportBuilder
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.streaming.callback import StreamingCallback

logger = logging.getLogger(__name__)


class MainContext:
    """
    Supervises an entire digital worker run and generates a work report
    and drift report for the run from the digital worker's manifest.

    You can optionally specify a callback function that will be run when
    this context is finished via the `callback` param in the constructor. A
    callback is a function that is invoked with two parameters: the
    current context (as the `MainContext` instance) and the `Report`
    generated from this digital worker's run.

    For example:

    .. code-block:: python

        def print_work_report(
            ctx: MainContext,
            work_report: Report
        ):
            print(work_report.__json__())

        def main()
            # ...

        with supervise(callback=print_work_report):
            main()
    """

    def __init__(
        self,
        report_builder: ReportBuilder,
        manifest: Union[Manifest, str, pathlib.Path],
        output_dir: Union[str, pathlib.Path],
        upload_uri: Optional[str] = None,
        callback: Optional[Callable] = None,
        streaming_callback: Optional[StreamingCallback] = None,
    ):
        """
        Args:
            report_builder (ReportBuilder): A ReportBuilder object that will
                receive the step reports and provide the run report.
                messages and logs throughout the process execution.
            manifest (str, Path): A pathlike object that points to the manifest
                file for the process.
            output_dir (str, Path): A pathlike object that points to the output
                directory for the process. This will receive the run report and
                output manifest.
            upload_uri (str, optional): A URI to upload the output files to.
            callback (callable, optional): a function that is invoked with three
                parameters: the current context (as the `MainContext` instance)
                and the `Report` generated from this digital worker's run.
        """
        self.report_builder = report_builder
        self.output_path = pathlib.Path(output_dir)
        self.upload_uri = upload_uri

        self.manifest_path = (
            manifest if isinstance(manifest, (str, pathlib.Path)) else None
        )
        self.manifest = self._parse_manifest(manifest)
        self.callback = callback
        self.streaming_callback = streaming_callback

    @staticmethod
    def _parse_manifest(
        manifest: Union[Manifest, str, pathlib.Path]
    ) -> Optional[Manifest]:
        if isinstance(manifest, Manifest):
            return manifest
        manifest_path = pathlib.Path(manifest)
        try:
            manifest = Manifest.from_file(manifest_path)
            return manifest
        except Exception:
            logger.exception("warning: could not read manifest")
        return None

    def __enter__(self) -> MainContext:
        """
        Logic for when this context is first started. Attempts to load the
        manifest and returns itself as the context.

        Returns:
            MainContext: This instance.
        """
        if self.manifest and self.streaming_callback:
            self.streaming_callback.post_manifest(self.manifest)
        self._stream_run_status_change(Status.RUNNING)

        return self

    def set_run_status(self, status: Union[Status, str]) -> None:
        """
        Sets the run status of the process. This is the final status of the
        process, and will be used to determine the status of the run report.

        Args:
            status (Union[Status, str]): The status to set.
        """
        self.report_builder.set_run_status(status)
        self._stream_run_status_change(status)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """
        Runs when the context is about to close, whether caused
        by a raised Exception or now.

        Returns:
            bool: True if the parent caller should ignore the
                Exception raised before entering this function
                (if any), False otherwise.
        """
        if exc_type:
            self.report_builder.run_had_exception = True
        work_report = self.report_builder.to_report()

        self._stream_run_status_change(work_report.status)

        # Create the output directory if it doesn't already exist
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Write the work report
        work_report_path = self._safe_report_path(file_prefix="run-report")
        work_report.write(work_report_path)

        # Write the manifest back out as a JSON file
        if self.manifest:
            manifest_json_path = self.output_path / "manifest.json"
            self.manifest.write_to_json_file(manifest_json_path)

        # Run the user-defined callback
        if self.callback:
            self.callback(self, work_report)

        # Upload output files to S3
        if self.upload_uri:
            try:
                self._upload_output_files_to_s3(self.upload_uri)
            except Exception:
                logger.exception("Failed to upload output files to S3")
        elif os.environ.get("ROBOCORP_HOME") is None:
            logger.warning(
                "SUPERVISOR_ARTIFACT_UPLOAD_URI is not set. Artifacts"
                " will not be uploaded to S3."
            )

        # Explicitly return false so that the parent caller above
        # this context sees the exception (if any)
        return False

    def _stream_run_status_change(self, status: Status) -> None:
        """
        Post a status change to the stream callback if it exists.
        """
        if self.streaming_callback:
            self.streaming_callback.post_status_change(status)

    def _upload_output_files_to_s3(self, upload_uri: str) -> None:
        """
        It uploads all files in the output directory to S3. It requires the
        environment variable `SUPERVISOR_ARTIFACT_UPLOAD_URI` to be set with
        the S3 URI to upload the files to.

        Args:
            upload_uri (str): The S3 URI to upload the files to.
        """
        s3_client = boto3.client("s3")
        parsed_upload_uri = urlparse(upload_uri.strip())
        bucket = parsed_upload_uri.hostname
        path = parsed_upload_uri.path.strip("/")

        for file in self.output_path.glob("*"):
            try:
                if file.is_file():
                    obj = f"{path}/{file.name}" if path else file.name
                    s3_client.upload_file(str(file), bucket, obj)
            except Exception:
                logger.exception(f"Failed to upload {file} to S3")

        if self.streaming_callback:
            self.streaming_callback.post_artifacts_uploaded(output_uri=upload_uri)

    def _safe_report_path(self, file_prefix: str) -> pathlib.Path:
        """
        A ``pathlib.Path`` instance that points to a new work report writable
        location that is safe across all OSes.

        Returns:
            pathlib.Path: The path to the new report to be written.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
        filename = f"{file_prefix}-{timestamp}.json"

        # Remove any characters from the timestamp that OSes don't like
        invalid_chars = [":", "*", "?", '"', "<", ">" "|", "'"]
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        return self.output_path / filename
