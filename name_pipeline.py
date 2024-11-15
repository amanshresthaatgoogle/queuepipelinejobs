from kfp.dsl import pipeline, component

@component(base_image="python:3.9")
def first_name_op(first_name: str) -> str:
  """Returns the first name."""
  return first_name

@component(base_image="python:3.9")
def last_name_op(last_name: str) -> str:
  """Returns the last name."""
  return last_name

@component(base_image="python:3.9")
def concat_op(first_name: str, last_name: str) -> str:
  """Concatenates first and last names."""
  return f"{first_name} {last_name}"

@pipeline(
    name="name-pipeline",
    description="A simple pipeline to concatenate first and last names.",
    pipeline_root="gs://vertexaipipeline/pipeline_root",  # Replace with your GCS bucket
)
def name_pipeline(
    first_name: str = "John",
    last_name: str = "Doe",
):
  """Pipeline to concatenate first and last names."""

  first_name_task = first_name_op(first_name=first_name)
  last_name_task = last_name_op(last_name=last_name)
  concat_task = concat_op(first_name=first_name_task.output, last_name=last_name_task.output)