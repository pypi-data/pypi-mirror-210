import datetime
import json
import logging
import zlib

import dateutil.parser

from ..circuit_serialization import encode_circuit
from ..exceptions import BQAPIError, BQError

logger = logging.getLogger("bluequbit-python-sdk")

_SINGLE_REQUEST_LIMIT = 100


def search_jobs(
    _connection, run_status=None, created_later_than=None, job_ids=None, batch_id=None
):
    if created_later_than is None:
        parsed_created_later_than = None
    elif isinstance(created_later_than, str):
        parsed_created_later_than = dateutil.parser.parse(created_later_than)
        if parsed_created_later_than.tzinfo is None:
            logger.warning(
                "created_later_than is a str object without timezone info, assuming UTC"
                " timezone"
            )
            parsed_created_later_than = parsed_created_later_than.replace(
                tzinfo=datetime.timezone.utc
            )
        parsed_created_later_than = parsed_created_later_than.isoformat()
    elif isinstance(created_later_than, datetime.datetime):
        if created_later_than.tzinfo is None:
            raise BQError(
                "created_later_than is a datetime object without timezone info"
            )
        parsed_created_later_than = created_later_than.isoformat()
    else:
        raise BQError(
            "created_later_than should be None, str, or datetime.datetime object"
        )

    params = {
        "limit": _SINGLE_REQUEST_LIMIT,
        "run_status": run_status,
        "created_later_than": parsed_created_later_than,
        "job_ids": job_ids,
        "batch_id": batch_id,
    }
    result_dict = {"data": []}
    while True:
        response = _connection.send_request(req_type="GET", path="/jobs", params=params)
        if not response.ok:
            raise BQAPIError(
                response.status_code, "Couldn't search jobs " + response.text
            )
        response = response.json()

        results = response["data"]
        result_dict["data"] += results
        result_dict["total_count"] = response["total_count"]

        if len(results) < _SINGLE_REQUEST_LIMIT:
            break

        params["offset"] = len(result_dict["data"])
    return result_dict


def submit_jobs(
    _connection,
    circuits,
    device,
    job_name=None,
    estimate_only=False,
    shots=None,
    asynchronous=False,
):
    if isinstance(circuits, list):
        encoded_circuits = [encode_circuit(circuit) for circuit in circuits]
    else:
        encoded_circuits = encode_circuit(circuits)

    params = {
        "estimate_only": estimate_only,
        "circuit": encoded_circuits,
        "job_name": job_name,
        "device": device,
        "shots": shots,
        "asynchronous": asynchronous,
    }
    data = json.dumps(params)
    if len(data) > 2000:
        data = zlib.compress(data.encode())
        headers = {"content-encoding": "gzip"}
    else:
        headers = {"content-type": "application/json"}
    response = _connection.send_request(
        req_type="POST", path="/jobs", data=data, headers=headers
    )
    if not response.ok:
        raise BQAPIError(response.status_code, "Couldn't submit jobs " + response.text)
    return response.json()["data"]


def cancel_jobs(_connection, job_ids):
    response = _connection.send_request(
        req_type="PATCH", path="/jobs", json_req={"job_ids": job_ids, "cancel": True}
    )
    if not response.ok:
        raise BQAPIError(response.status_code, "Couldn't cancel jobs " + response.text)
    return response.json()["data"]
