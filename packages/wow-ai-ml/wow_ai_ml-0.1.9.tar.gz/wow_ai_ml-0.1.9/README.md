Project description
What is the WOW AI ML backend?
The WOW AI ML backend is an SDK that lets you wrap your machine learning code and turn it into a web server. You can then connect that server to a WOW AI instance to perform 2 tasks:
Dynamically pre-annotate data based on model inference results
Retrain or fine-tune a model based on recently annotated data
If you just need to load static pre-annotated data into WOW AI, running an ML backend might be overkill for you. Instead, you can import preannotated data.
How it works
Get your model code
Wrap it with the WOW AI SDK
Create a running server script
Launch the script
Connect WOW AI to ML backend on the UI
Quickstart
Follow this example tutorial to run an ML backend with a simple text classifier:
Clone the repo
git clone https://github.com/wowai-3/wow-ai-ml-backend  


Setup environment
It is highly recommended to use venv, virtualenv or conda python environments. You can use the same environment as WOW AI does. Read more about creating virtual environments via venv.
cd wow-ai-ml-backend

# Install wow-ai-ml and its dependencies
pip install -U -e .

# Install example dependencies
pip install -r wow_ai_ml/examples/requirements.txt


Initialize an ML backend based on an example script:
wow-ai-ml init my_ml_backend --script wow_ai_ml/examples/text_classifier/text_classifier.py

This ML backend is an example provided by WOW AI. See how to create your own ML backend.
Start ML backend server
wow-ai-ml start my_ml_backend


Start WOW AI and connect it to the running ML backend on the project settings page.
Create your own ML backend
Follow this tutorial to wrap existing machine learning model code with the WOW AI ML SDK to use it as an ML backend with WOW AI.
Before you start, determine the following:
The expected inputs and outputs for your model. In other words, the type of labeling that your model supports in WOW AI, which informs the WOW AI labeling config. For example, text classification labels of "Dog", "Cat", or "Opossum" could be possible inputs and outputs.
The prediction format returned by your ML backend server.
This example tutorial outlines how to wrap a simple text classifier based on the scikit-learn framework with the WOW AI ML SDK.
Start by creating a class declaration. You can create a WOW AI-compatible ML backend server in one command by inheriting it from LabelStudioMLBase.
from wow_ai_ml.model import LabelStudioMLBase

class MyModel(WOWAIML):


Then, define loaders & initializers in the __init__ method.
def __init__(self, **kwargs):
    # don't forget to initialize base class...
    super(MyModel, self).__init__(**kwargs)
    self.model = self.load_my_model()


There are special variables provided by the inherited class:
self.parsed_label_config is a Python dict that provides a WOW AI project config structure. See ref for details. Use might want to use this to align your model input/output with WOW AI labeling configuration;
self.label_config is a raw labeling config string;
self.train_output is a Python dict with the results of the previous model training runs (the output of the fit() method described bellow) Use this if you want to load the model for the next updates for active learning and model fine-tuning.
After you define the loaders, you can define two methods for your model: an inference call and a training call.
Inference call
Use an inference call to get pre-annotations from your model on-the-fly. You must update the existing predict method in the example ML backend scripts to make them work for your specific use case. Write your own code to override the predict(tasks, **kwargs) method, which takes JSON-formatted WOW AI tasks and returns predictions in the format accepted by WOW AI.
Example
def predict(self, tasks, **kwargs):
    predictions = []
    # Get annotation tag first, and extract from_name/to_name keys from the labeling config to make predictions
    from_name, schema = list(self.parsed_label_config.items())[0]
    to_name = schema['to_name'][0]
    for task in tasks:
        # for each task, return classification results in the form of "choices" pre-annotations
        predictions.append({
            'result': [{
                'from_name': from_name,
                'to_name': to_name,
                'type': 'choices',
                'value': {'choices': ['My Label']}
            }],
            # optionally you can include prediction scores that you can use to sort the tasks and do active learning
            'score': 0.987
        })
    return predictions


Training call
Use the training call to update your model with new annotations. You don't need to use this call in your code, for example if you just want to pre-annotate tasks without retraining the model. If you do want to retrain the model based on annotations from WOW AI, use this method.
Write your own code to override the fit(annotations, **kwargs) method, which takes JSON-formatted WOW AI annotations and returns an arbitrary dict where some information about the created model can be stored.
Example
def fit(self, completions, workdir=None, **kwargs):
    # ... do some heavy computations, get your model and store checkpoints and resources
    return {'checkpoints': 'my/model/checkpoints'}  # <-- you can retrieve this dict as self.train_output in the subsequent calls


After you wrap your model code with the class, define the loaders, and define the methods, you're ready to run your model as an ML backend with WOW AI.
For other examples of ML backends, refer to the examples in this repository. These examples aren't production-ready, but can help you set up your own code as a WOW AI ML backend.
Deploy your ML backend to GCP
Before you start:
Install gcloud
Init billing for account if it's not activated
Init gcloud, type the following commands and login in browser:
gcloud auth login


Activate your Cloud Build API
Find your GCP project ID
(Optional) Add GCP_REGION with your default region to your ENV variables
To start deployment:
Create your own ML backend
Start deployment to GCP:
wow-ai-ml deploy gcp {ml-backend-local-dir} \
--from={model-python-script} \
--gcp-project-id {gcp-project-id} \
--wow-ai-host {https://tool.wowdao.ai} \
--wow-ai-api-key {YOUR-wow-ai-API-KEY}


After WOW AI deploys the model - you will get model endpoint in console.

twine upload -u 'huonghx' -p 'y@9^xwWA+!TzmY)' --repository-url https://upload.pypi.org/legacy/ dist/*

