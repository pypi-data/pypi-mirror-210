import qiskit
import requests

import bluequbit


def test_get_job():
    dq_client = bluequbit.init()
    qc_qiskit = qiskit.QuantumCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.x(1)
    result = dq_client.run(qc_qiskit)

    assert result.num_qubits == 2
    print(result)

    assert result._results_path is not None

    response = requests.get(result._results_path + "statevector.txt", timeout=60.0)
    assert len(response.content) == 326

    assert result.get_statevector().shape == (4,)
    assert len(result.get_counts()) == 2
