import qiskit

import bluequbit


def test_ok():
    dq_client = bluequbit.BQClient()
    # time_now = "2022-10-19T13:05:17.917290Z"
    qc_qiskit = qiskit.QuantumCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.x(1)
    job_result = dq_client.run(qc_qiskit, job_name="testing")

    assert job_result.ok
