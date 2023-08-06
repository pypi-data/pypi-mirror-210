from ..utilities import JobStatus, JobResponse
from braket.devices import LocalSimulator
import strangeworks
from strangeworks.braket import get_backends, run_circuit, get_circuit_results


class BraketFaaS:
    def __init__(self, backendData: dict):
        self.token = backendData["providerToken"]
        self.swUser = backendData["backendInfo"].get("swUser")
        self.provider = backendData.get("provider")
        self.backendName = backendData["name"]

    def init_sw_provider(self):
        strangeworks.authenticate(username=self.swUser, api_key=self.token)

    def submit_job(self, qcircuit, shots):
        jobResult = {}
        if self.provider == "qfaas":
            backend = LocalSimulator()
            job = backend.run(qcircuit, shots=shots)
            jobResult = job.result()
            hub = "qfaas-internal"
        elif self.provider == "braket-sw":
            self.init_sw_provider()
            backend = self.backendName
            job = run_circuit(circuit=qcircuit, backend=backend, shots=shots)
            jobResult = get_circuit_results(job)
            hub = self.swUser
        if jobResult:
            jobStatus = JobStatus(
                "DONE",
                "Job is successfully executed on Local Simulator",
            )
            providerJobId = jobResult.task_metadata.id
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
            job_result=dict(jobResult.measurement_counts),
        )

        return jobResponse
