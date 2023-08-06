import numpy as np
import pytest
import qiskit

import bluequbit


def test_basic_large_jobs():
    qc = qiskit.QuantumCircuit(24)
    qc.x(np.arange(24))

    dq_client1 = bluequbit.BQClient()
    result1 = dq_client1.run(qc, asynchronous=True)

    dq_client2 = bluequbit.BQClient()
    result2 = dq_client2.run(qc, asynchronous=True)

    res1 = dq_client1.wait(result1.job_id)
    assert res1.run_status == "COMPLETED"
    assert res1.error_message is None
    assert res1.job_id == result1.job_id
    print("Job1", res1)

    res2 = dq_client2.wait(result2.job_id)
    assert res2.run_status == "COMPLETED"
    assert res2.error_message is None
    assert res2.job_id == result2.job_id
    print("Job2", res2)
    print("Downloading job 2")
    with pytest.raises(bluequbit.exceptions.BQJobStatevectorTooLargeError) as e:
        res2.get_statevector()
    assert (
        e.value.message
        == f"Statevector is too large for {res2.num_qubits} qubits (job:"
        f" {res2.job_id}). Please use .get_counts() instead."
    )


def test_very_large_job():
    dq = bluequbit.BQClient()

    qc_qiskit = qiskit.QuantumCircuit(40)
    for i in range(40):
        qc_qiskit.h(i)
    qc_qiskit.cx(0, 1)

    with pytest.raises(bluequbit.exceptions.BQJobNotCompleteError) as e_info:
        dq.run(qc_qiskit)
    assert e_info.value.run_status == "FAILED_VALIDATION"


def test_very_large_job_but_unused_qubits():
    # Almost the same as test_very_large_job, except that most qubits are
    # unused.
    dq = bluequbit.BQClient()

    qc_qiskit = qiskit.QuantumCircuit(40)
    qc_qiskit.h(0)
    qc_qiskit.cx(0, 1)
    r0 = dq.run(qc_qiskit)
    assert r0.run_status == "COMPLETED"
