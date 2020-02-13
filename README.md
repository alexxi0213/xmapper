# xmapper

## Motivation
If you need to map massive number of XML files from one format to another format like below:
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
xmapper will help to bulid a mapper config file

## What is xmapper
xmapper is a tool build upoon on `untangle` but add some feature that can parse the XML with path. See below example:
```xml


```