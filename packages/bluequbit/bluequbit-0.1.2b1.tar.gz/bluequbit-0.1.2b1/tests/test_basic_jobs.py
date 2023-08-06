import datetime

import qiskit

import bluequbit


def test_basic_search_jobs():
    time_now = datetime.datetime.now(datetime.timezone.utc)
    dq_client = bluequbit.BQClient()
    # time_now = "2022-10-19T13:05:17.917290Z"
    qc_qiskit = qiskit.QuantumCircuit(2)
    qc_qiskit.h(0)
    qc_qiskit.x(1)
    job_result = dq_client.run(qc_qiskit, job_name="testing_basic_search_jobs")
    results = dq_client.search(
        run_status="COMPLETED",
        created_later_than=time_now - datetime.timedelta(seconds=10),
    )
    num_found = 0
    for result in results:
        if (
            job_result.job_id == result.job_id
            and job_result.job_name == "testing_basic_search_jobs"
        ):
            print(job_result)
            num_found += 1
            assert job_result.batch_id is None

    assert num_found == 1
