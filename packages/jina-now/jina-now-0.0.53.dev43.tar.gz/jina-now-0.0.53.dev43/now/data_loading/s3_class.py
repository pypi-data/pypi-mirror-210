import os
import pathlib
from pathlib import PurePosixPath, PureWindowsPath

from now.constants import FolderStructure
from now.now_dataclasses import UserInput
from now.utils.authentication.helpers import get_aws_profile


class CustomPurePath(pathlib.PurePath):
    """
    PurePath subclass that can be instantiated from a S3 URL or a local path. This is needed because the PurePath
    class does not support custom schemes. The purpose of this class is to parse the S3 URL as well as the local path
    and store the parsed parts in the same way as the PurePath class does. This class also adds a new attribute called
    is_s3 which is True if the path is a S3 URL and False if it is a local path.
    """

    s3_schema = "s3:/"

    def __new__(cls, *args):
        if args[0].startswith(cls.s3_schema):
            args = (args[0].replace(cls.s3_schema, "", 1),) + args[1:]
        cls = PureWindowsPath if os.name == 'nt' else PurePosixPath
        return cls._from_parts(args)  # type: ignore

    def __init__(self, *args):
        self.is_s3 = True if args[0].startswith(self.s3_schema) else False

    def __str__(self):
        try:
            return (self.s3_schema if self.is_s3 else '') + self._str  # type: ignore
        except AttributeError:
            self._str = (
                self._format_parsed_parts(
                    self._drv, self._root, self._parts  # type: ignore
                )
                or '.'
            )  # type: ignore
            return (self.s3_schema if self.is_s3 else '') + self._str


class S3Uri:
    def __init__(self, user_input: UserInput):
        if not user_input.dataset_path.startswith('s3://'):
            raise ValueError(
                f'S3 uri not set or Invalid s3 uri: {user_input.dataset_path}'
            )

        self._s3_uri = user_input.dataset_path
        self._uri_sections = self._s3_uri.split('/')
        self._bucket_name = self._uri_sections[2]
        self._s3_folder_prefix = self._uri_sections[3:]
        self._filename = self._uri_sections[-1]
        self._aws_profile = get_aws_profile(user_input)

        # initialize the bucket object and folder structure
        self._init_bucket()
        self._init_folder_structure()

    @property
    def bucket_name(self):
        return self._bucket_name

    @property
    def folder_prefix(self):
        return '/'.join(self._s3_folder_prefix)

    @property
    def filename(self):
        return self._filename

    @property
    def folder_structure(self):
        return self._folder_structure

    @property
    def bucket(self):
        return self._s3_bucket_obj

    @staticmethod
    def _is_folder(file_path):
        if isinstance(file_path, str):
            return file_path.endswith('/')
        return file_path.key.endswith('/')

    @staticmethod
    def _is_hidden(file_path):
        if isinstance(file_path, str):
            return file_path.split('/')[-1].startswith('.')
        return file_path.key.split('/')[-1].startswith('.')

    def _init_bucket(self):
        import boto3.session

        session = boto3.session.Session(
            aws_access_key_id=self._aws_profile.aws_access_key_id,
            aws_secret_access_key=self._aws_profile.aws_secret_access_key,
        )
        self._s3_bucket_obj = session.resource('s3').Bucket(self._bucket_name)

    def _init_folder_structure(self):
        first_obj = self.get_first_file_path()
        rel_path = first_obj[len(self.folder_prefix) :].split('/')
        self._folder_structure = (
            FolderStructure.SUB_FOLDERS
            if len(rel_path) > 1
            else FolderStructure.SINGLE_FOLDER
        )
        self._sub_folder_prefix = (
            first_obj if self._folder_structure == FolderStructure.SUB_FOLDERS else None
        )

    def get_first_file_path(self):
        """
        Returns the first non-hidden object in the s3 bucket.
        """
        try:
            # gets the first object in a s3 bucket, index 0 is reserved for the prefix itself
            i = 2
            first_object = self.get_prefix_contents(limit=i)[1].key
            while self._is_hidden(first_object):
                first_object = self.get_prefix_contents(limit=i + 1)[i].key
                i += 1
                if i > 100:
                    raise Exception(
                        f'Could not find a non-hidden file in first'
                        f' 100 entries in the folder prefix: {self.folder_prefix}'
                    )
        except IndexError:
            raise Exception(f'Could not find a file in the folder {self.folder_prefix}')
        return first_object

    def get_prefix_contents(self, limit=None, prefix=None):
        """
        Returns a list of all the s3 objects in the bucket with the given prefix. It includes the prefix itself
        as well as all the files and folders in the prefix including the sub-folders and their contents.
        :param limit: The maximum number of objects to return. If not specified, returns all objects.
        :param prefix: The prefix to search for. If not specified, uses the folder prefix of the s3 uri.
        """
        return list(
            self._s3_bucket_obj.objects.filter(
                Prefix=prefix or self.folder_prefix
            ).limit(limit)
        )

    def get_prefix_files(self, limit=None, use_sub_folder=True):
        """
        Returns a list of files in the prefix excluding the prefix itself and the hidden objects.
        If `use_sub_folder` is True, reads the first sub-folder in the prefix. If False, reads the prefix itself.

        :param limit: The maximum number of objects to read. If not specified, read all contents in the prefix.
        :param use_sub_folder: If True, reads the first sub-folder in the prefix. If False, reads the prefix itself.
        """
        objects = self.get_prefix_contents(
            limit=limit, prefix=self._sub_folder_prefix if use_sub_folder else None
        )
        return [
            obj.key
            for obj in objects
            if not self._is_hidden(obj) and not self._is_folder(obj)
        ]
