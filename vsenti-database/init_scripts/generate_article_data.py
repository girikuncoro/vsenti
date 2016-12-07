import MySQLdb as mysql
from faker import Factory
import random
import os
import sys

VSENTI_DB_HOST = os.getenv('VSENTI_DB_HOST', '127.0.0.1')
VSENTI_DB_PORT = int(os.getenv('VSENTI_DB_PORT', 3306))
VSENTI_DB_USER = os.getenv('VSENTI_DB_USER', 'vsenti')
VSENTI_DB_PASS = os.getenv('VSENTI_DB_PASS', '123456')
VSENTI_DB_NAME = os.getenv('VSENTI_DB_NAME', 'vsenti_database')

# Open database connection
db = mysql.connect(host=VSENTI_DB_HOST, port=VSENTI_DB_PORT,
        user=VSENTI_DB_USER, passwd=VSENTI_DB_PASS,
        db=VSENTI_DB_NAME)

# Create new db cursor
cursor = db.cursor()

# Get list of the media
medias = []
sql_get_medias = '''
select id,website_url from media;
'''
try:
    cursor.execute(sql_get_medias)
    results = cursor.fetchall()
    for row in results:
        media_id = row[0]
        media_url = row[1]
        medias.append({'id': media_id, 'url': media_url})
except mysql.Error as err:
    print 'Unable to fetch media data', err
    sys.exit()

# Get list of sentiment
sentiment_ids = []
sql_get_sentiment = '''
select id from sentiment;
'''
try:
    cursor.execute(sql_get_sentiment)
    results = cursor.fetchall()
    for row in results:
        sentiment_id = row[0]
        sentiment_ids.append(sentiment_id)
except mysql.Error as err:
    print 'Unable to fetch sentiment data', err
    sys.exit()

# Get list of product
product_ids = []
sql_get_product = '''
select id from product;
'''
try:
    cursor.execute(sql_get_product)
    results = cursor.fetchall()
    for row in results:
        product_id = row[0]
        product_ids.append(product_id)
except mysql.Error as err:
    print 'Unable to fetch product data', err
    sys.exit()

# Generate random data for the article
MAX_ARTICLES=100
sql_insert_article = '''
INSERT INTO `article`(`media_id`, `content`, `url`)
VALUES ('{}', '{}', '{}');
'''
sql_insert_sentiment = '''
INSERT INTO `article_sentiment`(`article_id`, `sentiment_id`,
    `confident_score_raw`, `confident_score_scaled`)
VALUES ('{}', '{}', '{}', '{}');
'''

fake = Factory.create()
total_sentiment = len(sentiment_ids)
total_product = len(product_ids)
for media in medias:
    media_id = media['id']
    media_url = media['url']
    for i in xrange(MAX_ARTICLES):
        content = fake.text()
        title = ' '.join(content.split()[:10]) + ' ' + str(media_id)
        content += ' ' + fake.text()
        content += ' ' + fake.text()
        title_url = title.lower().replace(' ', '-')
        url = '{}/{}'.format(media_url, title_url)

        n_label = random.randint(1, 3)
        sentiments = set([])
        for i in xrange(n_label):
            sentiment_i = random.randint(0, total_sentiment-1)
            sentiments.add(sentiment_ids[sentiment_i])

        # insert to the database
        try:
            # Parse the SQL command
            insert_sql = sql_insert_article.format(media_id, content, url)
            cursor.execute(insert_sql)
            article_id = cursor.lastrowid
            for sentiment_id in sentiments:
                score = random.uniform(0.5, 1.0)
                insert_sql = sql_insert_sentiment.format(article_id,
                        sentiment_id, score, score)
                cursor.execute(insert_sql)
            db.commit()
        except mysql.Error as err:
            print("Something went wrong: {}".format(err))
            db.rollback()

# Close the DB connection
db.close()
