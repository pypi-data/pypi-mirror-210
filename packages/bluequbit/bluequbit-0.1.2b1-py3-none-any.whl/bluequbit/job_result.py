import datetime
from io import BytesIO
from typing import Dict, Optional

import numpy as np
from dateutil.parser import parse

from . import job_metadata_constants
from .exceptions import (
    BQJobDoesNotContainCountsError,
    BQJobHasNotFinishedYetError,
    BQJobNotCompleteError,
    BQJobStatevectorTooLargeError,
)
from .http_utils import request_retriable


class JobResult:
    """This class contains information from a job run on quantum hardware or
    quantum simulators. Mainly it contains the resulting statevector from the
    run. It might contain only partial information, such as job ID,
    when :func:`BQClient.run` is called with ``asynchronous=True``."""

    def __init__(self, data):
        #: str: job id
        self.job_id = data.get("job_id")

        #: str: batch id
        self.batch_id = data.get("batch_id")

        #: str: job run status, can be one of ``"FAILED_VALIDATION"`` | ``"PENDING"`` |
        #       ``"QUEUED"`` | ``"RUNNING"`` | ``"TERMINATED"`` | ``"CANCELED"`` |
        #       ``"NOT_ENOUGH_FUNDS"`` | ``"COMPLETED"``
        self.run_status = data.get("run_status")

        #: str: job name
        self.job_name = data.get("job_name")

        #: str: run device
        self.device = data.get("device")

        #: int: estimated runtime in milliseconds
        self.estimated_runtime = data.get("estimated_runtime_ms")

        #: float: estimated cost in US dollars
        self.estimated_cost = data.get("estimated_cost")
        if self.estimated_cost is not None:
            self.estimated_cost /= 100.0

        #: datetime: job creation date in UTC timezone
        self.created_on = parse(data.get("created_on"))

        self._results_path = data.get("results_path")
        self.top_100_results = data.get("top_100_results")

        #: int: number of qubits
        self.num_qubits = data.get("num_qubits")
        self.tags = data.get("tags")

        self.run_start = data.get("run_start")
        if self.run_start is not None:
            self.run_start = parse(self.run_start)

        self.run_end = data.get("run_end")
        if self.run_end is not None:
            self.run_end = parse(self.run_end)

        #: int: job queue time in milliseconds
        self.queue_time_ms = None
        if self.run_start is not None:
            self.queue_time_ms = int(
                (self.run_start - self.created_on) / datetime.timedelta(milliseconds=1)
            )

        #: int: job runtime in milliseconds
        self.run_time_ms = None
        if self.run_start is not None and self.run_end is not None:
            self.run_time_ms = round(
                (self.run_end - self.run_start) / datetime.timedelta(milliseconds=1)
            )

        #: str: error message if failed
        self.error_message = data.get("error_message")

        #: float: job cost in US dollars
        self.cost = data.get("cost")
        if self.cost is not None:
            self.cost /= 100.0
        self._metadata = None

        #: bool: if statevector available
        self.has_statevector = data.get("has_statevector")

        self._statevector = None

    def get_statevector(self) -> np.array:
        """Return statevector of the job. If the statevector is too large then throws exception.

        :rtype: NumPy array
        """
        if self.run_status in job_metadata_constants.JOB_NON_TERMINAL_STATES:
            raise BQJobHasNotFinishedYetError(self.job_id, self.run_status)
        elif not self.ok:
            raise BQJobNotCompleteError(
                self.job_id, self.run_status, self.error_message
            )
        elif self.has_statevector is False:
            raise BQJobStatevectorTooLargeError(self.job_id, self.num_qubits)

        if self._statevector is None:
            response = request_retriable("GET", self._results_path + "statevector.txt")
            self._statevector = np.loadtxt(BytesIO(response.content), dtype=np.complex_)
        return self._statevector

    def get_counts(self) -> Optional[Dict[str, float]]:
        """
        "counts" is the measurement probabilities of the computation result,
        without any statistical fluctuation. It is equivalent to what you would
        get from a Qiskit result if you do `get_counts` on it from a Qiskit
        simulation with 0 shot.
        """
        if self._metadata is None:
            response = request_retriable("GET", self._results_path + "metadata.json")
            self._metadata = response.json()
        if "counts" not in self._metadata:
            raise BQJobDoesNotContainCountsError(self.job_id)
        return self._metadata["counts"]

    @property
    def ok(self) -> bool:  # pylint: disable=invalid-name
        """``True``, if job's current run status is ``"COMPLETED"``,
        else ``False``."""

        return self.run_status == "COMPLETED"

    def __repr__(self):
        jr_repr = f"Job ID: {self.job_id}"
        if self.batch_id is not None:
            jr_repr += f" (batch ID: {self.batch_id})"
        if self.job_name is not None:
            jr_repr += f", name: {self.job_name}"
        jr_repr += f", device: {self.device}"
        jr_repr += f", run status: {self.run_status}"
        jr_repr += (
            f", created on: {self.created_on.replace(microsecond=0, tzinfo=None)} UTC"
        )
        if (
            self.run_status in ["PENDING", "QUEUED", "RUNNING"]
            and self.estimated_runtime is not None
        ):
            jr_repr += f", estimated runtime: {self.estimated_runtime} ms"
            jr_repr += f", estimated cost: ${self.estimated_cost:.2f}"
        if self.cost is not None:
            jr_repr += f", cost: ${self.cost:.2f}"
        if self.run_time_ms is not None:
            jr_repr += f", run time: {self.run_time_ms} ms"
        if self.queue_time_ms is not None:
            jr_repr += f", queue time: {self.queue_time_ms} ms"
        if self.num_qubits is not None:
            jr_repr += f", num qubits: {self.num_qubits}"
        if self.error_message is not None:
            jr_repr += f", error_message: {self.error_message}"
        return jr_repr
