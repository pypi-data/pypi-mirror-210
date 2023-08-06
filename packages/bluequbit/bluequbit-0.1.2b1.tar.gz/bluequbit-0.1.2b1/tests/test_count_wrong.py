import os

import cirq
import numpy as np
import pytest

import bluequbit


@pytest.mark.skipif(
    "BLUEQUBIT_COUNT_BUG" not in os.environ,
    reason="Requires env variable to be set",
)
def test_count_wrong():
    bq = bluequbit.init()
    n = 26
    qc_cirq = cirq.testing.random_circuit(
        qubits=n, n_moments=50, op_density=1.0, random_state=1
    )

    measure_qubits = 1
    for _ in range(measure_qubits):
        qc_cirq.append(cirq.measure(cirq.NamedQubit("0")))

    device = "cpu"
    r0 = bq.run(
        qc_cirq, device=device, job_name=f"{n}_random_{measure_qubits}_{device}"
    )
    counts = r0.get_counts()
    assert len(counts) == 2
    sum_probs = 0.0
    for _, v in counts.items():
        sum_probs += v
    assert np.isclose(sum_probs, 1.0)
