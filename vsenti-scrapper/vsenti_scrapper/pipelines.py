# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb as mysql
from scrapy.exceptions import CloseSpider, DropItem

class ArticleValidation(object):
    def process_item(self, item, spider):
        content = item.get('content', 'content_not_set')
        if content == 'content_not_set':
            err_msg = 'Missing content in: %s' % item.get('url')
            raise DropItem(err_msg)

        published_at = item.get('published_at', 'published_at_not_set')
        if published_at == 'published_at_not_set':
            err_msg = 'Missing published_at in: %s' % item.get('url')
            raise DropItem(err_msg)

        # Pass item to the next pipeline, if any
        return item

class SaveToMySQL(object):
    sql_insert_article = '''
        INSERT INTO `article`(`media_id`, `content`,
            `url`, `published_at`)
        VALUES (%s, %s, %s, %s);
    '''

    def process_item(self, item, spider):
        url = item.get('url')
        content = item.get('content')
        published_at = item.get('published_at')

        # Insert to the database
        try:
            spider.cursor.execute(self.sql_insert_article, [spider.media['id'],
                content, url, published_at])
            spider.db.commit()
        except mysql.Error as err:
            spider.db.rollback()
            if spider.is_slack:
                error_msg = '{}: Unable to save article: {}\n```\n{}\n```\n'.format(
                    spider.name, url, err)
                # spider.slack.chat.post_message('#vsenti-scrapper-errors', error_msg,
                #     as_user=True)

        return item
