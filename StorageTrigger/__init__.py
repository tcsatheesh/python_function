import os
import logging

import azure.functions as func

# Form Recognizer API calls
import json
import time
from requests import get, post


class FormsRecognizer:
    def __init__(self, endpoint, cognitive_svc_key, model_id):
        self.endpoint = endpoint
        self.apim_key = cognitive_svc_key
        # Find the model_id of the trianed model from the 'Train' pane of the Form Recognizer Labelling Tool
        self.model_id = model_id
        self.post_url = self.endpoint + \
            "/formrecognizer/v2.0-preview/custom/models/%s/analyze" % self.model_id
        self.params = {"includeTextDetails": True}
        self.headers = {
            # Request headers
            'Content-Type': 'application/pdf',
            'Ocp-Apim-Subscription-Key': self.apim_key
        }

    def call_form_recognizer_api(self, data_bytes):
        get_url = None
        try:
            post_response = post(url=self.post_url,
                                 data=data_bytes,
                                 headers=self.headers,
                                 params=self.params)
            if post_response.status_code != 202:
                logging.error(f"Failure from Forms Recognizer\n"
                              f"Status Code: {post_response.status_code}\n"
                              f"Response Text: {post_response.text} bytes\n")
            else:
                logging.info(f"POST analyze succeeded\n")
                get_url = post_response.headers["operation-location"]
                logging.info(f"GET URL:{get_url}\n")
                n_tries = 4
                n_try = 0
                wait_sec = 5
                max_wait_sec = 60

                while n_try < n_tries:
                    try:
                        get_response = get(
                            url=get_url,
                            headers={"Ocp-Apim-Subscription-Key": self.apim_key})
                        response_json = get_response.json()
                        if get_response.status_code != 200:
                            logging.error(f"Failure from Forms Recognizer\n"
                                          f"Status Code: {get_response.status_code}\n"
                                          f"Response Text: {get_response.text} bytes\n")
                        else:
                            status = response_json["status"]
                            if status == "succeeded":
                                logging.info(f"GET analysis succeeded")
                                return response_json
                            elif status == "failed":
                                logging.exception(
                                    f"GET analysis failed {response_json}\n")
                                return
                            else:
                                # Analysis still running.  Wait and retry.
                                time.sleep(wait_sec)
                                n_try += 1
                                wait_sec = min(2 * wait_sec, max_wait_sec)
                    except Exception as e:
                        logging.error(
                            f"GET analyze results failed:\n{str(e)}\n")
                        break
        except Exception as e:
            logging.error(f"POST analyze failed due to:\n {str(e)}\n")

    @classmethod
    def call_forms_recognizer(cls, form_data):
        cognitive_svc_endpoint = os.getenv("FORMS_RECOGNIZER_SERVICE_ENDPOINT")
        cognitive_svc_key = os.getenv("FORMS_RECOGNIZER_SERVICE_API_KEY")
        model_id = os.getenv("FORMS_RECOGNIZER_MODEL_ID")
        cognitive_svc = CognitiveService(cognitive_svc_endpoint,
                                         cognitive_svc_key, model_id)
        return cognitive_svc.call_form_recognizer_api(data_bytes=form_data)


def main(inputblob: func.InputStream, outputblob: func.Out[func.InputStream]):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {inputblob.name}\n"
                 f"Blob Size: {inputblob.length} bytes\n")

    output_json = FormsRecognizer.call_forms_recognizer(
        form_data=inputblob.read())
    outputblob.set(json.dumps(output_json))
