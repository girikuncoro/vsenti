import MySQLdb as mysql
import os
import json
import sys

VSENTI_DB_HOST = os.getenv('VSENTI_DB_HOST', '127.0.0.1')
VSENTI_DB_PORT = int(os.getenv('VSENTI_DB_PORT', 3306))
VSENTI_DB_USER = os.getenv('VSENTI_DB_USER', 'vsenti')
VSENTI_DB_PASS = os.getenv('VSENTI_DB_PASS', '123456')
VSENTI_DB_NAME = os.getenv('VSENTI_DB_NAME', 'vsenti_database')

sql_insert_product = '''
INSERT INTO `product`(`name`, `website_url`, `logo_url`, `description`)
VALUES (%s, %s, %s, %s);
'''
sql_insert_sentiment = '''
INSERT INTO `sentiment`(`name`, `product_id`)
VALUES (%s, %s);
'''

# Insert data from file_name to the database db
def insert_data(db, file_name):
    # Read the data
    product_data = json.load(open(file_name))
    if not 'products' in product_data:
        raise ValueError('key products not exists')

    # Create database cursor
    cursor = db.cursor()

    for product in product_data['products']:
        product_name = product['name']
        product_website_url = product['website_url']
        if product_website_url == '':
            product_website_url = None
        product_logo_url = product['logo_url']
        if product_logo_url == '':
            product_logo_url = None
        product_description = product['description']

        product_id = -1
        try:
            cursor.execute(sql_insert_product, [
                product_name,
                product_website_url,
                product_logo_url,
                product_description])
            product_id = cursor.lastrowid
            db.commit()
        except mysql.Error as err:
            print("Something went wrong: {}".format(err))
            db.rollback()
            sys.exit()

        # Insert sentiment
        sentiments = product['sentiments']
        for sentiment_name in sentiments:
            try:
                cursor.execute(sql_insert_sentiment, [sentiment_name,
                    product_id])
                db.commit()
            except mysql.Error as err:
                print("Something went wrong: {}".format(err))
                db.rollback()

    # Insert oot sentiment
    try:
        cursor.execute(sql_insert_sentiment, ['oot',
            None])
        db.commit()
    except mysql.Error as err:
        print("Something went wrong: {}".format(err))
        db.rollback()

if __name__ == '__main__':
    # Open database connection
    db = mysql.connect(host=VSENTI_DB_HOST, port=VSENTI_DB_PORT,
            user=VSENTI_DB_USER, passwd=VSENTI_DB_PASS,
            db=VSENTI_DB_NAME)

    # Create new db cursor
    insert_data(db, 'data_vmware_product.json')

    # Close the DB connection
    db.close()
