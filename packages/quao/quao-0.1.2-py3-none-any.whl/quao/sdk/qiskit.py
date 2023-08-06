from qiskit import transpile
from qiskit_aer import Aer
from qiskit_ibm_runtime import QiskitRuntimeService, Options, Session, Sampler
import json

from ..utilities import JobResponse
from ..enum.providerType import ProviderType


class QiskitFaaS:

    def __init__(self, backend_data):
        self.device_name = backend_data.get("deviceName")
        self.provider_tag = backend_data.get("providerTag")
        self.connection = backend_data.get("authentication")

    def get_aer_backend(self):
        return Aer.get_backend(self.device_name)

    def get_ibm_provider(self, channel):
        token = self.connection.get("token")
        instance = self.connection.get("crn")

        return QiskitRuntimeService(channel=channel, token=token, instance=instance)

    def run_circuit_on_ibm(self, provider, circuit, shots):
        options = Options(optimization_level=1)
        options.execution.shots = shots

        with Session(service=provider, backend=self.device_name) as session:
            sampler = Sampler(session=session, options=options)
            job = sampler.run(circuits=circuit)

            return job

    def is_simulator(self, provider):
        backend = provider.get_backend(self.device_name)
        return backend.configuration().simulator

    def run_ibm_job(self, channel, circuit, shots) -> JobResponse:
        provider_job_id = ''
        try:
            provider = self.get_ibm_provider(channel=channel)
            job = self.run_circuit_on_ibm(provider=provider, circuit=circuit, shots=shots)
            provider_job_id = job.job_id()
            job_status = job.status().name
            job_result = {}
            if self.is_simulator(provider) or job_status == "DONE":
                job_result = job.result().to_dict()
                job_status = job.status().name

        except Exception as exception:
            job_result = {
                "error": "Exception when invoke job on " + channel + " provider",
                "exception": str(exception)
            }
            job_status = "ERROR"

        return JobResponse(
            provider_job_id=provider_job_id,
            job_status=job_status,
            job_result=json.dumps(job_result)
        )

    def submit_job(self, qcircuit, shots) -> JobResponse:
        if self.provider_tag == ProviderType.QUAO_QUANTUM_SIMULATOR.value:
            try:
                backend = self.get_aer_backend()
                transpile_circuit = transpile(qcircuit, backend)

                job = backend.run(transpile_circuit, shots=shots)
                job_result = job.result().to_dict()
                job_status = job.status().name
            except Exception as exception:
                job_result = {
                    "error": "Exception when invoke job with Quao provider",
                    "exception": str(exception)
                }
                job_status = "ERROR"
            return JobResponse(
                provider_job_id="Internal-Qiskit-Simulation-Job",
                job_status=job_status,
                job_result=json.dumps(job_result),
            )
        elif self.provider_tag == ProviderType.IBM_QUANTUM.value:
            return self.run_ibm_job(channel="ibm_quantum", circuit=qcircuit, shots=shots)
        elif self.provider_tag == ProviderType.IBM_CLOUD.value:
            return self.run_ibm_job(channel="ibm_cloud", circuit=qcircuit, shots=shots)

        return JobResponse(
            job_status="ERROR",
            job_result=json.dumps({"error": "Provider not supported"})
        )
