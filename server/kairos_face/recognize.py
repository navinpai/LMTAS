from kairos_face import exceptions, validate_settings, validate_file_and_url_presence
from kairos_face import settings
import requests
import base64

from kairos_face.entities import RecognizedFaceCandidate

_recognize_base_url = settings.base_url + 'recognize'


def recognize_face(gallery_name, url=None, file=None, additional_arguments={}):
    validate_settings()
    validate_file_and_url_presence(file, url)

    auth_headers = {
        'app_id': settings.app_id,
        'app_key': settings.app_key
    }
    payload = _build_payload(gallery_name, url, file, additional_arguments)

    response = requests.post(_recognize_base_url, json=payload, headers=auth_headers)
    json_response = response.json()
    if response.status_code != 200 or 'Errors' in json_response:
        raise exceptions.ServiceRequestError(response.status_code, json_response, payload)

    first_image = json_response['images'][0]
    recognized_faces = []
    if first_image['transaction']['status'] != 'failure':
        recognized_faces.append(_subject_from_first_response(first_image))
        #recognized_faces.extend(_extract_candidates(first_image['candidates'][1:]))

    return recognized_faces


def _subject_from_first_response(first_response):
    import pdb;pdb.set_trace()
    return RecognizedFaceCandidate(
        first_response['transaction']['subject_id'],
        float(first_response['transaction']['confidence'])
    )


def _extract_candidates(candidates_dict_array):
    candidates = []
    for entry in candidates_dict_array:
        entry.pop('enrollment_timestamp')
        subject_name = list(entry.keys())[0]
        candidates.append(RecognizedFaceCandidate(subject_name, float(entry[subject_name])))

    return sorted(candidates, key=lambda c: c.confidence)


def _flatten(candidate_keys):
    return [val for sublist in candidate_keys for val in sublist]


def _build_payload(gallery_name, url, file, additional_arguments):
    if file is not None:
        image = _extract_base64_contents(file)
    else:
        image = url

    required_fields = {
        'image': image,
        'gallery_name': gallery_name
    }

    return dict(required_fields, **additional_arguments)


def _extract_base64_contents(image_path):
    with open(image_path, 'rb') as fp:
        return base64.b64encode(fp.read()).decode('ascii')
