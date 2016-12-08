# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider

from vsenti_scrapper.items import Article
from vsenti_scrapper.spiders.base import BaseSpider

# number of thread list to crawl
MAX_PAGES=10

class VmtnforumSpider(BaseSpider):
    name = "vmtnforum"
    allowed_domains = ["communities.vmware.com"]
    start_urls = (
        'https://communities.vmware.com/community/vmtn/vsphere/content?filterID=contentstatus[published]~objecttype~objecttype[thread]',
    )
    start_page = 0
    pagination = 30

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

        # Collect threads on next page
        if self.start_page < self.pagination * MAX_PAGES:
            self.start_page += self.pagination
            next_page_url = self.start_urls[0] + '&start={}'.format(self.start_page)
            yield Request(next_page_url, callback=self.parse)

    # Collect article item
    def parse_article(self, response):
        self.logger.info('parse_article: {}'.format(response))
        # post_selectors = response.css('')
        reply_selectors = response.css('li.reply')

        # TODO: parse the thread starter
        for i, reply in enumerate(reply_selectors):
            # parse the discussion comments
            yield Request(response.url, meta={'reply': reply}, callback=self.parse_comment, dont_filter=True)

    # Collect article item
    def parse_comment(self, response):
        reply = response.meta['reply']

        # Init item loader
        # extract article published_at, content, url
        # Required: content, published_at
        loader = ItemLoader(item=Article(), response=response)
        loader.add_value('url', response.url)

        content_selectors = reply.css('div.jive-rendered-content > p::text')
        if not content_selectors:
            # Will be dropped on the item pipeline
            return loader.load_item()
        content = content_selectors.extract()
        content = ' '.join([w.strip() for w in content])
        content = content.strip()
        content = content.encode('ascii',errors='ignore')
        loader.add_value('content', content)
        self.logger.info('content: {}'.format(content))

        # Example: Dec 7, 2016 12:11 AM
        info_selectors = response.css('span.j-post-author::text')
        if not info_selectors:
            # Will be dropped on the item pipeline
            return loader.load_item()
        info = info_selectors.extract()[1]

        # Parse date information
        # Example: Dec 7, 2016 12:11 AM
        date_str = info.strip()
        if not date_str:
            # Will be dropped on the item pipeline
            return loader.load_item()

        # Example: Dec 7, 2016 12:11 AM
        try:
            published_at = datetime.strptime(date_str, '%b %d, %Y %H:%M %p')
        except ValueError:
            # Will be dropped on the item pipeline
            return loader.load_item()

        loader.add_value('published_at', published_at)

        # Move scraped news to pipeline
        return loader.load_item()
