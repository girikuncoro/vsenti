import csv
import click
import MySQLdb as mysql

# Change class below to use different method
from vsenti_svm import VsentiSVM
vsenti = VsentiSVM()

@click.group()
def cli():
    pass

# Train Vsenti
@click.command('train')
@click.option('--input', 'input_file',
        default='', help='Path to training data file',
        type=click.Path(exists=True))
@click.option('--output', 'output_file',
        default='', help='Where the model written to',
        type=click.Path())
def train(input_file, output_file):
    """Train Vsenti"""
    vsenti.train(input_file, output_file)
cli.add_command(train)

# Eval Vsenti
@click.command('eval')
@click.option('--model', default='', help='Path to the model file',
        type=click.Path(exists=True))
@click.option('--test-data', default='', help='Path to test data',
        type=click.Path(exists=True))
def evaluate(model, test_data):
    vsenti.eval(model, test_data)
cli.add_command(evaluate)

# Map product name to their corresponding data
product_data = {
    'vSphere': {
        'alias': ['vsphere', 'vcenter'],
        'id': -1
    },
    'NSX': {
        'alias': ['nsxt', 'nsx'],
        'id': -1
    },
    'vSAN': {
        'alias': ['vsan'],
        'id': -1
    }
}

# Sentiment data
# Map sentiment name to id
sentiment_data_id = {
    'pos_vsphere': -1,
    'neg_vsphere': -1,
    'pos_nsx': -1,
    'neg_nsx': -1,
    'pos_vsan': -1,
    'neg_vsan': -1,
    'oot': -1
}

# Function to scale the score
# value score_raw:
# -1.x < score_raw < 1.x
# we want to convert it to 0 < x <= 1.0 scale
def scale_confident_score(score_raw):
    score = abs(score_raw)
    if score >= 1.0:
        return 1.0
    else:
        return score

# Run Rojak
@click.command('run')
@click.option('--model', default='', help='Path to the model file',
    type=click.Path(exists=True))
@click.option('--db-host', 'db_host', default='127.0.0.1',
    help='Database host')
@click.option('--db-port', 'db_port', default=3306,
    help='Database port number')
@click.option('--db-user', 'db_user', default='vsenti',
    help='Database user name')
@click.option('--db-pass', 'db_pass', default='123456',
    help='Database user password')
@click.option('--db-name', 'db_name', default='vsenti_database',
    help='Database name')
@click.option('--max-articles', default=100, help='Maximum articles analyzed')
@click.option('--exclude-media', 'exclude_media_names', default='',
    help='Exclude media, media name separated by comma')
@click.option('--only-media', 'only_media_names', default='',
    help='Run analyzer only for this media')
def run(model, db_host, db_port, db_user, db_pass, db_name, max_articles,
    exclude_media_names, only_media_names):
    """Run Vsenti to analyze data on the database"""
    # Load the model
    vsenti.load_model(model)

    # Open database connection
    db = mysql.connect(host=db_host, port=db_port, user=db_user,
        passwd=db_pass, db=db_name)
    # Set autocommit to false
    db.autocommit(False)
    # Create new db cursor
    select_cursor = db.cursor()

    # Get product ID
    sql_get_product_id = 'select id from product where name=%s;'
    for product_name in product_data:
        try:
            select_cursor.execute(sql_get_product_id, [product_name])
            res = select_cursor.fetchone()
            product_id = int(res[0])
            product_data[product_name]['id'] = product_id
        except mysql.Error as err:
            raise Exception(err)

    # Get sentiment ID
    sql_get_sentiment_id = 'select id from sentiment where name=%s;'
    for sentiment_name in sentiment_data_id:
        try:
            select_cursor.execute(sql_get_sentiment_id, [sentiment_name])
            res = select_cursor.fetchone()
            sentiment_id = int(res[0])
            sentiment_data_id[sentiment_name] = sentiment_id
        except mysql.Error as err:
            raise Exception(err)

    # Exclude media if any
    excluded_media = exclude_media_names.split(',')
    excluded_media_ids = []
    sql_get_media_id = 'select id from media where name=%s;'
    for media_name in excluded_media:
        if media_name == '': continue
        # Get the id
        try:
            select_cursor.execute(sql_get_media_id, [media_name])
            res = select_cursor.fetchone()
            media_id = res[0]
        except mysql.Error as err:
            raise Exception(err)
        # Concat the sql string
        excluded_media_ids.append('media_id!=' + str(media_id) + ' ')

    # Run only for the following media
    only_media = only_media_names.split(',')
    only_media_ids = []
    for media_name in only_media:
        if media_name == '': continue
        # Get the id
        try:
            select_cursor.execute(sql_get_media_id, [media_name])
            res = select_cursor.fetchone()
            media_id = res[0]
        except mysql.Error as err:
            raise Exception(err)
        # Concat the sql string
        only_media_ids.append('media_id=' + str(media_id) + ' ')

    # SQL query to get the article
    sql_get_article_template = '''
        select id, content, media_id
        from article
        where is_analyzed=false
        {}{}
    '''
    excluded_media_sql = ''
    if len(excluded_media_ids) > 0:
        excluded_media_sql = 'and '.join(excluded_media_ids)
        excluded_media_sql = 'and ({})'.format(excluded_media_sql)
    only_media_sql = ''
    if len(only_media_ids) > 0:
        only_media_sql = 'or '.join(only_media_ids)
        only_media_sql = 'and ({})'.format(only_media_sql)

    sql_get_article = sql_get_article_template.format(excluded_media_sql,
        only_media_sql)
    print '=== Start debug sql_get_article'
    print 'sql_get_article:', sql_get_article
    print '=== End debug sql_get_article'
    select_cursor.execute(sql_get_article)
    for i in xrange(max_articles):
        content = ''

        result = select_cursor.fetchone()
        print "From the DB: ", result
        if result:
            article_id = result[0]
            article_content = result[1]
            article_media_id = result[2]
        else:
            print 'Cannot fetch article, skipping ...'
            continue
        raw_text = article_content

        # Get mention information
        print '=== Start debug mention'
        clean_raw_text = vsenti.clean_string(raw_text)
        normalized_words = clean_raw_text.lower().split(' ')
        print 'raw_text:', raw_text
        print 'normalized_words:', normalized_words
        print '=== End debug mention'

        print '=== Start debug label'
        pred = vsenti.predict([raw_text])
        print 'label:', pred['label']
        print 'confident_score:', pred['confident_score']
        print '=== End debug label'

        # Insert to the database
        insert_cursor = db.cursor()
        sql_insert_sentiment = '''
            insert into article_sentiment(`article_id`, `sentiment_id`,
                `confident_score_raw`, `confident_score_scaled`)
            values (%s, %s, %s, %s);
        '''
        sql_update_is_analyzed = '''
            update article set is_analyzed=true where id=%s;
        '''
        try:
            # For sentiment data
            label = pred['label']
            print 'Label: ', label
            if not label:
                raise Exception('Cannot predict the labels')

            sentiment_id = sentiment_data_id[label]
            print 'Sentiment ID: ', sentiment_id
            if sentiment_id == -1:
                raise Exception('product_id data not updated')
            print 'Pred Conf Score: ', pred['confident_score']
            score = pred['confident_score']
            print 'Score: ', score
            score_scaled = scale_confident_score(score)
            print 'Score scaled: ', score_scaled
            insert_cursor.execute(sql_insert_sentiment, [article_id,
                sentiment_id, score, score_scaled])

            print 'Product id: ', product_id

            # Update is_analyzed status
            insert_cursor.execute(sql_update_is_analyzed, [article_id])
            db.commit()
            insert_cursor.close()
        except Exception as err:
            db.rollback()
            print 'Failed to analyze articles:', article_id
            print 'Error:', err
            continue
    select_cursor.close()
    db.close()

cli.add_command(run)

if __name__ == '__main__':
    cli()
