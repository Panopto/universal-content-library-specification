from lxml import etree
import io
import os.path
import sys
import lib.required_elements_validator


def validate_xml(xmlfile, rel_xml_file, xsd_file, log_file):
    """
    This validates an xml againts its corresponding xsd file. Checks for xml
    syntax errors (independent of any xsd) and schema errors (as dictated by
    an xsd).
    """
    xmldoc = None

    # parse xml
    try:
        log_file.write('Validating '
                       + rel_xml_file
                       + ' for syntactical correctness...')
        xmldoc = etree.parse(xmlfile)
        log_file.write('Xml well formed, syntax ok.\n')

    # check for file IO error
    except IOError:
        log_file.write(rel_xml_file + ' is an invalid file\n')

    # check for XML syntax errors
    except etree.XMLSyntaxError as err:
        log_file.write(rel_xml_file
                       + ' has syntax error, see error_syntax.log\n')
        with open('error_syntax.log', 'a') as error_log_file:
            error_log_file.write(str(err.error_log) + '\n')

    except Exception as e:
        log_file.write('Unknown error validating '
                       + rel_xml_file
                       + ': '
                       + str(e)
                       )
        raise

    # validate against schema
    try:
        log_file.write('Validating '
                       + rel_xml_file
                       + ' for schema correctness...')
        xml_schema = etree.XMLSchema(etree.parse(xsd_file))
        xml_schema.assertValid(xmldoc)
        log_file.write('Xml is valid, schema validation ok.\n')

    except etree.DocumentInvalid as err:
        error = str(err.error_log) + '\n'

        # If ucs has missing required elements, lxml doesn't provide info on
        # which ones are missing. This will provide that information.
        if (
                "Missing child element(s)" in error or
                "This element is not expected" in error
           ):
            missing_elements = (
                lib.required_elements_validator.get_missing_elements(xmldoc)
                )
            validation_error = "Error: one or more instances of the following \
                                required elements are missing:\n"

            for element in missing_elements:
                validation_error += element + "\n"
        else:
            validation_error = error

        log_file.write(validation_error)
        raise

    except IOError as e:
        log_file.write('IOError loading xsd file '
                       + xsd_file
                       + ': '
                       + str(e))
        raise

    except Exception as e:
        log_file.write('Error validating ' + rel_xml_file + ': ' + str(e))
        raise

    return xmldoc
