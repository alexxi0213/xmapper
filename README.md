# xmapper

## Motivation:
If you need to convert massive number of XML files from one format to another format like below:

### from:
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
### to:
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
xmapper will come in handy, it can parse the input and output XML files and bulid a mapper rule yaml config file like below:
```yaml

```
Once you get the map rule file you can reuse that or build something advanced rules (use xmapper's API) to do future massive converting.

## How can xmapper help:
xmapper is a tool build upoon on `untangle` (which can make your XML act like python object) add some feature that can parse and convert XML to key value pairs. See below example:
```xml


```