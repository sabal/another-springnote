from base64 import b64encode
from cgi import escape
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.encoders import encode_noop
try:
    from http.client import HTTPSConnection
except ImportError:
    from httplib import HTTPSConnection
import socket
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
from xml.dom.minidom import parseString, getDOMImplementation

from .util import node2dict

APP_KEY = '06f05bc881d795dee3eadd36f40913500b444605'


class Page(object):
    def __init__(self, **kwargs):
        """
        Precedence: xml, dom, the rest

        @keyword xml: an XML to parse
        @keyword dom: dom to parse
        @keyword title
        @keyword relation_is_part_of
        @keyword source
        """

        properties = [
            'title',
            'relation_is_part_of',
            'identifier',
            'date_created',
            'date_modified',
            'source',
            'creator',
            'version',
            'contributor_modified',
            'uri'
        ]
        # TODO: ACL
        if 'xml' in kwargs:
            try:
                dom = parseString(kwargs['xml'])
            except:
                raise ValueError("Malformed XML:\n" + kwargs['xml'])
            if dom.documentElement.tagName == 'errors':
                raise ValueError(kwargs['xml'])
            elif dom.documentElement.tagName == 'html':
                for div in dom.documentElement.getElementsByTagName('div'):
                    if div.getAttribute('class') == 'errorPage':
                        # <div id="error502" class="errorPage">
                        raise ValueError(kwargs['xml'],
                                status=int(div.getAttribute('id')[5:]))
            node_dict = node2dict(dom.documentElement)
            # TODO: rights
        elif 'dom' in kwargs:
            dom = kwargs['dom']
            if dom.tagName == 'errors':
                raise ValueError(kwargs['xml'])
            node_dict = node2dict(dom)
        else:
            node_dict = {}
            for key in properties:
                if key in kwargs:
                    node_dict[key] = kwargs[key]
        for key in properties:
            if key in node_dict:
                self.__dict__[key] = node_dict[key]
            else:
                self.__dict__[key] = None
        if self.__dict__['relation_is_part_of']:
            self.__dict__['relation_is_part_of'] = int(
                    self.__dict__['relation_is_part_of'])
        if self.__dict__['identifier']:
            self.__dict__['identifier'] = int(self.__dict__['identifier'])
        # TODO: datetime
        if self.__dict__['source']:
            pass  # self.__dict__['source'] = unescape(self.__dict__['source'])
        else:
            self.__dict__['source'] = '<p><br/></p>'

    def append_node(self, doc, tag_name, text, type_=None):
        page = doc.documentElement
        elem = doc.createElement(tag_name)
        if type_:
            elem.setAttribute('type', type_)
        if not text:
            elem.setAttribute('nil', 'true')
        else:
            text_node = doc.createTextNode(text)
            elem.appendChild(text_node)
        page.appendChild(elem)

    def writable_dom(self):
        impl = getDOMImplementation()
        doc = impl.createDocument('http://api.springnote.com', 'page', None)
        self.append_node(doc, 'title', self.__dict__['title'])
        self.append_node(doc, 'relation_is_part_of',
                str(self.__dict__['relation_is_part_of']), 'integer')
        self.append_node(doc, 'source', self.__dict__['source'])
        return doc

    def full_xml(self):
        doc = self.writable_dom()
        self.append_node(doc, 'identifier',
                str(self.__dict__['identifier']), 'integer')
        self.append_node(doc, 'date_created',
                str(self.__dict__['date_created']), 'datetime')
        self.append_node(doc, 'date_modified',
                str(self.__dict__['date_modified']), 'datetime')
        self.append_node(doc, 'uri', self.__dict__['uri'])
        return doc.toxml('utf-8')

    def writable_xml(self):
        return self.writable_dom().toxml('utf-8')


class SpringnoteException(Exception):
    def __init__(self, url, xml, **kwargs):
        self.url = url
        self.xml = xml
        self.status = kwargs.get('status', None)

    def __str__(self):
        if self.status:
            return "Error {} at {}: {}".format(self.status, self.url, self.xml)
        return 'Error at {}: {}'.format(self.url, self.xml)


class SpringnoteRequest:
    SERVER_ADDRESS = 'api.springnote.com'

    def __init__(self, openid, user_key):
        user = quote(openid, '')
        password = '.'.join([user_key, APP_KEY])
        self.auth_key = b64encode(':'.join([user, password]).encode('ascii')).decode('ascii')

    def _request(self, method, path, body, headers):
        """Don't call this function directly."""
        success = False
        retry = 0
        while retry < 3:
            try:
                bot = HTTPSConnection(self.SERVER_ADDRESS)
                bot.request(method, path, body, headers)
                response = bot.getresponse()
                result = response.read()
                success = True
                break
            except socket.error as (errno, message):
                for encoding in ['utf8', 'cp949']:
                    try:
                        message = string.decode(message)
                    except:
                        pass
                print("Error: {} {}. Retrying...".format(errno, message))
            except Exception as e:
                print("Error: {}. Retrying...".format(repr(e)))
            finally:
                bot.close()
                retry += 1
        if retry > 1:
            print("Success. Continuing...")
        if not success:
            raise SpringnoteException(path, "Could not download")
        if response.status != 200:  # 200 OK
            raise SpringnoteException(path, result, status=response.status)
            # TODO: raise specific error
        if not result:
            raise SpringnoteException(path, "Response body empty")

        return result

    def _fetch(self, method, path, xml=None):
        """Don't call this function directly."""
        headers = {'Authorization': 'Basic %s' % self.auth_key}
        if not xml:
            return self._request(method, path, None, headers)
        else:
            headers['Content-Type'] = 'application/xml'
            headers['Content-Length'] = str(len(xml))
            return self._request(method, path, xml, headers)

    def _create_argument(self, **kwargs):
        args = {}
        if 'domain' in kwargs:
            args['domain'] = kwargs['domain']
        if not args:
            return ''
        result = []
        for key, value in args.items():
            result.append('='.join([key, escape(value)]))
        # TODO: use urllib
        return '?' + '&'.join(result)

    def get_pages(self, **kwargs):
        """
            Gets a page list.
            @keyword domain
        """
        path = '/pages.xml' + self._create_argument(**kwargs)
        response = self._fetch('GET', path)
        doc = parseString(response)
        result = []
        for page_node in doc.documentElement.getElementsByTagName('page'):
            result.append(Page(dom=page_node))
        return result

    def get_page(self, id_, **kwargs):
        """
            Gets a page.
            @keyword domain
        """
        path = '/pages/%d.xml' % id_ + self._create_argument(**kwargs)
        response = self._fetch('GET', path)
        return Page(xml=response)

    def modify_page(self, id_, page, **kwargs):
        """
            Modifies a page.
            @keyword domain
        """
        path = '/pages/%d.xml' % id_ + self._create_argument(**kwargs)
        response = self._fetch('PUT', path, page.to_writable_xml())
        result = Page(xml=response)
        return result

    def create_page(self, page, **kwargs):
        """
            Creates a page.
            @keyword domain
        """
        path = '/pages.xml' + self._create_argument(**kwargs)
        response = self._fetch('POST', path, page.to_writable_xml())
        result = Page(xml=response)
        return result

    def delete_page(self, id_, **kwargs):
        """
            Deletes a page.
            @keyword domain
        """
        path = '/pages/%d.xml' % id_ + self._create_argument(**kwargs)
        response = self._fetch('DELETE', path)
        return response

    def get_attachments(self, page_id, **kwargs):
        """Gets attachments list."""
        path = '/pages/%d/attachments.xml' % (
                page_id + self._create_argument(**kwargs))
        raise NotImplementedError

    def get_attachment(self, page_id, attachment_id, **kwargs):
        """Gets attachment."""
        path = '/pages/%d/attachment/%d.xml' % (
                (page_id, attachment_id) + self._create_argument(**kwargs))
        raise NotImplementedError

    def upload_attachment(self, page_id, filename, file_content, **kwargs):
        """Uploads attachment."""
        mime = MIMEMultipart('form-data')
        part = MIMEApplication(file_content, 'octet-stream', encode_noop)
        part.add_header('Content-Disposition', 'form-data', name='Filedata',
                filename=filename.encode('utf-8'))
        part.add_header('Content-Transfer-Encoding', 'binary')
        mime.attach(part)
        # we don't want mime.as_string(), because the format is different
        # from the one we should use in HTTP requests
        # all we wanted is a proper boundary string
        boundary = mime.get_boundary()
        body = '\r\n'.join([
            '--' + boundary,
            ('Content-Disposition: form-data; name="Filedata"; '
                'filename="{}"').format(filename.encode('utf-8')),
#            'MIME-Version: 1.0',
            'Content-Type: application/octet-stream',
#            'Content-Transfer-Encoding: binary',
            '',
            file_content,
            '--' + boundary + '--',
            '',
        ])
        path = '/pages/%d/attachments%s' % (
                page_id, self._create_argument(**kwargs))
        headers = {
            'Authorization': 'Basic %s' % self.auth_key,
            'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
            'Content-Length': str(len(body)),
        }
        try:
            return self._request('POST', path, body, headers)
        except SpringnoteException as ex:
            if ex.status >= 300 and ex.status < 400:  # it's a redirect
                return True  # TODO


class Tree:
    class Node:
        def __init__(self, page):
            self.page = page
            self.children = []

        def get_subpage_by_path(self, path):
            path_copy = []
            for directory in path:
                # for case-insensitive nature of Springnote
                path_copy.append(directory.lower())
            parent = self
            descendants = self.children
            while True:
                if not path_copy:
                    return parent.page
                if not descendants:
                    return None
                found = False
                for youngster in descendants:
                    if youngster.page.title.lower() == path_copy[0]:
                        parent = youngster
                        descendants = youngster.children
                        found = True
                        break
                if not found:
                    return None
                path_copy.pop(0)

    def __init__(self, xml):
        doc = parseString(xml)
        self.root = None
        self._hash = {}
        for dom in doc.documentElement.getElementsByTagName('page'):
            node = self.Node(Page(dom=dom))
            self._hash[node.page.identifier] = node
            if not node.page.relation_is_part_of:
                self.root = node  # XXX: root should be only one, shouldn't it?
        if not self.root:
            raise ValueError("Tree.__init__(): No root")
        for node in self._hash.values():
            if node == self.root:
                continue
            if node.page.relation_is_part_of not in self._hash:
                pass
#                raise ValueError(
#                        "Tree.__init__(): Broken tree structure")
            else:
                parent = self._hash[node.page.relation_is_part_of]
                parent.children.append(node)

    def to_xml(self):
        raise NotImplementedError  # XXX: Do we need Tree.toXML()?

    def get_node_by_identifier(self, identifier):
        return self._hash[identifier]

    def insert_page(self, page):
        parent = self.get_node_by_identifier(page.relation_is_part_of)
        new_node = self.Node(page)
        parent.children.append(new_node)
        self._hash[page.identifier] = new_node

    def modify_page(self, identifier, new_page):
        node = self.get_node_by_identifier(identifier)
        old_parent = self.get_node_by_identifier(node.page.relation_is_part_of)
        new_parent = self.get_node_by_identifier(new_page.relation_is_part_of)

        node.page = new_page
        old_parent.children.remove(node)
        new_parent.children.append(node)


class Springnote(SpringnoteRequest):
    def __init__(self, openid, user_key, **kwargs):
        SpringnoteRequest.__init__(self, openid, user_key)

        self.domain = False
        if 'domain' in kwargs:
            self.domain = kwargs['domain']

        self.tree = self.get_tree(**kwargs)
        self.root_node = self.tree.root
        self.root_page = self.tree.root.page

    def _filter_args(self, kwargs):
        result = {}
        if 'domain' in kwargs:
            result['domain'] = kwargs['domain']
        elif self.domain:
            result['domain'] = self.domain
        return result

    def get_tree(self, **kwargs):
        response = self._fetch('GET',
            '/pages.xml' + self._create_argument(**self._filter_args(kwargs)))
        return Tree(xml=response)

    def create_page(self, page, **kwargs):
        new_page = SpringnoteRequest.create_page(self, page,
                **self._filter_args(kwargs))
        self.tree.insert_page(new_page)
        return new_page

    def get_page(self, identifier, **kwargs):
        new_page = SpringnoteRequest.get_page(self, identifier,
                **self._filter_args(kwargs))
        self.tree.modify_page(identifier, new_page)
        return new_page

    def modify_page(self, identifier, page, **kwargs):
        new_page = SpringnoteRequest.modify_page(self, identifier, page,
                **self._filter_args(kwargs))
        self.tree.modify_page(identifier, new_page)
        return new_page
