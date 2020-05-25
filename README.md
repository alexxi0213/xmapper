# xmapper

## Installation:
```bash
pip install xmapper
```

## Motivation:
If you want to compare massive number of different XML files, maybe the content is same
 but the item order is different like:
 
 XML_1:
```xml
<?xml version='1.0' encoding='UTF-8'?>
<listing>
    <ad>
        <type>house</type>
        <listingId>353324</listingId>
        <priority>high</priority>
        <url>https://img.599245196.jpg</url>
    </ad>
</listing>
```

 XML_2:
```xml
<?xml version='1.0' encoding='UTF-8'?>
<listing>
    <ad>
        <url>https://img.599245196.jpg</url>
        <priority>high</priority>
        <listingId>353324</listingId>
        <type>house</type>
    </ad>
</listing>
```

If you need to convert massive number of XML files from one format to another format like below example:

### From:
```xml
<?xml version='1.0' encoding='UTF-8'?>
<listing>
    <ad>
        <type>house</type>
        <listingId>353324</listingId>
        <priority>high</priority>
        <url>https://img.599245196.jpg</url>
    </ad>
</listing>
```
### To:
```xml
<?xml version='1.0' encoding='UTF-8'?>
<property>
    <id>353324</id>
    <type>house</type>
    <propertyType>house</propertyType>
    <salePriority>high</salePriority>
    <image>https://img.599245196.jpg</image>
</property>
```
xmapper will come in handy, it will convert your XML to a key/value pairs
 structure like:
 ```python
{'listing.ad.priority': 'high',
 'listing.ad.listingId': '353324',
 'listing.ad.type': 'house',
 'listing.ad.url': 'https://img.599245196.jpg'}
```

xmapper can also parse the input and output XML files and bulid a customizable
 mapper rule yaml config file like below:
```yaml
property.id: listing.ad.listingId
property.image: listing.ad.url
property.propertyType: listing.ad.type
property.salePriority: listing.ad.priority
property.type: listing.ad.type
```
Once you get the map rule file you can reuse that or build something advanced rules (use xmapper's API) to do future massive converting.

## How can xmapper help:
xmapper is a tool build upoon on `untangle` (which can make your XML act like python object) add some feature that can parse and convert XML to key value pairs. See below example:
```python

In [31]: from xmapper import parse

In [32]: xml1 = """<?xml version='1.0' encoding='UTF-8'?>
    ...: <listing>
    ...:     <ad>
    ...:         <type>house</type>
    ...:         <listingId>353324</listingId>
    ...:         <priority>high</priority>
    ...:         <url>https://img.599245196.jpg</url>
    ...:     </ad>
    ...: </listing>"""

In [33]: obj = parse(xml1)
In [34]: obj.paths
Out[34]:
{'listing.ad.listingId',
 'listing.ad.priority',
 'listing.ad.type',
 'listing.ad.url'}

In [35]: obj.get_value_by_path('listing.ad.listingId')
Out[35]: '353324'
```
Now you have the mapping rules and the xml objects you can use `get_value_by_path` and `set_value_by_path` to perform the transformation.

Once the done set the values, you can convert the xml object back to XML file like:
```python
In [42]: from xmapper.utils import dump_xml

In [43]: dump_xml(obj, '/tmp/test.xml')

In [44]: cat /tmp/test.xml
<?xml version='1.0' encoding='UTF-8'?>
<property>
  <id>353324</id>
  <type>house</type>
  <propertyType>house</propertyType>
  <salePriority>high</salePriority>
  <image>https://img.599245196.jpg</image>
</property>
```
