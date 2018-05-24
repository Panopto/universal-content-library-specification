from lxml import etree
from io import StringIO
import io
import os.path
import sys
import lib.validate_xml
import lib.required_elements_validator
import lib.crc32
import lib.s3utils
import lib.constants
from lib.storage import StorageType


def validate_files(args, xml_doc, rel_sub_dir, store, validate_checksum, log_file):
    """
    Validates that files specified in UCS file exist. Also checks that their CRCs
    match what's specified in the UCS file if validate_checksum param is true.
    """

    noErrors = True

    # xpaths of all places where a file can exist for a session
    file_xpaths = [
        '/ucs:Session/ucs:Videos/ucs:Video/ucs:File',
        '/ucs:Session/ucs:Videos/ucs:Video/'
        + 'ucs:Transcripts/ucs:Transcript/ucs:File',
        '/ucs:Session/ucs:Presentations/ucs:Presentation/ucs:File',
        '/ucs:Session/ucs:Images/ucs:File']

    for file_xpath in file_xpaths:
        instances = xml_doc.xpath(file_xpath, namespaces=lib.constants.UCSNS)
        for xfile in instances:
            if xfile.get("Checksum") is not None:
                file = store.get_local_path(
                    store.combine(rel_sub_dir, xfile.text)
                    )

                if os.path.isfile(file):
                    if validate_checksum:
                        calc_checksum = lib.crc32.crc32(file)
                        if int(xfile.get("Checksum"), 16) == calc_checksum:
                            log_file.write(xfile.text + ' checksum is valid\n')
                        else:
                            log_file.write('Error: checksum '
                                           + xfile.get("Checksum")
                                           + ' does not match calculated value '
                                           + hex(calc_checksum) + '\n')
                            noErrors = False
                else:
                    log_file.write('Error: '
                                   + xfile.text
                                   + " doesn't exist\n")
                    noErrors = False
            else:
                log_file.write(xfile.text + ' has no checksum attribute\n')

    return noErrors


def validate_ucs(args, rel_xml_path, xsd_file, store, log_file):
    """
    Validates a UCS xml, including file checksums if commandline
    options dictate so.
    """

    noErrors = True

    xmlfile = store.get_local_path(rel_xml_path)

    try:
        xml_doc = lib.validate_xml.validate_xml(
            xmlfile, rel_xml_path, xsd_file, log_file
            )
    except:
        noErrors = False

    # validate files (including checksums)
    if noErrors:
        if not validate_files(
                args,
                xml_doc,
                os.path.dirname(rel_xml_path),
                store,
                args.validate_checksum,
                log_file
                ):
            noErrors = False

    return noErrors
