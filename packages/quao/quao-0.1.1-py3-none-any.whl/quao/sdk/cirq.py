from ..utilities import JobStatus, JobResponse

import cirq


class CirqFaaS:
    def __init__(self, backendData: dict):
        self.token = backendData["providerToken"]
        self.swUser = backendData["backendInfo"].get("swUser")
        self.provider = backendData.get("provider")
        self.backendName = backendData["name"]

    def submit_job(self, qcircuit, shots):
        jobResult = {}
        if self.provider == "qfaas":
            simulator = cirq.Simulator()
            job = simulator.run(qcircuit, repetitions=shots)
            jobData = job.data
            # Get counts (export the result similar to Qiskit and Braket)
            jobResult = self.get_counts(jobData)
            hub = "qfaas-internal"

        if jobResult:
            jobStatus = JobStatus(
                "DONE",
                "Job is successfully executed on Local Simulator",
            )
            providerJobId = "QFaaS-Internal-Cirq-Simulation-Job"
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

    def get_counts(self, jobData) -> dict:
        jobData["result"] = jobData.apply(lambda x: "".join(x.astype(str)), 1)
        counts = jobData.groupby(["result"]).size()
        countsDict = counts.to_dict()
        return countsDict
