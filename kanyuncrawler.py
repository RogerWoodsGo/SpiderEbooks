# -*- coding: utf-8 -*-
import urllib
import scrapy
from scrapy.selector import Selector
from scrapy import Request
from scrapy.contrib.loader import ItemLoader
import urlparse


class BookDetails(scrapy.Item):
    book_id = scrapy.Field()
    book_type = scrapy.Field()
    book_path = scrapy.Field()

class KanyuncrawlerSpider(scrapy.Spider):
    name = "kanyuncrawler"
    base_url = "http://www.kancloud.cn"
    allowed_domains = ["www.kancloud.cn", "down.kancloud.cn"]
    start_urls = (
        'http://www.kancloud.cn/@kancloud',
    )

    def parse(self, response):
        resp = Selector(response)
        resp_url = response.url
        url_content = urlparse.urlparse(resp_url)
        scheme = url_content.scheme
        net_location = url_content.netloc
        link_list = resp.xpath("/html/body/*//dt/a/@href").extract()
        for link in link_list:
            book_url = scheme + "://" + net_location + link;
            yield Request(book_url, self.parse_book_url)
            #break
            #print book_url

    def parse_book_url(self, response):
        book_item = BookDetails(book_id = "", book_type = "pdf")
        bil = ItemLoader(item=book_item, response=response)
        bil.add_xpath("book_id", "/*//script/text()", re = r'bookId\s*:\s*(.*),.*')
        bil.add_xpath("book_path", "/*//script/text()", re = r'getDownloadUrl\s*:\s*\"(.*)\".*')
        #bil.get_xpath()
        bil.load_item()
        download_url = self.base_url + book_item['book_path'][0]
        post_data = "book_id=" + book_item['book_id'][0] + "&" + "type=" + book_item['book_type']
        #post_data = "book_id=" + "2759" + "&" + "type=" + book_item['book_type']

        #set header
        post_header = {}
        post_header["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        post_header["User-Agent"] = "Mozilla/5.0"
        #print post_header
        #print curl_cmd

        yield Request(download_url, self.get_book_link, headers = post_header, method='POST', body=post_data)

    def get_book_link(self, response):
        #pass
        body_dict = eval(response.body)
        if "url" in body_dict.keys():
            file_url = body_dict["url"]
            fu_handled = "".join(file_url.split("\\"))

            url_content = urlparse.urlparse(fu_handled)
            scheme = url_content.scheme
            net_location = url_content.netloc
            print scheme, net_location
            yield Request(fu_handled, self.download_book)


    def download_book(self, response):
        url_content = urlparse.urlparse(response.url)
        url_query = url_content.query
        attr_file = url_query.split("&")[0].split("=")
        file_name = urllib.unquote(attr_file[1])
        print file_name, type(file_name)
        file_path = "e_books/" + file_name
        with open(file_path, "wb") as wf:
            wf.write(response.body)


        #print attr_query
