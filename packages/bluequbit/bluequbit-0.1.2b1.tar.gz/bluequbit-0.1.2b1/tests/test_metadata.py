import qiskit

import bluequbit


def test_metadata_json():
    dq_client = bluequbit.BQClient()
    qc_qiskit = qiskit.QuantumCircuit(3, 3)
    qc_qiskit.x(0)
    qc_qiskit.measure(0, 0)
    qc_qiskit.measure(1, 1)
    qc_qiskit.measure(2, 2)
    job_result = dq_client.run(qc_qiskit, job_name="testing")
    print(job_result.get_counts())

    assert job_result._metadata["has_measurements"] is True
    assert job_result._metadata["message"] is None
    assert job_result._metadata["top_128"] == {"001": 1.0}
    assert job_result._metadata["counts"] == {"001": 1.0}
    assert job_result._metadata["job_id"] == job_result.job_id
