# xmapper

xmapper helps you inspect, compare, and transform XML feeds without hand-writing XSLT or ad-hoc scripts. It normalises XML into stable dot-path/value mappings, lets you bootstrap YAML mapping rules from sample documents, and provides helpers to read, modify, and regenerate XML.

## Highlights

- Flatten XML into predictable dot-paths such as `listing.ad.listingId`.
- Read, update, and diff XML payloads programmatically.
- Auto-generate YAML mapping templates from example source/target documents.
- Rebuild well-formatted XML strings or files after applying your mappings.
- Works on small one-off transformations or large batch pipelines.

## Installation

```bash
pip install xmapper
```

Editable install for development:

```bash
pip install -e .
```

The library supports Python 3.8 through 3.12. Runtime dependencies: `lxml>=4.9,<5`, `PyYAML>=6.0`, and `untangle==1.2.1`.

## Quick start

```python
from xmapper import parse
from xmapper.utils import dump_str

source_xml = """<?xml version='1.0' encoding='UTF-8'?>
<listing>
  <ad>
    <type>house</type>
    <listingId>353324</listingId>
    <priority>high</priority>
    <url>https://img.599245196.jpg</url>
  </ad>
</listing>
"""

obj = parse(source_xml)

print(sorted(obj.paths))
# ['listing.ad.listingId', 'listing.ad.priority', 'listing.ad.type', 'listing.ad.url']

print(obj.get_value_by_path('listing.ad.priority'))
# 'high'

obj.set_value_by_path('listing.ad.priority', 'low')
print(dump_str(obj))
```

Output:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<listing>
  <ad>
    <type>house</type>
    <listingId>353324</listingId>
    <priority>low</priority>
    <url>https://img.599245196.jpg</url>
  </ad>
</listing>
```

## Generate mapping rules

Use the `Mapper` to discover how fields line up between two XML structures. This example uses raw XML strings, but file paths work as well.

```python
from xmapper import Mapper

source_xml = """<?xml version='1.0' encoding='UTF-8'?>
<listing>
  <ad>
    <type>house</type>
    <listingId>353324</listingId>
    <priority>high</priority>
    <url>https://img.599245196.jpg</url>
  </ad>
</listing>
"""

target_xml = """<?xml version='1.0' encoding='UTF-8'?>
<property>
  <id>353324</id>
  <type>house</type>
  <propertyType>house</propertyType>
  <salePriority>high</salePriority>
  <image>https://img.599245196.jpg</image>
</property>
"""

mapper = Mapper(source_xml, target_xml)
mapper.build_mapping()

print(mapper.MAPPER['exact_match'])
# {'property.id': 'listing.ad.listingId',
#  'property.image': 'listing.ad.url',
#  'property.propertyType': 'listing.ad.type',
#  'property.salePriority': 'listing.ad.priority',
#  'property.type': 'listing.ad.type'}
```

`Mapper.build_mapping()` prints three buckets:

- `exact_match` – fields with a single match in the source.
- `multiple_match` – fields with more than one possible source path.
- `human_intervention` – fields that need manual mapping.

Persist the suggestion to YAML for later review:

```python
mapper.dump_yaml_config('mapping.yaml')
```

## Compare two XML feeds

When you want to verify that two payloads carry the same data (regardless of element order), use `Comparer`.

```python
from xmapper import Comparer

comparer = Comparer('feed_a.xml', 'feed_b.xml')

if comparer.compare():
    print('Feeds match')
else:
    print('Differences found')
```

The comparer walks every path/value pair and prints any mismatches, so you can focus on the problematic fields instead of raw diffs.

## Typical use cases

- Onboard a new partner feed by generating mapping templates from sample XML.
- Build regression checks to ensure your exports still conform to downstream schemas.
- Transform legacy XML dumps into a normalised structure before loading into databases.
- Audit vendor feeds for missing or misplaced values.

## Testing

```bash
python -m unittest discover tests
```

## License

MIT

