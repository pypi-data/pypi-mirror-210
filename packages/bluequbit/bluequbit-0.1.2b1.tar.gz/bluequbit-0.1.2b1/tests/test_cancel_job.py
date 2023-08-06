import numpy as np
import pytest
import qiskit

import bluequbit

num_qubits = 30
qc_qiskit1 = qiskit.QuantumCircuit(num_qubits)
qc_qiskit1.x(np.arange(num_qubits))


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_long_running_cancel_job():
    dq_client = bluequbit.BQClient()

    r = dq_client.run(qc_qiskit1, asynchronous=True)
    for _ in range(1200):
        res = dq_client.get(r.job_id)
        if res.run_status == "RUNNING":
            break
    else:
        raise AssertionError()

    r = dq_client.cancel(r.job_id)
    assert r.run_status == "CANCELED"
    assert r.error_message == "Canceled by user"
