from typing import List

from ewoksutils import event_utils

from ..utils import Resource
from .. import api
from ...events.ewoks_events import reader_context


class ExecutionEvents(Resource):
    @api.get_ewoks_events()
    def get(self, **filters) -> List[List[dict]]:
        jobs = list()
        job = None
        job_id = None
        with reader_context() as reader:
            if reader is None:
                raise RuntimeError("server not configured for ewoks events")
            for event in reader.get_events(**filters):
                if event["job_id"] != job_id:
                    job_id = event["job_id"]
                    job = list()
                    jobs.append(job)
                if "engine" in event_utils.FIELD_TYPES:
                    event["binding"] = event["engine"]
                job.append(event)
        return {"jobs": jobs}, 200
