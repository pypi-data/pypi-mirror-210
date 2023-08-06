
# quao 

quao is a supporting library for Quantum Computing.



## Installation

Install quao with pip (Python >=3.10)

```bash
  pip install quao
```
    
## Usage/Examples

```javascript
from quao import Backend, RequestData, Utils

# Define sdk name
sdk = "qiskit"

# Pre-processing input data
def pre_process(input):
    data = RequestData(input, sdk)
    return data

# Post-processing output data
def post_process(job):
    output = Utils.counts_post_process(job)
    return output


def handle(event, context):
    # 1. Pre-processing
    requestData = pre_process(event)

    # 2. Generate Quantum Circuit
    qc = generate_circuit(requestData.input)

    # 3. Verify and get Backend information
    backend = Backend(requestData, qc)

    # 4. Submit job and wait up to 1 min for job to complete.
    job = backend.submit_job(qc)

    # 5. Post-process
    if job.jobResult:
        job = post_process(job)
    response = Utils.generate_response(job)

    # 6. Send back the result
    return response
```


## Authors

- [CITYNOW Co. Ltd.](https://citynow.vn/)


## Documentation

TBA

