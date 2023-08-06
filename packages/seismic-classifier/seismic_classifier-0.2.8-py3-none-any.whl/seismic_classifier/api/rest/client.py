import requests
from io import BytesIO
from uquake.core import read
from pickled_carrots.vinegar.core import HSFHandler


# Replace this with the path to the mseed file you want to send
mseed_file_path = '/data_1/ot-reprocessed-data/' \
                  '7afae7feef225ae2b05356b8003353ec.context_mseed'


# def predict(stream):
#     # Create a BytesIO object and write the stream data to it
#     stream_io = BytesIO()
#     stream.write(stream_io, format='mseed')
#
#     # Reset the buffer position to the beginning of the stream
#     stream_io.seek(0)
#
#     # Send the stream to the predict endpoint using requests.post()
#     response = requests.post(
#         'http://0.0.0.0:8000/classifier/predict/stream',
#         files={'stream_io': stream_io}
#     )
#
#     if response.status_code == 201:
#         raw_output = response.json()
#         print(raw_output)
#     else:
#         print(f'Request failed with status code {response.status_code}')
#
# # Read the mseed file into an ObsPy stream object
# st = read(open(mseed_file_path, 'rb'))[:12]
#
# # Call the predict function with the ObsPy stream object
# response = predict(st)


def predict_mseed(filename):
    """
    Read an mseed file, convert it to a stream, and send it to the prediction
    endpoint. Wait for the response.

    :param filename: Path to the mseed file.
    :type filename: str
    """
    url = "http://localhost:8000/classifier/predict/stream/mseed"

    # Read the mseed file into a Stream object using ObsPy
    st = read(filename)

    predict(st, url)


def predict_hsf(network, filename):
    """
    Read an hsf file, convert it to a stream, and send it to the prediction
    endpoint. Wait for the response.

    :param network: Network code
    :type network: str
    :param filename: Path to the mseed file.
    :type filename: str
    """
    url = "http://localhost:8000/classifier/predict/stream/{network}/hsf"

    # Read the mseed file into a Stream object using ObsPy
    st = HSFHandler.read(filename).file_bundle.stream

    # Convert the Stream object to a byte stream
    predict(st, url)


def predict(st, url):
    stream = BytesIO()
    st.write(stream, format="MSEED")
    stream.seek(0)  # Reset the stream position to the beginning

    # Create a dictionary with the file field and the stream as the value
    files = {"stream": stream}

    # Send a POST request to the endpoint
    response = requests.post(url, files=files)

    # Check if the request was successful
    if response.status_code == 201:
        # Print the response JSON string
        print(response.json())
    else:
        print("Error occurred:", response.text)



