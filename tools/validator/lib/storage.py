import os.path
import lib.s3utils
from abc import ABCMeta, abstractmethod
from enum import Enum


class StorageType(Enum):
    unc = 'unc'
    s3 = 's3'

    def __str__(self):
        return self.value


class IStorage(object):
    __metaclass__ = ABCMeta
    """
    Defines interface to enable program to seamlessly to do basic file
    operations regardless of where content library is in S3 or UNC location.
    """

    @abstractmethod
    def combine(self, path1, path2):
        pass

    @abstractmethod
    def get_local_path(self, relpath):
        pass

    @abstractmethod
    def file_exists(self, relpath):
        pass


class UncStorage(IStorage):
    def __init__(self, libraryrootpath):
        if os.path.isabs(libraryrootpath):
            self.libraryrootpath = libraryrootpath
        else:
            self.libraryrootpath = os.path.abspath(
                os.path.join(os.path.dirname(__file__), libraryrootpath))
        print(self.libraryrootpath)

    def combine(self, path1, path2):
        return os.path.join(path1, path2)

    def get_local_path(self, relpath):
        return os.path.join(self.libraryrootpath, relpath)

    def file_exists(self, relpath):
        return os.path.isfile(os.path.join(self.libraryrootpath, relpath))


class S3Storage(IStorage):
    def __init__(
            self,
            aws_access_key,
            aws_secret_key,
            aws_region,
            bucket,
            libraryrootpath,
            scratchdir,
            log_file
            ):
        self.bucket = bucket
        self.libraryrootpath = libraryrootpath
        self.scratchdir = scratchdir
        self.log_file = log_file
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region

    def combine(self, path1, path2):
        return os.path.join(path1, path2).replace('\\', '/')

    def get_local_path(self, relpath):
        s3path = self.libraryrootpath + '/' + relpath.replace('\\', '/')
        scratchsubdir = os.path.join(self.scratchdir, os.path.dirname(relpath))
        if not os.path.isdir(scratchsubdir):
            self.log_file.write('Creating scratch dir ' + scratchsubdir + '\n')
            os.makedirs(scratchsubdir)
        localfilepath = os.path.join(
            self.scratchdir,
            relpath
            ).replace('/', '\\')
        self.log_file.write('Downloading '
                            + s3path
                            + ' to '
                            + localfilepath
                            + '\n')
        lib.s3utils.get_file_from_s3(
            self.aws_access_key,
            self.aws_secret_key,
            self.aws_region,
            localfilepath,
            self.bucket,
            s3path
            )
        return localfilepath

    def file_exists(self, relpath):
        return lib.s3utils.file_exists(
            self.aws_access_key,
            self.aws_secret_key,
            self.aws_region,
            self.bucket,
            relpath
            )


def get_storage_instance(args, log_file):
    if args.storage_type == StorageType.unc:
        return UncStorage(args.library_root_dir)
    elif args.storage_type == StorageType.s3:
        return S3Storage(
            args.aws_access_key,
            args.aws_secret_key,
            args.aws_region,
            args.aws_bucket,
            args.library_root_dir,
            args.scratch_dir,
            log_file
            )
