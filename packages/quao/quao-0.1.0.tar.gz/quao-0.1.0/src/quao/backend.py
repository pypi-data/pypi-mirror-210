from json import JSONDecodeError

import requests

from .dataUtils import RequestData
from .utilities import JobResponse


class Backend:
    def __init__(self, request_data: RequestData, circuit):
        self.server_url = request_data.server_url
        self.sdk = request_data.sdk
        self.input = request_data.input
        self.shots = request_data.shots
        self.required_qubit = self.get_qubit_number(circuit)
        self.backend_request = self.generate_backend_request(request_data.device_id)
        # Get backend data from server
        self.backend_data = self.get_backend_data()

    def get_qubit_number(self, circuit) -> int:

        if self.sdk == "qiskit":
            return int(circuit.num_qubits)
        if self.sdk == "braket":
            return int(circuit.qubit_count)
        if self.sdk == "cirq":
            return int(len(circuit.all_qubits()))
        return 0
        # if self.sdk == "qsharp":
        # return int(self.input)  # Temporarily

    def generate_backend_request(self, device_id):

        backend_request = {
            "deviceId": device_id,
            "qubitAmount": self.required_qubit
        }

        return backend_request

    def get_backend_data(self):
        response = requests.get(
            self.server_url,
            params=self.backend_request
        )
        if response.status_code == 200:
            try:
                backend_data = response.json().get("data")
            except JSONDecodeError:
                return None
            return backend_data
        else:
            return None

    def submit_job(self, circuit, interval: int = 3, timeout: int = 30) -> JobResponse:
        job_response = JobResponse()
        shots = self.shots
        if circuit and self.backend_data and 0 < interval <= timeout:
            if self.sdk == "qiskit":
                from .sdk.qiskit import QiskitFaaS

                be_instance = QiskitFaaS(self.backend_data)
                job_response = be_instance.submit_job(circuit, shots=shots)
            elif self.sdk == "braket":
                from .sdk.braket import BraketFaaS

                be_instance = BraketFaaS(self.backend_data)
                job_response = be_instance.submit_job(circuit, shots=shots)
            elif self.sdk == "cirq":
                from .sdk.cirq import CirqFaaS

                be_instance = CirqFaaS(self.backend_data)
                job_response = be_instance.submit_job(circuit, shots=shots)
            elif self.sdk == "q#":
                from .sdk.qsharp import QsharpFaaS

                be_instance = QsharpFaaS(self.backend_data)
                job_response = be_instance.submit_job(circuit, self.input)
        elif self.backend_data is None:
            job_response.job_status = "ERROR"
        return job_response


