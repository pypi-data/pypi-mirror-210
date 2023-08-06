import datetime
import json
import signal
import sys
import time
from collections.abc import MutableMapping
from contextlib import contextmanager

import requests


class YaspinWrapper:
    def ok(self, *args, **kwargs):
        pass


@contextmanager
def null_context(*args, **kwargs):
    yield YaspinWrapper()


def current_time():
    return datetime.datetime.utcnow().isoformat() + 'Z'


def flatten_dict(d, parent_key='', sep='__'):
    """
    This function converts a nested dictionary into a dictionary of attirbutes using '__' as a separator.
    Example:
        {'a': {'b': {'c': 1, 'd': 2}}} -> {'a__b__c': 1, 'a__b__c': 2}
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            # TODO for now, we just have string values, str(v) should be removed once we support numeric values
            items.append((new_key, str(v)))
    return dict(items)


def hide_string_chars(s):
    return ''.join(['*' for _ in range(len(s) - 4)]) + s[len(s) - 4 :] if s else None


def to_camel_case(text):
    """Convert text to camel case in great coding style"""
    s = text.replace("_", " ")
    s = s.split()
    return ''.join(i.capitalize() for i in s)


def my_handler(signum, frame, spinner):
    with spinner.hidden():
        sys.stdout.write("Program terminated!\n")
    spinner.stop()
    exit(0)


class BetterEnum:
    def __iter__(self):
        return [getattr(self, x) for x in dir(self) if ('__' not in x)].__iter__()


def download_docarray_from_s3(hubble_s3_uri: str):
    """
    This function returns the first docs from the hubble api response.
    :param hubble_s3_uri: the response from the hubble api containing the s3 uri to the stored DocArray
    :return: the first docs from the hubble api response as json
    """
    tries = 0
    while tries < 10:  # limited retries
        response = requests.get(hubble_s3_uri)
        if response.status_code == 200:
            break
        time.sleep(1)
        tries += 1

    # raise appropriate error if we couldn't get the docs
    if response.status_code != 200:  # noqa
        print(
            f'Could not get DocArray from hubble even after retries!', response.content
        )
        response.raise_for_status()

    # read the content and return the docs
    content = response.content.decode('utf-8')
    docs = json.loads(content)
    return docs


sigmap = {signal.SIGINT: my_handler, signal.SIGTERM: my_handler}
