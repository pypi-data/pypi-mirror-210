from . import job_metadata_constants


class BQError(Exception):
    def __init__(self, message="Unknown Error Message"):
        super().__init__(message)
        self.message = message


class BQSDKUsageError(BQError):
    def __init__(self, message):
        super().__init__(message)


class BQUnauthorizedAccessError(BQError):
    def __init__(self):
        super().__init__(
            "Wrong API key. You can find your API key once you log in to"
            " https://app.bluequbit.io."
        )


class BQJobStatevectorTooLargeError(BQError):
    def __init__(self, job_id, num_qubits):
        super().__init__(
            (
                f"Statevector is too large for {num_qubits} qubits (job: {job_id})."
                " Please use .get_counts() instead."
            ),
        )
        self.job_id = job_id
        self.num_qubits = num_qubits


class BQJobDoesNotContainCountsError(BQError):
    def __init__(self, job_id):
        super().__init__(f"The job {job_id} result metadata doesn't contain counts.")
        self.job_id = job_id


class BQJobNotCompleteError(BQError):
    def __init__(self, job_id, run_status, error_message):
        super().__init__(
            f"Job {job_id} finished with status: {run_status}. {error_message}",
        )
        self.job_id = job_id
        self.run_status = run_status
        self.error_message = error_message


class BQJobHasNotFinishedYetError(BQError):
    def __init__(self, job_id, run_status):
        super().__init__(
            f"Job {job_id} has not finished yet. Current status: {run_status}.",
        )
        self.job_id = job_id
        self.run_status = run_status


class BQJobCouldNotCancelError(BQError):
    def __init__(self, job_id, run_status, error_message):
        super().__init__(
            (
                f"Couldn't cancel job {job_id}. Finished status is {run_status}."
                f" {error_message}"
            ),
        )
        self.job_id = job_id
        self.run_status = run_status


class BQBatchJobsLimitExceededError(BQError):
    def __init__(self, num):
        super().__init__(
            "Batch operations job count limit exceeded. The maximum is"
            f" {job_metadata_constants.MAXIMUM_NUMBER_OF_BATCH_JOBS}, but {num} was"
            " used."
        )
        self.num = num


class BQAPIError(BQError):
    def __init__(self, http_status_code, error_message):
        super().__init__(
            f"{error_message}. HTTP response status code: {http_status_code}.",
        )
        self.http_status_code = http_status_code
        self.error_message = error_message


class BQJobInvalidDeviceTypeError(BQError):
    def __init__(self, device):
        super().__init__(
            f"Invalid device type {device}. Must be one of"
            f" {', '.join(job_metadata_constants.DEVICE_TYPES)}."
        )
