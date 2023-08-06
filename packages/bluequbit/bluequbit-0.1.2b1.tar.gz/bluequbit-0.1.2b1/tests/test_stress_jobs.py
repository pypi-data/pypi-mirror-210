import threading

import qiskit

import bluequbit

NUM_PER_THREAD = 2
NUM_THREADS = 2

qc_qiskit = qiskit.QuantumCircuit(2)
qc_qiskit.h(0)
qc_qiskit.x(1)

job_ids = [[] for _ in range(NUM_THREADS)]


def submit_task(dq_client, thread_no):
    for _ in range(NUM_PER_THREAD):
        job_ids[thread_no].append(dq_client.run(qc_qiskit, asynchronous=True).job_id)


def test_stress_submit_jobs():
    dq_client = bluequbit.BQClient()
    threads = []
    for i in range(NUM_THREADS):
        threads.append(
            threading.Thread(
                target=submit_task,
                args=(
                    dq_client,
                    i,
                ),
            )
        )
        threads[-1].start()

    for i in range(NUM_THREADS):
        threads[i].join()

    job_ids_flat = [item for sublist in job_ids for item in sublist]

    assert len(job_ids_flat) == NUM_THREADS * NUM_PER_THREAD

    dq_client = bluequbit.BQClient()
    for job_id in job_ids_flat:
        job_result = dq_client.wait(job_id)
        assert job_result.run_status == "COMPLETED"
        assert job_result.error_message is None
