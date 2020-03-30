# -*- coding: utf-8 -*-
import unittest

from xmapper.utils import parse, dump_str


class TestCommon(unittest.TestCase):

    def test_basic(self):
        xml1 = """<?xml version='1.0' encoding='UTF-8'?>
                    <property>
                        <id>353324</id>
                        <type>house</type>
                        <propertyType>house</propertyType>
                        <salePriority>high</salePriority>
                        <image>https://img.599245196.jpg</image>
                    </property>
                """

        obj1 = parse(xml1, mode='r')
        paths = {
            'property.id',
            'property.type',
            'property.propertyType',
            'property.salePriority',
            'property.image'
        }
        self.assertEqual(obj1.paths, paths)

        value_mapping = {
            'property.image': 'https://img.599245196.jpg',
            'property.id': '353324',
            'property.propertyType': 'house',
            'property.type': 'house',
            'property.salePriority': 'high'
        }

        self.assertEqual(obj1.value_mapping, value_mapping)

    def test_complex(self):
        xml2 = """<?xml version="1.0" encoding="UTF-8"?>
                    <bookstore>
                        <book category="cooking">
                            <title lang="en">Everyday Italian</title>
                            <author>Giada De Laurentiis</author>
                            <year>2005</year>
                            <price>30.00</price>
                        </book>
                        <book category="children">
                            <title lang="en">Harry Potter</title>
                            <author>J K. Rowling</author>
                            <year>2005</year>
                            <price>29.99</price>
                        </book>
                        <book category="web">
                            <title lang="en">Learning XML</title>
                            <author>Erik T. Ray</author>
                            <year>2003</year>
                            <price>39.95</price>
                        </book>
                    </bookstore>"""

        obj2 = parse(xml2, mode='r')
        paths = {
            'bookstore.book.0.title',
             'bookstore.book.0.price',
             'bookstore.book.1.price',
             'bookstore.book.1.year',
             'bookstore.book.0.year',
             'bookstore.book.1.author',
             'bookstore.book.2.title',
             'bookstore.book.2.price',
             'bookstore.book.2.year',
             'bookstore.book.0.author',
             'bookstore.book.2.author',
             'bookstore.book.1.title'
        }
        self.assertEqual(obj2.paths, paths)

        self.assertEqual(
            obj2.get_value_by_path('bookstore.book.0.title'),
            'Everyday Italian'
        )
        self.assertEqual(
            obj2.get_value_by_path('bookstore.book.2.year'),
            '2003'
        )
        self.assertEqual(
            obj2.get_attr_by_path('bookstore.book.0.title'),
            {'lang': 'en'}
        )
        self.assertEqual(
            obj2.get_attr_by_path('bookstore.book.2'),
            {'category': 'web'}
        )

    def test_build_xml(self):
        xml3 = """<?xml version='1.0' encoding='UTF-8'?>
                    <property>
                        <id></id>
                        <type></type>
                        <propertyType></propertyType>
                        <salePriority></salePriority>
                        <image></image>
                    </property>
                """

        obj3 = parse(xml3, mode='rw')

        obj3.set_value_by_path('property.id', '353324')
        obj3.set_value_by_path('property.type', 'house')
        obj3.set_value_by_path('property.propertyType', 'house')
        obj3.set_value_by_path('property.salePriority', 'high')
        obj3.set_value_by_path('property.image', 'https://img.599245196.jpg')

        obj3 = parse(dump_str(obj3))
        paths = {
            'property.id',
            'property.type',
            'property.propertyType',
            'property.salePriority',
            'property.image'
        }
        self.assertEqual(obj3.paths, paths)

        value_mapping = {
            'property.image': 'https://img.599245196.jpg',
            'property.id': '353324',
            'property.propertyType': 'house',
            'property.type': 'house',
            'property.salePriority': 'high'
        }

        self.assertEqual(obj3.value_mapping, value_mapping)
