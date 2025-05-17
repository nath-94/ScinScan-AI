from inference_sdk import InferenceHTTPClient

def detect(image_path:str):
    client = InferenceHTTPClient(
      api_url="https://detect.roboflow.com",
      api_key="8V5TEzrrRuOJWTfF0Ing"
  )

    result = client.run_workflow(
      workspace_name="tets-hzv1l",
      workflow_id="detect-count-and-visualize-2",
      images={
          "image": image_path
      },
      use_cache=True # cache workflow definition for 15 minutes
  )
    return result
