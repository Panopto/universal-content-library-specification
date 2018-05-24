#!/usr/bin/python

import argparse
import os
import lib
import sys
from lib.storage import StorageType


def main():
    """
    Main method for validating a UCLS folder to ensure that UCLS/UCS xml files
    are valid and that content files exist as they should as per the xml files.
    """
    if sys.version_info[0] < 2:
        raise Exception("The version of Python must 2 or greater.")

    parser = argparse.ArgumentParser(
        description='Validates a UCLS content library for UCLS/UCS manifest '
                    'correctness, as well as for file existences.')
    parser.add_argument(
        '-t',
        '--storage-type',
        default='unc',
        type=lambda storagetype: StorageType[storagetype],
        choices=list(StorageType), dest='storage_type',
        required=False,
        help='Specifies whether working-directory is s3 or unc location.')
    parser.add_argument(
        '-b',
        '--aws-bucket',
        default=None,
        dest='aws_bucket',
        required=False,
        help='AWS access key. Required if working-directory is S3.')
    parser.add_argument(
        '-a',
        '--aws-access-key',
        default=None,
        dest='aws_access_key',
        required=False,
        help='AWS access key to use if library storage type is S3. '
             'If not specified, script will use default AWS CLI profile.')
    parser.add_argument(
        '-s',
        '--aws-secret-key',
        default=None,
        dest='aws_secret_key',
        required=False,
        help='AWS secret key to use if library storage type is S3. If not '
             'specified, script will use default AWS CLI profile.')
    parser.add_argument(
        '-r',
        '--aws-region',
        default='us-east-1',
        dest='aws_region',
        required=False,
        help='AWS region to use if library storage type is S3. If not '
             'specified, script will use default AWS CLI profile.')
    parser.add_argument(
        '-l',
        '--library-xml',
        default=None,
        dest='library_xml',
        required=False,
        help='Full path to UCLS library xml in the root of the library store.')
    parser.add_argument(
        '-o',
        '--log-oile',
        dest='log_file',
        required=False,
        help='Filename of output log file. Based on current time if '
             'not overridden')
    parser.add_argument(
        '-v',
        '--validate-checksum',
        dest='validate_checksum',
        required=False,
        help='Validates file checksum if attribute is present in xml.',
        action='store_true')
    parser.add_argument(
        '-d',
        '--scratch-dir',
        default="./scratch",
        dest='scratch_dir',
        required=False,
        help='Scratch dir for downloading UCLS/UCS manifest and media files.')

    args = parser.parse_args()

    print('\nPerforming validation...')

    result = lib.validate_ucls_library_xml.validate_library(args)

    if result:
        print('Everything looks good!')
    else:
        print('Done, errors found, check logs')


if __name__ == '__main__':
    main()
