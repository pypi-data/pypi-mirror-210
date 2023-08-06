import os
from datetime import datetime
from .test_execute import upload_graph
from .test_execute import get_events


def test_get_execution_events(local_exec_client):
    client, sclient = local_exec_client

    graph_name, expected = upload_graph(client)
    nevents = 0
    nevents_per_exec = 2 * (len(expected) + 2)

    # Test no events (nothing has been executed)
    response = client.get("/execution/events")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"jobs": list()}

    # Execute workflow
    response = client.post(f"/execute/{graph_name}")
    data = response.get_json()
    assert response.status_code == 200, data
    job_id1 = data["job_id"]
    nevents += nevents_per_exec

    # Wait until all events have been received over the websocket
    events1 = get_events(sclient, nevents, timeout=3)

    # Query should return the same a what was recieved over the websocket
    response = client.get("/execution/events")
    assert response.status_code == 200
    events = response.get_json()["jobs"]
    assert len(events) == 1
    assert events[0] == events1

    response = client.get(f"/execution/events?job_id={job_id1}")
    assert response.status_code == 200
    events = response.get_json()["jobs"]
    assert len(events) == 1
    assert events[0] == events1

    response = client.get("/execution/events?context=job")
    assert response.status_code == 200
    events = response.get_json()["jobs"]
    assert len(events) == 1
    assert len(events[0]) == 2

    dtmid = datetime.now().astimezone()

    # Execute workflow
    response = client.post(f"/execute/{graph_name}")
    data = response.get_json()
    assert response.status_code == 200, data
    job_id2 = data["job_id"]
    nevents += nevents_per_exec

    # Wait until all events have been received over the websocket
    events2 = get_events(sclient, nevents_per_exec, timeout=3)

    response = client.get("/execution/events")
    assert response.status_code == 200
    events = response.get_json()["jobs"]
    assert len(events) == 2
    assert events[0] == events1
    assert events[1] == events2

    response = client.get(f"/execution/events?job_id={job_id2}")
    assert response.status_code == 200
    events = response.get_json()["jobs"]
    assert len(events) == 1
    assert events[0] == events2

    response = client.get("/execution/events?context=job")
    assert response.status_code == 200
    events = response.get_json()["jobs"]
    assert len(events) == 2
    assert len(events[0]) == 2
    assert len(events[1]) == 2

    if os.name == "nt":
        return  # TODO: time filtering fails on windows

    # Test time Query
    midtime = dtmid.isoformat().replace("+", "%2b")
    response = client.get(f"/execution/events?endtime={midtime}")
    assert response.status_code == 200
    events = response.get_json()["jobs"]
    assert len(events) == 1
    assert events[0] == events1

    response = client.get(f"/execution/events?starttime={midtime}")
    assert response.status_code == 200
    events = response.get_json()["jobs"]
    assert len(events) == 1
    assert events[0] == events2
