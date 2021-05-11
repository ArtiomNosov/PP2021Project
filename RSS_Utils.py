
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml
import xml.etree.ElementTree as ET
import feedparser
import re


def RSS_feeds():
    opml_root = ET.parse("..\Parser\companies.opml.xml").getroot()
    rss_url = ""
    num = 0
    for tag in opml_root.findall('.//outline'):
        num += 1
        rss_url += f"{num}. {tag.items()[2][1]} \n"
    return rss_url