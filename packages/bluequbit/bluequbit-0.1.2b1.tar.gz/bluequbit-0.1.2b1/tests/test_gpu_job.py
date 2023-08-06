import os
import time

import cirq
import pytest
import qiskit

import bluequbit


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ, reason="Requires env variable to be set"
)
def test_gpu_job():
    dq_client = bluequbit.BQClient()
    # time_now = "2022-10-19T13:05:17.917290Z"
    n = 10  # will get to GPU1
    qc_qiskit = qiskit.QuantumCircuit(n)
    for i in range(n):
        qc_qiskit.h(i)
    qc_qiskit.measure_all()

    job_result = dq_client.run(qc_qiskit, job_name="testing_gpu_qiskit", device="gpu")
    print(job_result)

    assert job_result.run_status == "COMPLETED"


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ,
    reason="Requires env variable to be set",
)
@pytest.mark.order(2)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_gpu_job_cirq_measure_gpu1():
    dq_client = bluequbit.BQClient()
    num_qubits = 32
    qc_cirq = cirq.Circuit()
    qubits = cirq.LineQubit.range(num_qubits)
    for i in range(num_qubits):
        qc_cirq.append(cirq.H(qubits[i]))
    job_result = dq_client.run(qc_cirq, job_name="testing_gpu_cirq_meas", device="gpu")
    assert job_result.run_status == "COMPLETED"
    print(job_result)

    assert job_result.run_time_ms < 13000  # tests 12651, 12708, 12683


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ
    and "BLUEQUBIT_FORCE_GPU2_TEST" not in os.environ,
    reason="Requires env variable to be set",
)
@pytest.mark.order(1)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_gpu_job_cirq_measure_gpu2():
    dq_client = bluequbit.BQClient()
    num_qubits = 33
    qc_cirq = cirq.Circuit()
    qubits = cirq.LineQubit.range(num_qubits)
    for i in range(num_qubits):
        qc_cirq.append(cirq.H(qubits[i]))
    job_result = dq_client.run(qc_cirq, job_name="testing_gpu_cirq_meas", device="gpu")
    assert job_result.run_status == "COMPLETED"
    print(job_result)

    assert job_result.run_time_ms < 13300  # tests 12994, 12976, 13071


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ, reason="Requires env variable to be set"
)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_gpu_job_cirq_measure_gpu4():
    dq_client = bluequbit.BQClient()
    num_qubits = 34
    qc_cirq = cirq.Circuit()
    qubits = cirq.LineQubit.range(num_qubits)
    for i in range(num_qubits):
        qc_cirq.append(cirq.H(qubits[i]))
    job_result = dq_client.run(qc_cirq, job_name="testing_gpu_cirq_meas", device="gpu")
    assert job_result.run_status == "COMPLETED"
    print(job_result)

    assert job_result.run_time_ms < 14000  # tests: 13726, 13743, 13728


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ, reason="Requires env variable to be set"
)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_gpu_job_cirq_measure_gpu8():
    dq_client = bluequbit.BQClient()
    n = 35
    qc = cirq.Circuit()
    qs = cirq.LineQubit.range(n)
    for i in range(n):
        qc.append(cirq.H(qs[i]))
    qc.append(cirq.measure(qs))
    job_result = dq_client.run(qc, job_name="testing_gpu_cirq", device="gpu")
    assert job_result.run_status == "COMPLETED"
    assert job_result.run_time_ms < 15500  # tests: 15128, 15131, 15275
    print(job_result)


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ, reason="Requires env variable to be set"
)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_gpu_job_cirq_measure_gpu16():
    dq_client = bluequbit.BQClient()
    n = 36
    qc = cirq.Circuit()
    qs = cirq.LineQubit.range(n)
    for i in range(n):
        qc.append(cirq.H(qs[i]))
    qc.append(cirq.measure(qs))
    job_result = dq_client.run(qc, job_name="testing_gpu_cirq", device="gpu")
    assert job_result.run_status == "COMPLETED"
    print(job_result)


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ, reason="Requires env variable to be set"
)
def test_gpu_job_cirq_8gpu_issue():
    dq_client = bluequbit.BQClient()
    n = 35
    qc = cirq.Circuit()
    qs = cirq.LineQubit.range(n)
    for i in range(n):
        qc.append(cirq.H(qs[i]))
    qc.append(cirq.measure(qs))
    r = dq_client.run(qc, job_name="testing_gpu_cirq", device="gpu", asynchronous=True)
    for _ in range(1200):
        res = dq_client.get(r.job_id)
        if res.run_status == "RUNNING":
            break
        time.sleep(1)
    else:
        raise AssertionError()

    time.sleep(10)
    r = dq_client.cancel(r.job_id)
    assert r.run_status == "CANCELED"
