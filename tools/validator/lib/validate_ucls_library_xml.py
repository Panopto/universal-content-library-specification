from lxml import etree
from io import StringIO
import io
import os.path
import sys
import uuid
import lib.validate_xml
import lib.validate_ucls_directory_xml
import lib.s3utils
import lib.constants
from lib.storage import StorageType
from time import gmtime, strftime


def create_log_file(args):
    """
    Set up a file for logging
    """
    currenttime = strftime("%Y-%m-%d %HH-%MM-%SS", gmtime())
    if args.log_file is None:
        log_file = open(currenttime + '.log', 'w')
    else:
        log_file = open(args.log_file, 'a')

    log_file.write("Executing program at " + currenttime + '\n')

    return log_file


def setup_storage_instance(args, log_file):
    """
    Set up a storage instance for where UCLS library is (local drive or s3)
    """

    # instantiate the right concrete storage manager
    store = lib.storage.get_storage_instance(args, log_file)

    if not store.file_exists(args.library_xml):
        print(args.library_xml + ' not found, aborting...')
        exit()

    # create scratch dir for downloads if s3
    if args.storage_type == StorageType.s3:
        log_file.write('Creating scratch dir ' + args.scratch_dir + '\n')
        if not os.path.isdir(args.scratch_dir):
            os.makedirs(args.scratch_dir)
        log_file.write('Scratch dir ' + args.scratch_dir + ' created\n')

    return store


def validate_library(args):
    """
    Top level function where validation starts via the library xml
    in the store root directory
    """
    noErrors = True

    args.library_root_dir = os.path.dirname(args.library_xml)
    args.library_xml = os.path.basename(args.library_xml)

    log_file = create_log_file(args)
    store = setup_storage_instance(args, log_file)

    library_xml = store.get_local_path(args.library_xml)

    if not os.path.isfile(library_xml):
        print("Unable to download library.xml, aborting\n")
        return False

    tree = lib.validate_xml.validate_xml(
            library_xml,
            args.library_xml,
            os.path.abspath(__file__ + "/../../../../schemas/")
            + "/"
            + lib.constants.UCLS_LIBRARY_XSD,
            log_file
        )

    if tree is None:
        noErrors = False
    else:
        instances = tree.xpath(
                '/ucls:Library/ucls:RootDirectories/ucls:RootDirectory',
                namespaces=lib.constants.UCLSNS
            )

        for node in instances:
            log_file.write('Validating RootDirectory file '
                           + node.text + ':\n')
            if not lib.validate_ucls_directory_xml.validate_directory(
                    args,
                    node.text,
                    store,
                    log_file
                    ):
                noErrors = False

    return noErrors
