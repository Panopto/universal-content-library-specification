import lib.constants


def get_missing_elements(tree):
    """
    This checks for UCS nodes that must exist if their parent node exists and
    returns a list of those elements. Since lxml gives only a generic message
    about missing elements in such cases, this is useful for providing info
    what exactly what elements were missing in a UCS xml.
    """
    required_elements = {
        '/ucs:Session':
            ['/ucs:Title'],
        '/ucs:Session/ucs:Videos/ucs:Video':
            ['/ucs:Start', '/ucs:File', '/ucs:Type'],
        '/ucs:Session/ucs:Videos/ucs:Video/ucs:TableOfContents':
            ['/ucs:Title', '/ucs:Time'],
        '/ucs:Session/ucs:Videos/ucs:Video/ucs:Transcripts/ucs:Transcript':
            ['/ucs:File'],
        '/ucs:Session/ucs:Cuts/ucs:Cut':
            ['/ucs:Start', '/ucs:Duration'],
        '/ucs:Session/ucs:Presentations/ucs:Presentation':
            ['/ucs:Start', '/ucs:File', '/ucs:SlideChanges'],
        '/ucs:Session/ucs:Presentations/ucs:Presentation/'
            + 'ucs:SlideChanges/ucs:SlideChange':
            ['/ucs:Title', '/ucs:Time', '/ucs:SlideNumber'],
        '/ucs:Session/ucs:Images/ucs:Image':
            ['/ucs:File', '/ucs:Time']
        }

    missing_elements = []

    for xpath_to_search in list(required_elements.keys()):
        instances = tree.xpath(xpath_to_search, namespaces=lib.constants.UCSNS)
        for node in instances:
            for required_child in required_elements[xpath_to_search]:
                if not node.xpath(
                        '.' + required_child,
                        namespaces=lib.constants.UCSNS
                        ):
                    missing_elements.insert(
                        0,
                        xpath_to_search + required_child
                        )

    return missing_elements
