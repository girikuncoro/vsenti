import MySQLdb as mysql
import os
import csv
import sys

MEDIA_NAME = os.getenv('MEDIA_NAME', 'vmtnforum')
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

sql_get_media_id = '''
select id from media where name=%s;
'''
try:
    cursor.execute(sql_get_media_id, [MEDIA_NAME])
    result = cursor.fetchone()
    media_id = result[0]
except mysql.Error as err:
    print 'Unable to fetch media id', err
    sys.exit()

sql_get_article_count = '''
select count(*) from article where media_id=%s;
'''
try:
    cursor.execute(sql_get_article_count, [media_id])
    result = cursor.fetchone()
    article_count = result[0]
except mysql.Error as err:
    print 'Unable to fetch news count', err
    sys.exit()

sql_get_article = """
select url,content,published_at from article where media_id=%s;
"""

# Read CSV file
file_name = 'data_{}_{}.csv'.format(MEDIA_NAME, article_count)
output_file = open(file_name, 'w')
fields = ['url', 'content', 'published_at_utc']
csv_writer = csv.DictWriter(output_file, fields)
csv_writer.writeheader()

try:
    cursor.execute(sql_get_article, [media_id])
    for i in xrange(article_count):
        result = cursor.fetchone()
        url = result[0]
        content = result[1]
        published_at = result[2]
        csv_writer.writerow({'url': url, 'content':
            content, 'published_at_utc': published_at})
except mysql.Error as err:
    print 'Unable to fetch articles', err
    sys.exit()

output_file.close()
