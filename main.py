import json
import os
import base64  # Import base64

from flask import Flask, request
from google.cloud import aiplatform

app = Flask(__name__)

# ----------------------------------
#  Configure these variables
# ----------------------------------

# Pub/Sub Configuration
PROJECT_ID = os.environ.get("PROJECT_ID", "test-data-studio-365519")
# SUBSCRIPTION_ID = "pipeline-requests-sub" 
TOPIC_ID = "pipeline-requests"

# Vertex AI Configuration
REGION = "us-central1"
# ... (Add other Vertex AI configurations if needed)

# ----------------------------------
#  End of Configuration
# ----------------------------------

# Pipeline Queue (use a list for simplicity)
pipeline_queue = []


# Function to add a pipeline request to the queue
def add_to_queue(pipeline_request):
    print("add to queue back received")
    # Basic queuing (no prioritization for now)
    pipeline_queue.append(pipeline_request)



def get_pipeline_resources(template_path):
    """
    Extracts resource requirements from a pipeline template JSON file.

    Args:
        template_path (str): GCS path to the pipeline template JSON file.

    Returns:
        dict: A dictionary containing resource information for each component.
                   Includes default values if resources are not explicitly defined.
    """
    try:
        # Initialize a Cloud Storage client
        storage_client = storage.Client()

        # Parse the GCS path 
        bucket_name, blob_name = template_path.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download the contents of the blob as a string
        template_data = json.loads(blob.download_as_string())

    except Exception as e:
        print(f"Error accessing or parsing the pipeline template: {e}")
        return {}


    resource_info = {}
    for executor_label, executor in template_data.get('pipelineSpec', {}).get('deploymentSpec', {}).get('executors', {}).items():
        resources = executor.get('container', {}).get('resources', {})
        resource_info[executor_label] = {
            'request_cpu': resources.get('cpuLimit', '0.5'),
            'request_memory': resources.get('memoryLimit', '1Gi'),
            'limit_cpu': resources.get('cpuLimit', '1'),
            'limit_memory': resources.get('memoryLimit', '2Gi')
        }
    return resource_info

# Function to process the queue and execute pipelines
def process_queue():
    print("Process queue")
    if pipeline_queue:  # Process while the queue is not empty
        pipeline_request = pipeline_queue.pop(0)  # Get the first item

        try:
            # Execute the pipeline using Vertex AI SDK
            aiplatform.init(project=PROJECT_ID, location=REGION)

            # Assuming pipeline_request has 'pipeline_root' and 'template_path'
            job = aiplatform.PipelineJob(
                display_name=pipeline_request.get(
                    'display_name', 'pipeline-job'),
                template_path=pipeline_request['template_path'],
                pipeline_root=pipeline_request['pipeline_root'],
                enable_caching=False,
            )
            job.submit()
            print(f"Submitted job: {job.resource_name}")

        except Exception as e:
            print(f"Error submitting pipeline job: {e}")
            # Implement error handling (e.g., logging, retrying, etc.)


@app.route('/', methods=['POST'])  # Add this route
def receive_message():
    """Handles incoming Pub/Sub messages."""
    try:
        # Get the message data from the request
        envelope = request.get_json()
        if not envelope:
            raise Exception("Invalid Pub/Sub message format")
        message = envelope["message"]
        data = message["data"]
        # Decode the message data
        pipeline_request = json.loads(base64.b64decode(data).decode("utf-8"))

        # Add request to the queue (with potential prioritization)
        add_to_queue(pipeline_request)

        # Trigger pipeline execution
        process_queue()

        # Return a success response
        return 'Message received and processed', 200

    except Exception as e:
        print(f"Error processing message: {e}")
        return 'Error processing message', 500


# Flask route for health checks (optional)
@app.route('/health')
def health_check():
    return 'Healthy', 200


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))