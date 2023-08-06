import base64
import itertools
import json
import os
from typing import Dict, List

import requests

from now.constants import (
    AVAILABLE_MODALITIES_FOR_FILTER,
    AVAILABLE_MODALITIES_FOR_SEARCH,
    FILETYPE_TO_MODALITY,
    NOT_AVAILABLE_MODALITIES_FOR_FILTER,
    SUPPORTED_FILE_TYPES,
    FolderStructure,
)
from now.data_loading.elasticsearch import ElasticsearchConnector
from now.data_loading.s3_class import CustomPurePath, S3Uri
from now.now_dataclasses import UserInput
from now.utils.common.helpers import download_docarray_from_s3, flatten_dict
from now.utils.docarray.helpers import (
    docarray_typing_to_modality_string,
    modality_string_to_docarray_typing,
)
from now.utils.errors.helpers import RetryException

# List of Document attributes that can hold the content of the document
DOCUMENT_CONTENT_ATTRIBUTE = ['text', 'blob', 'tensor', 'uri']


def get_field_type(field_value):
    # if there is a file ending, and it is among the known file types
    for file_type in FILETYPE_TO_MODALITY.keys():
        if not isinstance(field_value, str):
            continue
        if field_value.endswith(file_type):
            return file_type
    return 'txt'  # for some reason the code expects a file type, so we return a default one


def _create_candidate_index_filter_fields(field_name_to_value):
    """
    Creates candidate index fields from the field_names for s3
    and local file path.
    A candidate index field is a field that we can detect its modality
    A candidate filter field is a field that we can't detect its modality,
    or it's modality is different from image, video or audio.

    :param field_name_to_value: dictionary
    """
    index_field_candidates_to_modalities = {}
    filter_field_candidates_to_modalities = {}
    not_available_file_types_for_filter = list(
        itertools.chain(
            *[
                SUPPORTED_FILE_TYPES[modality]
                for modality in NOT_AVAILABLE_MODALITIES_FOR_FILTER
            ]
        )
    )
    for field_name, field_value in field_name_to_value.items():
        # we determine search modality
        file_type = get_field_type(field_value)
        index_field_candidates_to_modalities[field_name] = FILETYPE_TO_MODALITY[
            file_type
        ]

        # we determine if it's a filter field
        if (
            field_name == 'uri'
            and field_value.split('.')[-1] not in not_available_file_types_for_filter
        ) or field_name.split('.')[-1] not in not_available_file_types_for_filter:
            filter_field_candidates_to_modalities[
                field_name
            ] = field_value.__class__.__name__

    if len(index_field_candidates_to_modalities.keys()) == 0:
        raise ValueError(
            'No searchable fields found, please check documentation https://now.jina.ai'
        )
    return index_field_candidates_to_modalities, filter_field_candidates_to_modalities


def _extract_field_candidates_docarray(docs, data_preview=False):
    """
    Downloads the first document in the document array and extracts field names from it
    if tags also exists then it extracts the keys from tags and adds to the field_names
    :param docs: document array
    :param data_preview: if True, returns a sample document
    :return: search_modalities, filter_modalities, sample_docs

    """
    search_modalities = {}
    filter_modalities = {}
    sample_docs = {} if data_preview else None
    doc = docs[0]

    if (
        not doc.get('_metadata', None)
        or 'multi_modal_schema' not in doc['_metadata']['fields']
    ):
        raise RuntimeError(
            'Multi-modal schema is not provided. Please prepare your data following this guide - '
            'https://docarray.jina.ai/datatypes/multimodal/'
        )
    mm_schema = doc['_metadata']['fields']['multi_modal_schema']
    mm_fields = mm_schema['structValue']['fields']
    for field_name, value in mm_fields.items():
        if 'position' not in value['structValue']['fields']:
            raise ValueError(
                f'No modality found for the dataclass field: `{field_name}`. Please follow the steps in the '
                f'documentation to add modalities to your documents https://docarray.jina.ai/datatypes/multimodal/'
            )
        field_pos = value['structValue']['fields']['position']['numberValue']
        if not doc['chunks'][field_pos]['modality']:
            raise ValueError(
                f'No modality found for {field_name}. Please follow the steps in the documentation'
                f' to add modalities to your documents https://docarray.jina.ai/datatypes/multimodal/'
            )
        modality = doc['chunks'][field_pos]['modality'].lower()
        docarray_type = modality_string_to_docarray_typing(modality)
        content = None
        for attribute in DOCUMENT_CONTENT_ATTRIBUTE:
            if attribute in doc['chunks'][field_pos]:
                content = doc['chunks'][field_pos][attribute]
                if attribute == 'tensor':  # handle special case for tensors
                    content = content['dense']['buffer']
                break
        if docarray_type in AVAILABLE_MODALITIES_FOR_SEARCH:
            search_modalities[field_name] = docarray_type
            if data_preview:
                sample_docs[field_name] = content
        else:
            raise ValueError(
                f'The modality {modality} is not supported for search. Please use one of the following modalities: '
                f'{map(docarray_typing_to_modality_string, AVAILABLE_MODALITIES_FOR_SEARCH)}'
            )
        if docarray_type in AVAILABLE_MODALITIES_FOR_FILTER:
            filter_modalities[field_name] = modality

    if doc.get('tags', None):
        for el, value in doc['tags']['fields'].items():
            for val_type, val in value.items():
                filter_modalities[el] = val_type
                if data_preview:
                    sample_docs[el] = val

    if len(search_modalities.keys()) == 0:
        raise ValueError(
            'No searchable fields found, please check documentation https://now.jina.ai'
        )
    return search_modalities, filter_modalities, sample_docs


def set_field_names_from_docarray(user_input: UserInput, data_preview=False, **kwargs):
    """
    Get the schema from a DocArray

    :param user_input: UserInput object
    :param data_preview: If True, return the first sample doc from the DocArray as json

    Makes a request to hubble API and downloads the first 10 documents
    from the document array and uses the first document to get the schema and sets field_names in user_input
    """
    if not user_input.dataset_name:
        # meant to be caught when jina-now is executed from CLI
        raise RetryException('Please retry')

    dataset_name = (
        user_input.admin_name + '/' + user_input.dataset_name
        if '/' not in user_input.dataset_name
        else user_input.dataset_name
    )

    json_data = {'name': dataset_name}
    cookies = {'st': user_input.jwt['token']}

    response = requests.post(
        'https://api.hubble.jina.ai/v2/rpc/docarray.getFirstDocuments',
        cookies=cookies,
        json=json_data,
    )

    sample_docs = None
    if response.status_code == 200:
        s3_uri = response.json()['data']['download']
        docs = download_docarray_from_s3(s3_uri)
        (
            user_input.index_field_candidates_to_modalities,
            user_input.filter_field_candidates_to_modalities,
            sample_docs,
        ) = _extract_field_candidates_docarray(docs, data_preview)
    else:
        if 400 <= response.status_code < 500:  # Custom error message for 4xx errors
            raise ValueError(
                f'DocumentArray "{dataset_name}" does not exist or you do not have access to it. '
                'Make sure to add user name as a prefix. Check documentation here. '
                'https://docarray.jina.ai/fundamentals/cloud-support/data-management/'
            )
        response.raise_for_status()  # Raise error for 5xx errors

    return sample_docs


def _extract_field_names_single_folder(
    file_paths: List[str], s3_bucket=None, data_preview=False
) -> (Dict[str, str], Dict[str, str]):
    """This function extracts the file name with extension in a single folder and returns them as field names.
    It works with a local file structure or a remote file structure.

    :param file_paths: list of relative file paths from data set path
    :return: list of file endings
    """
    file_suffix = {}
    for path in file_paths:
        path = CustomPurePath(path)
        file_suffix[path.suffix] = path

    sample_data = None
    if s3_bucket and data_preview:
        # read one file for each file ending and add it to the sample data
        sample_data = {}
        for suffix, path in file_suffix.items():
            content = s3_bucket.Object(str(path)).get()['Body'].read()
            try:
                content = content.decode('utf-8')  # convert to string if possible
                if suffix == '.json':  # handle special case for json
                    content = json.loads(content)
            except UnicodeDecodeError:
                content = base64.b64encode(content)
            sample_data[suffix] = content
    file_suffix_dict = {suffix: suffix for suffix in file_suffix.keys()}
    return file_suffix_dict, sample_data


def _extract_field_names_sub_folders(
    file_paths: List[str], s3_bucket=None, data_preview=False
) -> (Dict[str, str], Dict[str, str]):
    """This function extracts the files in sub folders and returns them as field names. Also, it reads json files
    and adds them as key-value pairs to the field names dictionary.
    It works with a local file structure or a remote file structure.

    :param file_paths: list of relative file paths from data set path
    :param s3_bucket: s3 bucket object, only needed if interacting with s3 bucket
    :param data_preview: If True, return the sample documents
    :return: list of file endings
    """
    fields_dict = {}
    sample_data = {} if data_preview else None
    file_paths = [CustomPurePath(path) for path in file_paths]
    for path in file_paths:
        if path.suffix == '.json':
            if s3_bucket:
                data = json.loads(s3_bucket.Object(str(path)).get()['Body'].read())
            else:
                with open(str(path)) as f:
                    data = json.load(f)
            for el, value in data.items():
                fields_dict[el] = value
            flattened_dict = flatten_dict(data)
            fields_dict.update(flattened_dict)
            if data_preview:
                sample_data.update(flattened_dict)
        else:
            file_name = path.name
            fields_dict[file_name] = file_name
            if s3_bucket and data_preview:
                content = s3_bucket.Object(str(path)).get()['Body'].read()
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    content = base64.b64encode(content)
                sample_data[file_name] = content
    return fields_dict, sample_data


def set_field_names_from_s3_bucket(user_input: UserInput, data_preview=True, **kwargs):
    """
    Get the schema from a S3 bucket

    :param user_input: UserInput object
    :param data_preview: If True, return the sample documents
    :param kwargs: Additional keyword arguments

    :return: None if data_preview is False, otherwise return the sample documents as json

    checks if the bucket exists and the format of the folder structure is correct,
    if yes then downloads the first folder and sets its content as fields_dict in user_input
    """
    s3_uri_obj = S3Uri(user_input)
    file_paths = s3_uri_obj.get_prefix_files(limit=100)
    if s3_uri_obj.folder_structure == FolderStructure.SINGLE_FOLDER:
        fields_dict, sample_data = _extract_field_names_single_folder(
            file_paths, s3_uri_obj.bucket, data_preview
        )
    else:
        fields_dict, sample_data = _extract_field_names_sub_folders(
            file_paths, s3_uri_obj.bucket, data_preview
        )
    fields_dict_cleaned = {
        field_key: field_value
        for field_key, field_value in fields_dict.items()
        if not isinstance(field_value, list) and not isinstance(field_value, dict)
    }
    (
        user_input.index_field_candidates_to_modalities,
        user_input.filter_field_candidates_to_modalities,
    ) = _create_candidate_index_filter_fields(fields_dict_cleaned)

    return sample_data


def set_field_names_from_local_folder(user_input: UserInput, **kwargs):
    """
    Get the schema from a local folder

    :param user_input: UserInput object

    checks if the folder exists and the format of the folder structure is correct,
    if yes set the content of the first folder as field_names in user_input
    """
    dataset_path = user_input.dataset_path.strip()
    dataset_path = os.path.expanduser(dataset_path)
    if os.path.isfile(dataset_path):
        raise ValueError(
            'The path provided is not a folder, please check documentation https://now.jina.ai'
        )
    file_paths = []
    folder_generator = os.walk(dataset_path, topdown=True)
    current_level = folder_generator.__next__()
    # check if the first level contains any folders
    folder_structure = (
        FolderStructure.SUB_FOLDERS
        if len(current_level[1]) > 0
        else FolderStructure.SINGLE_FOLDER
    )
    if folder_structure == FolderStructure.SINGLE_FOLDER:
        file_paths.extend(
            [
                os.path.join(dataset_path, file)
                for file in current_level[2]
                if not file.startswith('.')
            ]
        )
        fields_dict, _ = _extract_field_names_single_folder(file_paths)
    else:
        # depth-first search of the first nested folder containing files
        while len(current_level[1]) > 0:
            current_level = folder_generator.__next__()
        first_folder = current_level[0]
        file_paths = [
            os.path.join(first_folder, file)
            for file in os.listdir(first_folder)
            if os.path.isfile(os.path.join(first_folder, file))
            and not file.startswith('.')
        ]
        fields_dict, _ = _extract_field_names_sub_folders(file_paths)
    fields_dict_cleaned = {
        field_key: field_value
        for field_key, field_value in fields_dict.items()
        if not isinstance(field_value, list) and not isinstance(field_value, dict)
    }
    (
        user_input.index_field_candidates_to_modalities,
        user_input.filter_field_candidates_to_modalities,
    ) = _create_candidate_index_filter_fields(fields_dict_cleaned)


# Elasticsearch schema detection
def set_field_names_elasticsearch(user_input: UserInput, **kwargs):
    """
    Get the schema from an Elasticsearch instance

    :param user_input: UserInput object

    checks if the Elasticsearch instance exists and grabs the first document from the index,
    the first document is then used to create modalities dicts for index and filter fields
    """
    with ElasticsearchConnector(
        connection_str=user_input.es_host_name,
    ) as es_connector:
        query = {
            'query': {'match_all': {}},
            '_source': True,
        }
        first_docs = list(
            es_connector.get_documents_by_query(
                query=query, index_name=user_input.es_index_name, page_size=1
            )
        )[
            0
        ]  # get one document
    fields_dict = first_docs[0]
    fields_dict_cleaned = {
        field_key: field_value
        for field_key, field_value in fields_dict.items()
        if not isinstance(field_value, list) and not isinstance(field_value, dict)
    }
    (
        user_input.index_field_candidates_to_modalities,
        user_input.filter_field_candidates_to_modalities,
    ) = _create_candidate_index_filter_fields(fields_dict_cleaned)
