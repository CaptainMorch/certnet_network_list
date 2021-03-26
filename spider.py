import re
import pathlib
import collections

import scrapy


PATTERN = re.compile(r'参考数据：([\d.]*)-([\d.]*) (\S*) ([^<]*)')
UNIVERSITY_KEY_WORDS = ['学院', '大学']
OUTPUT = pathlib.Path('output.csv')
FIELDS = ('network', 'ip_start', 'ip_end', 'region', 'university')
Column = collections.namedtuple('Column', FIELDS)

class CERNETSpider(scrapy.Spider):
    name = 'cert_spider'
    custom_settings = {
        'FEEDS': {
            OUTPUT: {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': FIELDS,
            },
        },
    }
    start_urls = ['http://ip.bczs.net/china/CERNET_IP']

    def parse(self, response):
        for column in response.xpath('//tbody/tr'):
            fields = column.xpath('td')

            href = fields[0].xpath('a').attrib['href']
            url = response.urljoin(href)

            network = fields[-1].xpath('text()').get()
            yield scrapy.Request(
                url, callback=self.parse_content,
                cb_kwargs={'network': network})

    def parse_content(self, response, network):
        content = response.css('.well').xpath('p').get()
        match = re.search(PATTERN, content)

        column = Column(network, *match.groups())
        if any([k in column.university for k in UNIVERSITY_KEY_WORDS]):
            yield column._asdict()
        else:
            yield None
