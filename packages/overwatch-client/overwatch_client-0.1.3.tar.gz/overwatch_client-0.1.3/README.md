# Overwatch Client

This is a python client for the Overwatch REST API. This implementation is a work in progress but is still able to communicate with the overwatch server and register/infer models. 


```py 

from overwatch_client import HTTPClient

client = HTTPClient(
  overwatch_server_url = "https://overwatch.distributive.network",
  model_registry_url = "https://models.overwatch.distributive.network"
)

print(f"Can we connect? {client.check_overwatch_server_connection()}")

#### Register a Model

response = client.register_model(
    model_name = "my_model",
    model_path = "./my_model.onnx",
    preprocess_path = "./preprocess.py",
    postprocess_path = "./postprocess.py",
    password = "my_password",
    language = "python",
    packages = ["numpy", "pandas", "opencv-python"]
)

print(response.text) ### Model registered successfully!

#### Infer a Model


response = client.infer(
    inputs = files, # a list of the bytes of each input
    model_name = "my_model",
    slice_batch = 1, # number of inputs per slice
    inference_id = "my_inference_id", # An identifier for the inference
    compute_group_info = "joinKey/joinSecret" # The compute group info for the inference
)


```
