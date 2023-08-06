import numpy as np
import pytest
import qiskit

import bluequbit
from bluequbit import job_metadata_constants


def make_simple_circuit():
    qc_qiskit = qiskit.QuantumCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.x(1)
    return qc_qiskit


def test_job_estimation():
    dq_client = bluequbit.BQClient()
    qc_qiskit = make_simple_circuit()
    results = dq_client.estimate(qc_qiskit)
    assert results.estimated_runtime == 100


def test_job_estimation_wrong_device_type():
    dq_client = bluequbit.BQClient()
    qc_qiskit = make_simple_circuit()
    # Should work
    dq_client.estimate(qc_qiskit, device="CPU")

    # Should fail
    with pytest.raises(Exception) as e_info:
        dq_client.estimate(qc_qiskit, device="supercpu")
    expected = "Invalid device type supercpu. Must be one of " + ", ".join(
        job_metadata_constants.DEVICE_TYPES
    )
    print(e_info.value)
    assert expected in str(e_info.value)


def test_job_estimation_large():
    dq_client = bluequbit.BQClient()
    qc = qiskit.QuantumCircuit(24)
    qc.x(np.arange(24))
    results = dq_client.estimate(qc)
    assert results.estimated_runtime == 187
    # assert results.device == "qsim_simulator"
    assert results.num_qubits == 24
    assert (
        results.warning_message
        == "This is just an estimate; the actual runtime may be less or more."
    )


def test_job_estimate_validation_too_many_qubits():
    # Too many qubits
    dq_client = bluequbit.BQClient()
    qc = qiskit.QuantumCircuit(38)
    qc.x(np.arange(38))
    result = dq_client.estimate(qc)
    expected_message = (
        "Circuit contains more than 34 qubits, which is not supported for CPU backend."
        " See https://app.bluequbit.io/docs for more details."
    )
    assert expected_message in result.error_message

    with pytest.raises(bluequbit.exceptions.BQJobNotCompleteError) as e_info:
        dq_client.run(qc)
    assert e_info.value.run_status == "FAILED_VALIDATION"


def test_job_estimation_quantum():
    dq_client = bluequbit.BQClient()
    qc = qiskit.QuantumCircuit(24)
    qc.x(np.arange(24))
    qc.measure_all()
    results = dq_client.estimate(qc, device="quantum")

    assert results.estimated_runtime == 1
