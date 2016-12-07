# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider

from vsenti_scrapper.items import Article
from vsenti_scrapper.spiders.base import BaseSpider

class VmtnforumSpider(BaseSpider):
    name = "vmtnforum"
    allowed_domains = ["communities.vmware.com"]
    start_urls = (
        'https://communities.vmware.com/community/vmtn/vsphere/content?filterID=contentstatus[published]~objecttype~objecttype[thread]',
    )

    def parse(self, response):
        self.logger.info('parse: {}'.format(response))
        is_no_update = False

        # Get list of threads from the current page
        articles = response.css('tr.js-browse-item')
        if not articles:
            raise CloseSpider('article not found')
        for article in articles:
            # Close the spider if we don't find the list of urls
            url_selectors = article.css('td.j-td-title > div > a::attr(href)')
            if not url_selectors:
                raise CloseSpider('url_selectors not found')
            url = 'http://communities.vmware.com' + url_selectors.extract()[0]
            self.logger.info('Url: {}'.format(url))

            # Example: December 6, 2016 3:03:53 PM
            info_selectors = article.css('td.j-td-date > a::text')
            if not info_selectors:
                info_selectors = article.css('td.j-td-date::text')
            if not info_selectors:
                raise CloseSpider('info_selectors not found')

            info_time = info_selectors.extract()[0]
            if 'Last Activity' in info_time:
                info_time = info_time[len('Last Activity: '):]
            self.logger.info('info_time: {}'.format(info_time))

            # Parse date information
            try:
                published_at = datetime.strptime(info_time, '%B %d, %Y %H:%M:%S %p')
            except ValueError as e:
                raise CloseSpider('cannot_parse_date: {}'.format(e))

            if self.media['last_scraped_at'] >= published_at:
                is_no_update = True
                break
            # For each url we create new scrapy request
            yield Request(url, callback=self.parse_article)

        if is_no_update:
            self.logger.info('Media have no update')
            return

        # Collect news on next page
        # if response.css('div.bu.fr > a'):
        #     next_page = response.css('div.bu.fr > a[rel="next"]::attr(href)').extract()[0]
        #     next_page_url = response.urljoin(next_page)
        #     yield Request(next_page_url, callback=self.parse)

    # Collect article item
    def parse_article(self, response):
        pass
