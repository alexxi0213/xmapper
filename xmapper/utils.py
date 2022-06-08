from collections import Counter
import copy
import os

from lxml import etree
from untangle import Element
from untangle import is_url, is_string
from untangle import StringIO
from xml.sax import make_parser, handler


class CachedProperty(object):
    """
    Descriptor (non-data) for building an attribute on-demand on first use.
    """
    def __init__(self, factory):
        """
        <factory> is called such: factory(instance) to build the attribute.
        """
        self._attr_name = factory.__name__
        self._factory = factory

    def __get__(self, instance, owner):
        # Build the attribute.
        attr = self._factory(instance)

        # If readonly mode cache the value; hide ourselves.
        if instance.mode == 'r':
            setattr(instance, self._attr_name, attr)
        return attr


class Node(Element):
    def __init__(self, name, attributes, mode='rw'):
        super(Node, self).__init__(name, attributes)
        self.position = None
        self.mode = mode

    def raw_paths(self):
        if not self.children:
            if self.position is not None:
                return [[self._name] + [self.position]]
            else:
                return [[self._name]]
        raw_paths = []
        for child in self.children:
            for path in child.raw_paths():
                if self.position is not None:
                    raw_paths.append([self._name] + [self.position] + path)
                else:
                    raw_paths.append([self._name] + path)
        return raw_paths

    def build_position(self):
        names = [i._name for i in self.children]
        count = Counter(names)
        duplicates = {k: 0 for k, v in count.items() if v > 1}
        for item in duplicates:
            for child in self.children:
                if child._name == item:
                    child.position = str(duplicates[item])
                    duplicates[item] = duplicates[item] + 1

    def clean_path_cache(self):
        """
        clean the path cache after the structure changed
        pls use this on top level tree
        """
        if 'paths' in self.__dict__:
            delattr(self, 'paths')
        if 'all_paths' in self.__dict__:
            delattr(self, 'all_paths')
        for child in self.children:
            child.clean_path_cache()

    @CachedProperty
    def paths(self):
        """
        paths contains all the full paths in xml tree
        partial path not included compare to all_paths:
        <export>
          <listings>
            <ad>
              <agent>
                <id></id>
              </agent>
            </ad>
          </listings>
        </export>
        {'export.listings.ad.agent.id'}
        :return set of full paths
        :type set
        """
        raw_paths = copy.deepcopy(self.raw_paths())
        for p in raw_paths:
            if None in p:
                p.remove(None)
        if self._name is not None:
            for p in raw_paths:
                del p[0]
        paths = {str('.'.join(p)) for p in raw_paths}
        return paths

    @CachedProperty
    def all_paths(self):
        """
        all paths contails all the paths in xml tree
        include partial path and full path like:
        <export>
          <listings>
            <ad>
              <agent>
                <id></id>
              </agent>
            </ad>
          </listings>
        </export>
        {'export',
         'export.listings',
         'export.listings.ad',
         'export.listings.ad.agent',
         'export.listings.ad.agent.id'}
        :return: a set of all the paths
        :type set
        """
        paths = set()
        for full_path in self.paths:
            partials = full_path.split('.')
            for i in range(1, len(partials) + 1)[::-1]:
                partial = partials[0:i]
                if partial:
                    to_add_path = '.'.join(partial)
                    if to_add_path in paths:
                        break
                    else:
                        paths.add(to_add_path)
        return paths

    def get_value_by_path(self, path):
        """
        make sure your path in a valid path
        that means it should be in self.paths set
        :param path: a valid path in self.paths
        :return: '' or the object.cdata for that path
        """
        obj = self
        if isinstance(path, str):
            path_list = path.split('.')
            for i in path_list:
                if i.isdigit():
                    obj = obj[int(i)]
                elif isinstance(obj, list):
                    try:
                        obj = getattr(obj[0], i)
                    except AttributeError:
                        return ''
                elif i[0] == '@':
                    return obj._attributes.get(i[1:], '')
                else:
                    try:
                        obj = getattr(obj, i)
                    except AttributeError:
                        return ''
        if isinstance(obj, list):
            return [node.cdata.strip() for node in obj]
        if isinstance(obj, str) and obj.strip() == '':
            return []
        if isinstance(obj, str):
            return obj
        return obj.cdata.strip()

    def get_value_by_tag(self, tag):
        """
        get all the object.cdata of that tag name
        in object
        :param tag: tag name
        :return: empty list or list of value
        """
        if not self.children:
            if self._name == tag:
                return [self.cdata]
            else:
                return
        results = []
        for child in self.children:
            result = child.get_value_by_tag(tag)
            if result:
                results += result
        return results

    def set_value_by_tag(self, tag, value):
        """
        set Node.cdata with that tag name
        make sure the tag is unique in you Node
        otherwise it will set all the tags of that name
        :param tag: tag name
        :value value: value for that tag
        """
        if self._name == tag:
            self.cdata = value
        for child in self.children:
            child.set_value_by_tag(tag, value)

    def get_attr_by_tag(self, tag):
        """
        get all the object._attributes of that tag name
        in object
        :param tag: tag name
        :return: empty list or list of Node object attributes
        """
        if self._name == tag:
            return [self._attributes]
        results = []
        for child in self.children:
            result = child.get_attr_by_tag(tag)
            if result:
                results += result
        return [i for i in results if i]

    def get_attr_value_by_tag(self, tag, attr_key):
        """
        get all the object._attributes value of that tag name
        and attribute key name in object
        :param tag: tag name
        :param attr_key: attribute key name
        :return: empty list or list of Node object attribute value
        """
        if self._name == tag:
            return [self._attributes.get(attr_key, '')]
        results = []
        for child in self.children:
            result = child.get_attr_value_by_tag(tag, attr_key)
            if result:
                results += result
        return [i for i in results if i]

    def get_obj_by_tag(self, tag):
        """
        get all the sub objects of that tag name
        in object
        :param tag: tag name
        :return: empty list or list of Node object
        """
        if self._name == tag:
            return [self]
        results = []
        for child in self.children:
            result = child.get_obj_by_tag(tag)
            if result:
                results += result
        return results

    def get_obj_by_attr_value(self, tag, attr_key, value):
        """
        get all the sub objects of that tag name
        and object[attr_key] == value
        :param tag: tag name
        :return: empty list or list of Node object
        """
        if self._name == tag and \
                self._attributes.get(attr_key) == value:
            return [self]
        results = []
        for child in self.children:
            result = child.get_obj_by_attr_value(tag, attr_key, value)
            if result:
                results += result
        return results

    def get_object_by_path(self, path):
        obj = self
        if isinstance(path, str):
            if path not in self.all_paths:
                return
            path_list = path.split('.')
            for i in path_list:
                try:
                    if i.isdigit():
                        obj = obj[int(i)]
                    else:
                        obj = getattr(obj, i)
                except AttributeError:
                    return
        return obj

    def get_attr_by_path(self, path):
        obj = self
        if isinstance(path, str):
            path_list = path.split('.')
            for i in path_list:
                if i.isdigit():
                    obj = obj[int(i)]
                else:
                    obj = getattr(obj, i)
        return obj._attributes

    def get_attr_value_by_path(self, path):
        """
        get attribute value by path
        path should be like property.agent.@name
        the last sub path should be start with @
        :param path: path string
        :return: attribute value
        """
        obj = self
        attr_key = ''
        if isinstance(path, str):
            path_list = path.split('.')
            attr_key = path_list[-1].strip('@')
            if '.'.join(path_list[:-1]) not in self.all_paths:
                return ''
            for i in path_list[:-1]:
                if i.isdigit():
                    obj = obj[int(i)]
                else:
                    obj = getattr(obj, i)
        return obj._attributes.get(attr_key, '')

    def set_value_by_path(self, path, value):
        obj = self
        if isinstance(path, str):
            path_list = path.split('.')
            for i in path_list:
                if i.isdigit():
                    obj = obj[int(i)]
                else:
                    obj = getattr(obj, i)
            if isinstance(value, list):
                for idx, val in enumerate(value):
                    setattr(obj[idx], 'cdata', val)
            elif isinstance(obj, list):
                setattr(obj[0], 'cdata', value)
            else:
                setattr(obj, 'cdata', value)

    def set_attr_by_path(self, path, value):
        obj = self
        if isinstance(path, str):
            path_list = path.split('.')
            for i in path_list:
                if i.isdigit():
                    obj = obj[int(i)]
                else:
                    obj = getattr(obj, i)
            for k, v in value.items():
                obj._attributes[k] = v

    @property
    def value_mapping(self):
        mapping = {}
        for i in self.paths:
            mapping[i] = self.get_value_by_path(i)
        return mapping

    @property
    def search_mapping(self):
        mapping = {}
        for k, v in self.value_mapping.items():
            mapping[v] = mapping.get(v, [])
            mapping[v].append(k)
        return mapping

    @property
    def attr_mapping(self):
        mapping = {}
        for i in self.paths:
            mapping[i] = self.get_attr_by_path(i)
        return mapping


class Handler(handler.ContentHandler):
    """
    SAX handler which creates the Python object structure out of ``Node``s
    """
    def __init__(self,  mode='rw'):
        self.mode = mode
        self.root = Node(None, None, self.mode)
        self.root.is_root = True
        self.elements = []
        self.index = {}

    def startElement(self, name, attributes):
        name = name.replace('-', '~')
        name = name.replace('.', '_')
        name = name.replace(':', '*')
        attrs = dict()
        for k, v in attributes.items():
            attrs[k] = v
        element = Node(name, attrs, self.mode)
        self.index[element._name] = 0
        if len(self.elements) > 0:
            self.elements[-1].add_child(element)
            self.index[element._name] = self.index[element._name] + 1
        else:
            self.root.add_child(element)
            self.index[element._name] = self.index[element._name] + 1
        self.elements.append(element)

    def endElement(self, name):
        self.elements[-1].build_position()
        self.elements.pop()

    def characters(self, cdata):
        self.elements[-1].add_cdata(cdata)


def parse(filename, mode='rw', **parser_features):
    """
    Interprets the given string as a filename, URL or XML data string,
    parses it and returns a Python object which represents the given
    document.

    Extra arguments to this function are treated as feature values to pass
    to ``parser.setFeature()``. For example, ``feature_external_ges=False``
    will set ``xml.sax.handler.feature_external_ges`` to False, disabling
    the parser's inclusion of external general (text) entities such as DTDs.

    Raises ``ValueError`` if the first argument is None / empty string.

    Raises ``AttributeError`` if a requested xml.sax feature is not found in
    ``xml.sax.handler``.

    Raises ``xml.sax.SAXParseException`` if something goes wrong
    during parsing.
    """
    if filename is None or (is_string(filename) and filename.strip()) == '':
        raise ValueError('parse() takes a filename, URL or XML string')
    parser = make_parser()
    for feature, value in parser_features.items():
        parser.setFeature(getattr(handler, feature), value)
    sax_handler = Handler(mode)
    parser.setContentHandler(sax_handler)
    if is_string(filename) and (os.path.exists(filename) or is_url(filename)):
        parser.parse(filename)
    else:
        if hasattr(filename, 'read'):
            parser.parse(filename)
        else:
            parser.parse(StringIO(filename))

    return sax_handler.root


def build_etree(obj):
    """
    :param obj: obj must be instance of xmapper Node
    :return: etree object
    """
    if not obj.children:
        return element_gen(obj)
    else:
        tree = element_gen(obj)
        position = 0
        for child in obj.children:
            tree.insert(position, build_etree(child))
            position += 1
        return tree


def dump_xml(obj, xml_name):
    if not isinstance(obj, Node):
        raise TypeError('input must be a Xmapper.Node instance')

    if obj._name is not None:
        temp_tree = build_etree(obj)
    else:
        temp_tree = build_etree(obj.children[0])

    xml_str = etree.tostring(temp_tree, encoding='utf-8',
                             xml_declaration=True, pretty_print=True)
    parser = etree.XMLParser(remove_blank_text=True)
    temp_tree = etree.XML(xml_str, parser)
    new_tree = etree.ElementTree(temp_tree)
    new_tree.write(
        xml_name,
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=True)


def dump_str(obj):
    if not isinstance(obj, Node):
        raise TypeError('input must be a Xmapper.Node instance')

    if obj._name is not None:
        temp_tree = build_etree(obj)
    else:
        temp_tree = build_etree(obj.children[0])

    temp_str = etree.tostring(temp_tree, encoding='utf-8',
                              xml_declaration=True, pretty_print=True)
    parser = etree.XMLParser(remove_blank_text=True)
    new_tree = etree.XML(temp_str, parser)
    temp_tree = etree.ElementTree(new_tree)
    xml_str = etree.tostring(temp_tree, encoding='utf-8',
                             xml_declaration=True, pretty_print=True)
    return xml_str.decode('utf-8')


def element_gen(obj):
    if not isinstance(obj, Node):
        raise TypeError('input must be a Xmapper.Node instance')

    tag_name = obj._name
    tag_name = tag_name.replace('_', '.')
    tag_name = tag_name.replace('*', ':')
    tag_name = tag_name.replace('~', '-')
    element = etree.Element(tag_name)
    element.text = obj.cdata
    if obj._attributes:
        for k, v in obj._attributes.items():
            element.attrib[k] = v
    return element
