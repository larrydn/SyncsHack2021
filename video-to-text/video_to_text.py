import json
import sys

"""
    NEEDS TO BE DONE BEFORE RUNNING:
        1. export GOOGLE_APPLICATION_CREDENTIALS="some_path/.../video-to-text-324211-dfded3aa3010.json" 
        2. you need to have uploaded the video file to a bucket and have its gsc_uri

    EXPECTED TO BE RUN LINE THIS:
        python video_to_text.py gcs_uri

    OUTPUTS:
        video_transcript.json in text_data folder
"""

def transcribe_gcs(gcs_uri, timeout=2100):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        # sample_rate_hertz=16000,
        language_code="en-US",
        max_alternatives=5,
        use_enhanced=True,
        model="phone_call"
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=timeout)

    return response

#TODO: We can have this export to a google cloud storage bucket if needed
def export_to_json(response, path="output.json"):
    rows = []
    for res in response.results:
        max_conf = 0
        max_alt = ""
        for alt in res.alternatives:
            if alt.confidence > max_conf:
                max_alt = alt.transcript
        rows.append(max_alt)

    with open(path, "w", encoding='utf-8') as f:
        json.dump(rows, f, indent = 4)

    print("Json file created.")



# gcs_uri = "gs://video_storage_314/snd_trim_flac.flac"
# gcs_uri_2 = "gs://video_storage_314/snd_trim_20.flac"

if len(sys.argv) > 1:
    gcs_uri = sys.argv[1]
else:
    gcs_uri = None #"gs://video_storage_314/snd_trim_20.flac"


directory = "../text_data/"
filename = "video_transcript.json"
path = directory + filename
print("Transcribing: " + gcs_uri)
response = transcribe_gcs(gcs_uri)
print("Finished transcription.")
export_to_json(response, path)

