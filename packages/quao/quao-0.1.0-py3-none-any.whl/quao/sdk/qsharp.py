from ..utilities import JobResponse

import qsharp


class QsharpFaaS:
    def __init__(self, backendData: dict):
        self.token = backendData["providerToken"]
        self.swUser = backendData["backendInfo"].get("swUser")
        self.provider = backendData.get("provider")
        self.backendName = backendData["name"]

    def submit_job(self, qcircuit, input):
        jobResult = {}
        if self.provider == "qfaas":
            job = qcircuit.simulate(input=input)
            jobResult = {"data": job}
            hub = "qfaas-internal"

        if jobResult:
            jobStatus = JobStatus(
                "DONE",
                "Job is successfully executed on Local Simulator",
            )
            providerJobId = "QFaaS-Internal-QSharp-Simulation-Job"
        else:
            jobStatus = JobStatus("FAILED", "Job is failed")
            providerJobId = ""

        jobResponse = JobResponse(
            provider_job_id=providerJobId,
            job_status=jobStatus,
            backend={
                "name": self.backendName,
                "hub": hub,
            },
            job_result=jobResult,
        )
        return jobResponse
