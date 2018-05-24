from lxml import etree
from io import StringIO
import boto3
import io
import os.path
import sys
import lib.validate_xml
import lib.validate_ucs_xml
import lib.s3utils
import lib.constants
from lib.storage import StorageType


def validate_directory(args, rel_xml_path, store, log_file):
    """
    Recursively validates all UCLS Directories starting from
    a passed in directory xml (rel_xml_path).
    """
    directory_xml = store.get_local_path(rel_xml_path)

    if not os.path.isfile(directory_xml):
        log_file.write("Error: " + rel_xml_path
                       + " doesn't exist or failed to downloaed")
        return False

    noErrors = True

    tree = lib.validate_xml.validate_xml(
            directory_xml,
            os.path.basename(directory_xml),
            os.path.abspath(__file__ + "/../../../../schemas/")
            + "/"
            + lib.constants.UCLS_DIRECTORY_XSD, log_file
        )

    if not tree:
        noErrors = False
    else:
        log_file.write('Validating '
                       + rel_xml_path
                       + ' Sessions and SubDirectories...\n')

        subdirs = tree.xpath(
                '/ucls:Directory/ucls:Subdirectories/ucls:Directory',
                namespaces=lib.constants.UCLSNS
            )

        if(len(subdirs) == 0):
            log_file.write(rel_xml_path + " has no subdirectories\n")
        else:
            log_file.write(str(len(subdirs))
                           + ' subdirectories found for '
                           + rel_xml_path + ':\n')
            for node in subdirs:
                log_file.write(node.text + '\n')

        # Validate sessions
        sessions = tree.xpath(
                '/ucls:Directory/ucls:Sessions/ucls:Session',
                namespaces=lib.constants.UCLSNS
            )

        for node in sessions:
            log_file.write('Validating Session file ' + node.text + '\n')
            if not lib.validate_ucs_xml.validate_ucs(
                    args,
                    node.text,
                    os.path.abspath(__file__ + "/../../../../schemas/")
                    + "/"
                    + lib.constants.UCS_XSD,
                    store,
                    log_file
                    ):
                noErrors = False

        # Validate subdirectories
        # The xml/xsd validation near the top ensures are there RootDirectory
        # nodes at this point, so no need to check 'subdirs' for None
        for node in subdirs:
            log_file.write('Validating SubDirectory file ' + node.text + ':\n')
            if not validate_directory(args, node.text, store, log_file):
                noErrors = False

    return noErrors
