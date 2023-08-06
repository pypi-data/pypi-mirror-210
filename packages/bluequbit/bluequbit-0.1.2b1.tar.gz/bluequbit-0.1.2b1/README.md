![lint and tests](https://github.com/BlueQubitDev/bluequbit-python-sdk/actions/workflows/lint_and_tests.yml/badge.svg) ![PyPI release status](https://github.com/BlueQubitDev/bluequbit-python-sdk/actions/workflows/release.yml/badge.svg) ![Deploy docs](https://github.com/BlueQubitDev/bluequbit-python-sdk/actions/workflows/deploy_docs.yml/badge.svg)

# BlueQubit Python SDK

## Quick Start

1. Register on https://app.bluequbit.io and copy the API token.

2. Install Python SDK from PyPI:
```
    pip install bluequbit
```
3. An example of how to run a Qiskit circuit using the SDK:

```
    import qiskit

    import bluequbit

    bq_client = bluequbit.init("<token>")

    qc_qiskit = qiskit.QuantumCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.x(1)

    job_result = bq_client.run(qc_qiskit, job_name="testing_1")

    state_vector = job_result.get_statevector() 
    # returns a NumPy array of [0. +0.j 0. +0.j 0.70710677+0.j 0.70710677+0.j]
```

The packages is tested extensively on Python 3.8.

## Full reference

Please find detailed reference at https://app.bluequbit.io/sdk-docs.

## Questions and Issues

Please submit questions and issues to info@bluequbit.io.
