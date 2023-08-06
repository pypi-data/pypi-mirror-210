import os

import numpy as np
import pytest
import qiskit

import bluequbit


@pytest.mark.skipif(
    "BLUEQUBIT_STRESS_TESTS" not in os.environ, reason="Requires env variable to be set"
)
def test_long_running_cancel_job():
    dq_client = bluequbit.BQClient()
    num_qubits = 29
    qc_qiskit = qiskit.QuantumCircuit(num_qubits)
    qc_qiskit.x(np.arange(num_qubits))

    with pytest.raises(bluequbit.exceptions.BQJobNotCompleteError) as e:
        dq_client.run(qc_qiskit)
    assert e.value.run_status == "TERMINATED"
