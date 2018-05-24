import argparse
import os
import sys
from mock import patch
import lib.validate_xml
from lib.storage import StorageType


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t',
        '--storage-type',
        type=lambda storagetype: StorageType[storagetype],
        choices=list(StorageType), dest='storage_type')
    parser.add_argument(
        '-l',
        '--library-xml',
        default="library.xml",
        dest='library_xml')
    parser.add_argument(
        '-o',
        '--log-oile',
        dest='log_file')
    parser.add_argument(
        '-v',
        '--validate-checksum',
        default=False,
        dest='validate_checksum')

    args = parser.parse_args()
    return args


def test_videoonly():
    testargs = ["prog",
                "-l", "..\\..\\..\\samples\\video-only\\library.xml",
                "-t", "unc",
                "-o", "output.log"]
    with patch.object(sys, 'argv', testargs):
        args = get_args()
        result = lib.validate_ucls_library_xml.validate_library(args)
        assert result is True


def test_primary_secondary_ppt_and_cuts():
    testargs = ["prog",
                "-l",
                "..\\..\\..\\samples\\primary-secondary-ppt-and-cuts\\library.xml",
                "-t",
                "unc",
                "-o",
                "output.log"]
    with patch.object(sys, 'argv', testargs):
        args = get_args()
        result = lib.validate_ucls_library_xml.validate_library(args)
        assert result is True


def test_ppt_only():
    testargs = ["prog",
                "-l", "..\\..\\test-content\\ppt-only\\library.xml",
                "-t", "unc",
                "-o", "output.log"]
    with patch.object(sys, 'argv', testargs):
        args = get_args()
        result = lib.validate_ucls_library_xml.validate_library(args)
        assert result is True


def test_test_three_level_session_folders():
    testargs = ["prog",
                "-l",
                "..\\..\\..\\samples\\three-level-session-folders\\library.xml",
                "-t",
                "unc",
                "-o",
                "output.log"]
    with patch.object(sys, 'argv', testargs):
        args = get_args()
        result = lib.validate_ucls_library_xml.validate_library(args)
        assert result is True


def test_bad_checksum():
    testargs = ["prog",
                "-l", "..\\..\\test-content\\bad-checksum\\library.xml",
                "-t", "unc",
                "-o", "output.log",
                "--validate-checksum", "True"]
    with patch.object(sys, 'argv', testargs):
        args = get_args()
        result = lib.validate_ucls_library_xml.validate_library(args)
        assert result is False


def test_missing_required_fields():
    testargs = ["prog",
                "-l",
                "..\\..\\test-content\\missing-required-fields\\library.xml",
                "-t",
                "unc",
                "-o",
                "output.log"]
    with patch.object(sys, 'argv', testargs):
        args = get_args()
        result = lib.validate_ucls_library_xml.validate_library(args)
        assert result is False
