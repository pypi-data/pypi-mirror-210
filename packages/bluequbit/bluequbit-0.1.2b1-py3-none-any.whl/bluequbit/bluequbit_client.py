# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import contextlib
import logging
import os
import time
from typing import TYPE_CHECKING, Any

from . import job_metadata_constants
from .api import jobs
from .backend_connection import BackendConnection
from .check_version import check_version
from .estimate_result import EstimateResult
from .exceptions import (
    BQBatchJobsLimitExceededError,
    BQJobCouldNotCancelError,
    BQJobInvalidDeviceTypeError,
    BQJobNotCompleteError,
)
from .job_result import JobResult
from .version import __version__

if TYPE_CHECKING:
    import datetime

# TODO this requires imports of actual quantum libraries for proper type
# checking.
CircuitT = Any

logger = logging.getLogger("bluequbit-python-sdk")


class BQClient:
    """Client for managing jobs on BlueQubit platform.

    :param api_token: API token of the user. If ``None``, the token will be looked
                      in default configuration file ``$HOME/.config/bluequbit/config.json``.
                      If not ``None``, the token will also be saved in the same
                      default configuration file.
    :param update_config_file: if True, update default configuration file
                               if api_token is not None.
    """

    def __init__(self, api_token: str | None = None, update_config_file: bool = True):
        if os.environ.get("BLUEQUBIT_TESTING") is None:
            with contextlib.suppress(Exception):
                check_version(__version__)

        self._backend_connection = BackendConnection(api_token, update_config_file)

    @staticmethod
    def validate_device(device):
        if not isinstance(device, str):
            raise BQJobInvalidDeviceTypeError(device)
        converted_device = device.lower()
        if converted_device not in job_metadata_constants.DEVICE_TYPES:
            raise BQJobInvalidDeviceTypeError(device)
        return converted_device

    @staticmethod
    def validate_batch(batch):
        if (
            isinstance(batch, list)
            and len(batch) > job_metadata_constants.MAXIMUM_NUMBER_OF_BATCH_JOBS
        ):
            raise BQBatchJobsLimitExceededError(len(batch))

    def estimate(
        self, circuits: CircuitT | list[CircuitT], device: str = "cpu"
    ) -> EstimateResult | list[EstimateResult]:
        """Estimate job runtime

        :param circuits: quantum circuit or circuits
        :type circuits: Cirq, Qiskit, list
        :param device: device for which to estimate the circuit. Can be one of
                       ``"cpu"`` | ``"gpu"`` | ``"quantum"``
        :return: estimate result or results metadata
        """
        device = self.validate_device(device)
        self.validate_batch(circuits)
        response = jobs.submit_jobs(
            self._backend_connection, circuits, device, estimate_only=True
        )
        if isinstance(circuits, list):
            return [EstimateResult(data) for data in response]
        else:
            return EstimateResult(response)

    def run(
        self,
        circuits: CircuitT | list[CircuitT],
        device: str = "cpu",
        asynchronous: bool = False,
        job_name: str | None = None,
        shots: int = 1000,
    ) -> JobResult | list[JobResult]:
        """Submit a job to run on BlueQubit platform

        :param circuits: quantum circuit or list of circuits
        :type circuits: Cirq, Qiskit, list
        :param device: device on which to run the circuit. Can be one of
                       ``"cpu"`` | ``"gpu"`` | ``"quantum"``
        :param asynchronous: if set to ``False``, wait for job completion before
                             returning. If set to ``True``, return immediately
        :param job_name: customizable job name
        :param shots: number of shots to run if device is quantum.
        :return: job metadata
        """
        device = self.validate_device(device)
        self.validate_batch(circuits)
        response = jobs.submit_jobs(
            self._backend_connection,
            circuits,
            device,
            job_name,
            shots=shots,
            asynchronous=asynchronous,
        )
        if isinstance(circuits, list):
            logger.info(
                "Submitted %s jobs. Batch ID %s", len(response), response[0]["batch_id"]
            )
            job_results = [JobResult(data) for data in response]
            if not asynchronous:
                if self._check_all_in_terminal_states(job_results):
                    return job_results
                return self.wait(job_results)
                # if job_results[0].batch_id is not None:
                #     return self.wait(batch_id=job_results[0].batch_id)
                # else:
            else:
                return job_results
        else:
            submitted_job = JobResult(response)
            if (
                submitted_job.run_status
                in job_metadata_constants.JOB_NO_RESULT_TERMINAL_STATES
            ):
                raise BQJobNotCompleteError(
                    submitted_job.job_id,
                    submitted_job.run_status,
                    submitted_job.error_message,
                )
            logger.info("Submitted: %s", submitted_job)
            if (
                not asynchronous
                and submitted_job.run_status
                not in job_metadata_constants.JOB_TERMINAL_STATES
            ):
                jr = self.wait(submitted_job.job_id)
                return jr
            return submitted_job

    @staticmethod
    def _check_all_in_terminal_states(job_results):
        if not isinstance(job_results, list):
            return job_results.run_status in job_metadata_constants.JOB_TERMINAL_STATES
        else:
            return all(
                job_result.run_status in job_metadata_constants.JOB_TERMINAL_STATES
                for job_result in job_results
            )

    def wait(
        self, job_ids: str | list[str] | JobResult | list[JobResult]
    ) -> JobResult | list[JobResult]:
        """Wait for job completion

        :param job_ids: job IDs that can be found as property of :class:`JobResult` metadata
                        of :func:`~run` method, or `JobResult` instances from which job IDs
                        will be extracted
        :return: job metadata
        """
        self.validate_batch(job_ids)
        while True:
            job_results = self.get(job_ids)
            if self._check_all_in_terminal_states(job_results):
                if (
                    not isinstance(job_ids, list)
                    and job_results.run_status
                    in job_metadata_constants.JOB_NO_RESULT_TERMINAL_STATES
                ):
                    raise BQJobNotCompleteError(
                        job_ids, job_results.run_status, job_results.error_message
                    )
                return job_results
            time.sleep(1.0)

    def get(
        self,
        job_ids: str | list[str] | JobResult | list[JobResult],
    ) -> JobResult | list[JobResult]:
        """Get current metadata of jobs

        :param job_ids: job IDs that can be found as property of :class:`JobResult` metadata
                        of :func:`~run` method
        :return: jobs metadata
        """
        self.validate_batch(job_ids)
        job_ids_list = job_ids if isinstance(job_ids, list) else [job_ids]
        if isinstance(job_ids_list[0], JobResult):
            job_ids_list = [jr.job_id for jr in job_ids_list]
        job_results = jobs.search_jobs(self._backend_connection, job_ids=job_ids_list)
        job_results = [JobResult(r) for r in job_results["data"]]
        if isinstance(job_ids, list):
            return job_results
        else:
            return job_results[0]

    def cancel(
        self, job_ids: str | list[str] | JobResult | list[JobResult]
    ) -> JobResult | list[JobResult]:
        """Submit jobs cancel request

        :param job_ids: job IDs that can be found as property of :class:`JobResult` metadata
                        of :func:`run` method
        :return: job or jobs metadata
        """
        self.validate_batch(job_ids)
        if isinstance(job_ids, JobResult):
            job_ids = job_ids.job_id
        elif isinstance(job_ids, list) and isinstance(job_ids[0], JobResult):
            job_ids = [jr.job_id for jr in job_ids]
        responses = jobs.cancel_jobs(self._backend_connection, job_ids)
        if isinstance(job_ids, list):
            for response in responses:
                if response["ret"] == "FAILED":
                    logger.warning(response["error_message"])
        try:
            self.wait(job_ids)
        except BQJobNotCompleteError as e:
            if not e.run_status == "CANCELED":
                raise BQJobCouldNotCancelError(
                    e.job_id, e.run_status, e.error_message
                ) from None
        return self.get(job_ids)

    def search(
        self,
        run_status: str | None = None,
        created_later_than: str | datetime.datetime | None = None,
        batch_id: str | None = None,
    ) -> list[JobResult]:
        """Search jobs

        :param run_status: if not ``None``, run status of jobs to filter.
                           Can be one of ``"FAILED_VALIDATION"`` | ``"PENDING"`` |
                           ``"QUEUED"`` | ``"RUNNING"`` | ``"TERMINATED"`` | ``"CANCELED"`` |
                           ``"NOT_ENOUGH_FUNDS"`` | ``"COMPLETED"``

        :param created_later_than: if not ``None``, filter by latest job creation datetime.
                                   Please add timezone for clarity, otherwise UTC
                                   will be assumed

        :param batch_id: if not ``None``, filter by batch ID

        :return: metadata of jobs
        """
        job_results = jobs.search_jobs(
            self._backend_connection, run_status, created_later_than, batch_id=batch_id
        )
        return [JobResult(r) for r in job_results["data"]]
