import time
from ewokscore.tests.examples.graphs import get_graph


def test_execute_with_celery(celery_exec_client):
    _test_execute(*celery_exec_client)


def test_execute_without_celery(local_exec_client):
    _test_execute(*local_exec_client)


def test_new_client_new_events(local_exec_client):
    client, sclient = local_exec_client
    _test_execute(client, sclient)
    sclient.disconnect()
    sclient.connect()
    time.sleep(1)
    assert not sclient.get_received()


def _test_execute(client, sclient):
    graph_name, expected = upload_graph(client)
    response = client.post(f"/execute/{graph_name}")
    assert response.status_code == 200, response.get_json()

    n = 2 * (len(expected) + 2)
    events = get_events(sclient, n)
    _assert_events(response, events, expected)
    return n


def upload_graph(client):
    graph_name = "acyclic1"
    graph, expected = get_graph(graph_name)
    response = client.post("/workflows", json=graph)
    assert response.status_code == 200, response.get_json()
    return graph_name, expected


def get_events(sclient, nevents, timeout=3):
    t0 = time.time()
    events = list()
    while True:
        new_events = sclient.get_received()
        events.extend(new_events)
        if len(events) == nevents:
            break
        time.sleep(0.1)
        if time.time() - t0 > timeout:
            break

    ewoks_events = list()
    for flask_event in events:
        ewoks_events.extend(flask_event["args"])
    return ewoks_events


def _assert_events(response, events, expected):
    n = 2 * (len(expected) + 2)
    assert len(events) == n

    job_id = response.get_json()["job_id"]
    for event in events:
        assert event["job_id"] == job_id
        if event["node_id"]:
            assert event["node_id"] in expected
