# -*- coding: utf-8 -*-
import re
import scrapy
from test_task.items import MacbookItem

def parse_price(price_str):
    """
    Prices are split into three parts:
    -before the nonbreaking space
    -between the nonbreaking space and decimal mark
    -after the decimal mark
    :param price_str: price string to be parsed
    :return: numeric price value
    """
    m = re.findall('\d+', price_str)
    return int(m[0])*1000+int(m[1])+int(m[2])*0.01

def parse_name(item_link):
    """
    Extracts the item's name from its url.
    Item names in links start after https://www.ebay.com/itm/
    (first 25 characters), and end with /,
    so we can just take that part of the link
    as the item's name, replacing hyphens with spaces.
    This also avoids character issues, since links always use English.
    :param item_link: link leading to the item's page
    :return: item name string
    """
    return item_link[25:item_link.find('/', 25)].replace('-', ' ')

def sort_append(item_list, new_item):
    """
    Adds new items to a list, keeping the list sorted.
    :param item_list: list of items
    :param new_item: item to be inserted
    """
    i=len(item_list)
    o = 0
    while (o < i) and (item_list[o]['price'] < new_item['price']):
        o += 1
    item_list.insert(o, new_item)
    return item_list


class EbayMacbooksSpider(scrapy.Spider):
    name = 'ebay_macbooks'
    allowed_domains = ['www.ebay.com']
    start_urls = ['https://www.ebay.com/sch/i.html?_nkw=macbook+pro+13/']

    def parse(self, response):
        item_list = []
        for data in response.xpath("//ul[@class='srp-results srp-list clearfix']/li/div"):
            item = MacbookItem()
            item['price'] = parse_price(data.xpath(".//span[@class='s-item__price']/text()").get())
            item['link'] = data.xpath(".//a[@class='s-item__link']/@href").get()
            item['file_urls'] = [data.xpath(".//img[@class='s-item__image-img']/@src").get()]
            sort_append(item_list, item)
        result_number = 3
        for item in item_list[:result_number]:
            yield scrapy.Request(url=item['link'],
                                 callback=self.save_pages)
            yield item
        # data_list = response.xpath("//span[@class='s-item__price']/text()").getall()
        # price_list = [parse_price(s) for s in data_list]

    def save_pages(self, response):
        filename = 'tmp/' + parse_name(response.url) + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
