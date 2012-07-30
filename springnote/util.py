import re
try:
    from html.entities import entitydefs
except ImportError:
    from htmlentitydefs import entitydefs
from xml.dom import Node


def unescape(text):
    result = text
    def convert_entity(m):
        if m.group(1):
            try:
                return chr(int(m.group(2)))
            except ValueError:
                return m.group(0)

        return entitydefs.get(m.group(2), m.group(0))

    result = re.sub(r'&(#?)(.+?);', convert_entity, result)

    #def convert_uri(m):
    #    absolute_uri = urljoin(page_uri, m.group(2))
    #    return '%s="%s"' % (m.group(1), absolute_uri)
    #
    #result = re.sub(r'(src|href)="(.+?)"', convert_uri, result)

    return result


def node2dict(node):
    """ Converts xml.dom node to dictionary, provided that there's only one
        node per one tag name.
    """
    result = {}
    for child in node.childNodes:
        if child.nodeType != Node.ELEMENT_NODE:
            continue

        key = child.tagName
        
        grandchild = child.lastChild
        if (not grandchild) or (grandchild.nodeType != Node.TEXT_NODE):
            value = None
        else:
            value = grandchild.data

        result[key] = value

    return result

