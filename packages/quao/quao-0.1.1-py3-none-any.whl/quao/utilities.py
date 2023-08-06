
class JobResponse(object):
    def __init__(
            self,
            provider_job_id: str = "",
            job_status: str = "",
            job_result=None,
    ):
        self.provider_job_id = provider_job_id if provider_job_id else ""
        self.job_status = job_status if job_status else "ERROR"
        self.job_result = job_result if job_result else None


class Utils:
    def __init__(self):
        # do nothing
        pass

    @staticmethod
    def generate_response(job_response: JobResponse) -> dict:
        if job_response:
            status_code = 201  # not yet finished
            if job_response.job_status == "DONE":
                status_code = 200
            elif job_response.job_status == "ERROR":
                status_code = 400
            job_dict = {
                "providerJobId": job_response.provider_job_id,
                "jobStatus": job_response.job_status,
                "jobResult": job_response.job_result
            }  # Object to directory
            response = {"statusCode": status_code, "body": job_dict}
        else:
            response = {
                "statusCode": 500,
                "body": "Error in function code. Please contact the developer.",
            }
        return response

    @staticmethod
    def qrng_counts_post_process(job) -> JobResponse:
        # If input type = JobResponse or have jobRawResult
        job_raw_result = {}
        if type(job) is JobResponse:
            if job.job_result:
                job_raw_result = job.job_result
        else:
            job = JobResponse()
            return job

        if job_raw_result:
            job.job_result = PostProcess.handle_job_result(job_raw_result)
            job.job_status = "DONE"
        return job


# Post-Processing functions
class PostProcess:
    def __init__(self):
        # do nothing
        pass

    @staticmethod
    def handle_job_result(job_counts: dict) -> dict:
        key_maximum_result = max(job_counts, key=job_counts.get)
        value_maximum_result = max(job_counts.values())
        all_possible_values = {
            k: int(k, 2) for k, v in job_counts.items() if v == value_maximum_result
        }
        details = {
            "decimalValue": int(key_maximum_result, 2),
            "numberOfOccurrence": value_maximum_result,
            "allPossibleValues": all_possible_values,
        }
        return {"data": key_maximum_result, "details": details}
