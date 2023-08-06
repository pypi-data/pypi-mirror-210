import datetime
import os

import numpy as np
import pytest
import qiskit

import bluequbit


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ, reason="Requires env variable to be set"
)
def test_quantum_job():
    dq_client = bluequbit.BQClient()
    # time_now = "2022-10-19T13:05:17.917290Z"
    qc_qiskit = qiskit.QuantumCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.x(1)
    qc_qiskit.measure_all()
    job_result = dq_client.run(
        qc_qiskit, job_name="testing_quantum", device="quantum", shots=50
    )
    assert job_result.error_message is None
    assert job_result.run_status == "COMPLETED"
    assert job_result.device == "quantum"
    actual = sum(job_result.get_counts().values())
    assert actual == 50

    counts = job_result.get_counts()
    print(counts)
    total_counts = 0
    for _, v in counts.items():
        total_counts += v
    assert total_counts == 50


def test_quantum_job_no_measurement():
    dq_client = bluequbit.BQClient()
    qc_qiskit = qiskit.QuantumCircuit(2)
    qc_qiskit.h(0)

    with pytest.raises(bluequbit.exceptions.BQJobNotCompleteError) as e_info:
        dq_client.run(qc_qiskit, job_name="testing_quantum", device="quantum")
    assert e_info.value.run_status == "FAILED_VALIDATION"


def check_aspen_time_availability():
    time_now_hour = datetime.datetime.now(datetime.timezone.utc).hour
    if (time_now_hour >= 4 and time_now_hour < 6) or (
        time_now_hour >= 15 and time_now_hour < 18
    ):
        return True
    return False


@pytest.mark.skipif(
    check_aspen_time_availability(), reason="Requires env variable to be set"
)
def test_quantum_job_when_aspen_not_available():
    dq_client = bluequbit.BQClient()
    # time_now = "2022-10-19T13:05:17.917290Z"
    num_qubits = 30
    qc_qiskit = qiskit.QuantumCircuit(num_qubits)
    qc_qiskit.x(np.arange(num_qubits))
    qc_qiskit.measure_all()
    with pytest.raises(bluequbit.exceptions.BQJobNotCompleteError) as e_info:
        dq_client.run(qc_qiskit, job_name="testing_quantum", device="quantum")
    assert e_info.value.run_status == "FAILED_VALIDATION"


@pytest.mark.skipif(
    check_aspen_time_availability() or "BLUEQUBIT_STRESS_TESTS" not in os.environ,
    reason="Requires env variable to be set",
)
def test_quantum_async_job_when_aspen_not_available():
    dq_client = bluequbit.BQClient()
    # time_now = "2022-10-19T13:05:17.917290Z"
    num_qubits = 30
    qc_qiskit = qiskit.QuantumCircuit(num_qubits)
    qc_qiskit.x(np.arange(num_qubits))
    qc_qiskit.measure_all()
    job_result = dq_client.run(
        qc_qiskit, job_name="testing_quantum_async", device="quantum", asynchronous=True
    )
    assert job_result.run_status != "FAILED_VALIDATION"


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ, reason="Requires env variable to be set"
)
def test_cancel_quantum_job():
    dq_client = bluequbit.BQClient()
    # time_now = "2022-10-19T13:05:17.917290Z"
    num_qubits = 30
    qc_qiskit = qiskit.QuantumCircuit(num_qubits)
    qc_qiskit.x(np.arange(num_qubits))
    qc_qiskit.measure_all()
    job_result = dq_client.run(
        qc_qiskit, job_name="testing_quantum", device="quantum", asynchronous=True
    )
    job_result = dq_client.cancel(job_result.job_id)

    assert job_result.run_status == "CANCELED"
