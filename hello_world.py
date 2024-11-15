from kfp import dsl
from kfp.dsl import pipeline, component

@component(
    base_image="python:3.9",
    packages_to_install=["google-cloud-storage"]
)
def hello_world_op(output_text: str) -> str:
    """Prints a hello world message."""
    print(output_text)
    return output_text

@pipeline(
    name="hello-world-pipeline",
    description="A simple pipeline that prints 'Hello World!'.",
    pipeline_root="gs://vertexaipipelinebucket/pipeline_root"  # Replace with your GCS bucket
)
def hello_world_pipeline(
    output_text: str = "Hello World!"
):
    """Pipeline to print 'Hello World!'."""

    hello_world_task = hello_world_op(output_text=output_text) \
        .set_cpu_limit('0.5') \
        .set_memory_limit('512Mi') \
        .set_accelerator_limit(1) \
        .add_node_selector_constraint('NVIDIA_TESLA_T4')