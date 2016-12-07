import MySQLdb as mysql
import os
import json
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

data_file = open('data_media.json')
data_media = json.load(data_file)
sql_insert_media = '''
INSERT INTO `media`(`name`, `website_url`, `logo_url`)
VALUES (%s, %s, %s);
'''

for media in data_media['media']:
    media_name = media['name']
    media_website_url = media['website_url']
    media_logo_url = media['logo_url']
    if media_logo_url == '':
        media_logo_url = None

    # insert to the database
    try:
        cursor.execute(sql_insert_media, (media_name, media_website_url,
            media_logo_url))
        db.commit()
    except mysql.Error as err:
        print("Something went wrong: {}".format(err))
        db.rollback()

# Close the DB connection
db.close()

# Close the file stream
data_file.close()
