from seismic_classifier.core import classifier
from fastapi import FastAPI, File, HTTPException
from obspy import read
from io import BytesIO
from importlib import reload
from seismic_classifier.api.rest.models import ClassifierResults
from seismic_classifier.ai.model import EventClassifier2
from pickled_carrots.vinegar.core import HSFHandler
from loguru import logger
import uvicorn
import os
import tempfile

# Read the value of an environment variable
try:
    num_workers = int(os.getenv("API_NUM_WORKERS"))
except Exception as e:
    logger.error(e)
    num_workers = 1

reload(classifier)

app = FastAPI()

root_dir = '/tmp/projects'
project_name = 'classification'
network_name = 'cls'

ec = classifier.Classifier2(root_dir, project_name, network_name, gpu=True)

if ec.event_classifier is None:
    ec.add_model(EventClassifier2.load())

app = FastAPI()


# Define the endpoint for handling predictions
@app.post('/classifier/predict/stream/mseed', status_code=201,
          response_model=ClassifierResults)
async def predict_mseed(stream: bytes = File(...)):
    """
    Endpoint for making predictions on a stream of data.

    :param stream: A byte stream of data in miniSEED format.
    :type stream: bytes

    :return: A JSON string representing the prediction output. The string will contain
             a list of dictionaries, where each dictionary corresponds to a predicted
             label for a specific time window in the input stream.
    :rtype: str
    """

    # Read the stream data into a BytesIO object
    f_in = BytesIO(stream)

    # Use ObsPy to read the stream data into a Stream object
    st = read(f_in)

    # Make a prediction using the Stream object and a pre-trained rest
    classifier_output = ec.predict(st)

    # Print the prediction (optional)
    print(classifier_output)

    # Convert the prediction to a JSON string and return it as the response
    return classifier_output.to_fastapi()


@app.post('/classifier/predict/stream/{network}/hsf', status_code=201,
          response_model=ClassifierResults)
async def predict_hsf(network: str, stream: bytes = File(...)):
    """
    Endpoint for making predictions on a stream of data.

    :param network: The network code.
    :type network: str
    :param stream: A byte stream of data in miniSEED format.
    :type stream: bytes
    :return: A JSON string representing the prediction output.
    :rtype: str
    """

    try:
        # Create a temporary file and write the stream data to it
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(stream)
            temp_file_path = temp_file.name

        # Use HSFHandler to read the temporary file
        st = HSFHandler.read(temp_file_path, network).file_bundle.stream

        # Make a prediction using the Stream object and a pre-trained model
        classifier_output = ec.predict(st)

        # Log the prediction output
        logger.info(classifier_output)

        # Convert the prediction to a JSON string and return it as the response
        return classifier_output.to_fastapi()
    except Exception as e:
        # Log and return an appropriate error response
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        # Delete the temporary file
        if temp_file_path:
            os.remove(temp_file_path)


# async def create_training(stream: bytes = File(...)):

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Seismic classification",
        version="0.1.0",
        description="Trace by trace classification API providing access to the "
                    "CNN rest",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.get("/docs", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Seismic Classification",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    return custom_openapi()


def start():

    uvicorn.run("seismic_classifier.api.rest.server:app", host="0.0.0.0",
                port=8000, reload=True, workers=num_workers)
