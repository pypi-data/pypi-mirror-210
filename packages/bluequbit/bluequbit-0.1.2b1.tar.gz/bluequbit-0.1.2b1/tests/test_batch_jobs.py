import datetime
import os

import numpy as np
import pytest
import qiskit

import bluequbit

qc_qiskit1 = qiskit.QuantumCircuit(2)
qc_qiskit1.h(0)
qc_qiskit1.x(1)
qc_qiskit2 = qiskit.QuantumCircuit(2)
qc_qiskit2.x(0)
qc_qiskit2.h(1)


def test_batch_jobs():
    time_now = datetime.datetime.now(datetime.timezone.utc)
    dq_client = bluequbit.BQClient()
    job_results = dq_client.run([qc_qiskit1, qc_qiskit2], job_name="testing_batch_jobs")
    expected = {
        ("testing_batch_jobs_0", job_results[0].job_id),
        (("testing_batch_jobs_1", job_results[1].job_id)),
    }
    results = dq_client.search(
        run_status="COMPLETED",
        created_later_than=time_now - datetime.timedelta(seconds=10),
    )
    num_found = 0
    for jr in results:
        if (jr.job_name, jr.job_id) in expected:
            num_found += 1
            assert jr.batch_id is not None
            expected.remove((jr.job_name, jr.job_id))

    assert num_found == 2


def test_batch_jobs_exceed_max():
    dq_client = bluequbit.BQClient()
    with pytest.raises(bluequbit.exceptions.BQBatchJobsLimitExceededError) as e_info:
        dq_client.run([qc_qiskit1] * 501, job_name="testing_batch_jobs")
    assert e_info.value.num == 501


def test_batch_job_estimation():
    dq_client = bluequbit.BQClient()
    results = dq_client.estimate([qc_qiskit1, qc_qiskit2])
    for result in results:
        assert result.estimated_runtime == 100


def test_batch_jobs_wait_get():
    dq_client = bluequbit.BQClient()
    job_results = dq_client.run(
        [qc_qiskit1, qc_qiskit2], job_name="testing_batch_jobs_async", asynchronous=True
    )
    expected = {
        ("testing_batch_jobs_async_0", job_results[0].job_id),
        (("testing_batch_jobs_async_1", job_results[1].job_id)),
    }
    results = dq_client.wait(
        [
            job_results[0].job_id,
            job_results[1].job_id,
        ]
    )
    num_found = 0
    for jr in results:
        if (jr.job_name, jr.job_id) in expected:
            num_found += 1
            expected.remove((jr.job_name, jr.job_id))

    assert num_found == 2

    expected = {
        ("testing_batch_jobs_async_0", job_results[0].job_id),
        (("testing_batch_jobs_async_1", job_results[1].job_id)),
    }
    results = dq_client.get(
        [
            job_results[0].job_id,
            job_results[1].job_id,
        ]
    )
    num_found = 0
    for jr in results:
        if (jr.job_name, jr.job_id) in expected:
            num_found += 1
            expected.remove((jr.job_name, jr.job_id))

    assert num_found == 2


num_qubits = 29
qc_qiskit3 = qiskit.QuantumCircuit(num_qubits)
qc_qiskit3.x(np.arange(num_qubits))

qc_qiskit4 = qiskit.QuantumCircuit(num_qubits)
qc_qiskit4.h(np.arange(num_qubits))


@pytest.mark.skipif(
    "BLUEQUBIT_LOCAL_ENV_TESTS" not in os.environ,
    reason="Requires env variable to be set",
)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_long_running_batch_cancel_job1():
    dq_client = bluequbit.BQClient()
    results = dq_client.run([qc_qiskit3, qc_qiskit4], asynchronous=True)
    for _ in range(1200):
        res = dq_client.get([results[0].job_id, results[1].job_id])
        if res[0].run_status == "RUNNING" and res[1].run_status == "RUNNING":
            break
    else:
        raise AssertionError()

    r1 = dq_client.cancel(results[0].job_id)
    assert r1.run_status == "CANCELED"
    assert r1.error_message == "Canceled by user"

    with pytest.raises(bluequbit.exceptions.BQJobNotCompleteError):
        # This test should be run on local setup, in that case the second job
        # will be terminated due to memory issue, which is the expected behavior
        dq_client.wait(results[1].job_id)


@pytest.mark.skipif(
    "BLUEQUBIT_LOCAL_ENV_TESTS" not in os.environ,
    reason="Requires env variable to be set",
)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_long_running_batch_cancel_job2():
    dq_client = bluequbit.BQClient()
    results = dq_client.run([qc_qiskit3, qc_qiskit4], asynchronous=True)
    for _ in range(1200):
        res = dq_client.get([results[0].job_id, results[1].job_id])
        if res[0].run_status == "RUNNING" and res[1].run_status == "RUNNING":
            break
    else:
        raise AssertionError()

    r1 = dq_client.cancel([results[0].job_id, results[1].job_id])
    for r in r1:
        assert r.run_status == "CANCELED"
        assert r.error_message == "Canceled by user"


@pytest.mark.skipif(
    "BLUEQUBIT_LOCAL_ENV_TESTS" not in os.environ,
    reason="Requires env variable to be set",
)
def test_batch_jobs_many():
    dq_client = bluequbit.BQClient()
    job_results = dq_client.run(
        [qc_qiskit1, qc_qiskit2] * 10, job_name="testing_batch_jobs"
    )
    for jr in job_results:
        assert jr.run_status in ["COMPLETED", "JOBS_LIMIT_EXCEEDED"]

    assert len(job_results) == 20
