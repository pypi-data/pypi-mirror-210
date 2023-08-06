import braket.circuits
import cirq
import pytest
import qiskit

from bluequbit import circuit_serialization


def test_cirq():
    qc_cirq = cirq.Circuit()
    qubits = cirq.LineQubit.range(2)
    qc_cirq.append(cirq.H(qubits[0]))
    qc_cirq.append(cirq.X(qubits[1]))

    encoded_cirq = circuit_serialization.encode_circuit(qc_cirq)
    decoded_cirq = circuit_serialization.decode_circuit(encoded_cirq)
    all_ops = list(decoded_cirq.all_operations())
    # Check that we recover the original circuit
    assert len(all_ops) == 2
    assert isinstance(all_ops[0].gate, cirq.ops.HPowGate), all_ops[0].gate
    assert isinstance(all_ops[1].gate, cirq.ops.XPowGate), all_ops[0].gate


def test_cirq_oq2():
    qs = cirq.LineQubit.range(2)
    circuit = cirq.Circuit([cirq.ry(0.5).on(qs[1]).controlled_by(qs[0])])

    # If we encode normally, we should see "ProductOfSums" in the output.
    encoded_cirq = circuit_serialization.encode_circuit(circuit)
    assert "ProductOfSums" in encoded_cirq["circuit"]

    # If we use OQ2, there should be none, because it's not in OpenQASM spec.
    encoded_cirq = circuit_serialization.encode_circuit(circuit, use_cirq_qasm=True)
    assert "ProductOfSums" not in encoded_cirq["circuit"]

    decoded_cirq = circuit_serialization.decode_circuit(encoded_cirq)
    all_ops = list(decoded_cirq.all_operations())
    # The cirq.ry is expanded into 5 operations
    assert len(all_ops) == 5
    assert isinstance(all_ops[0].gate, cirq.circuits.qasm_output.QasmUGate), all_ops[
        0
    ].gate


def test_qiskit():
    qc_qiskit = qiskit.QuantumCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.x(1)

    encoded_qiskit = circuit_serialization.encode_circuit(qc_qiskit)
    decoded_qiskit = circuit_serialization.decode_circuit(encoded_qiskit)
    qc = decoded_qiskit
    assert qc.data[0].operation.name == "h"
    assert qc.data[1].operation.name == "x"


def test_braket():
    qc_braket = braket.circuits.Circuit().h(0).x(1)
    encoded_braket = circuit_serialization.encode_circuit(qc_braket)
    assert (
        encoded_braket["circuit"]
        == "OPENQASM 3.0;\nbit[2] b;\nqubit[2] q;\nh q[0];\nx q[1];\nb[0] = measure"
        " q[0];\nb[1] = measure q[1];"
    )
    with pytest.raises(Exception, match="Braket decoding is not yet supported."):
        circuit_serialization.decode_circuit(encoded_braket)


def test_unsupported():
    wrong = {}
    with pytest.raises(Exception) as e_info:
        circuit_serialization.encode_circuit(wrong)
        assert e_info == Exception("Unsupported circuit type", wrong)
    with pytest.raises(
        Exception, match="Wrong data structure. 'circuit_type' must be present."
    ):
        circuit_serialization.decode_circuit({})
    with pytest.raises(
        Exception, match="Wrong data structure. 'circuit' must be present."
    ):
        circuit_serialization.decode_circuit({"circuit_type": "Qiskit"})
