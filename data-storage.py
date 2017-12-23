import argparse
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import logging
import json
import atexit

topic_name = ''
kafka_broker = ''
cassandra_broker = ''
keyspace = ''
table = ''

logging.basicConfig()
logger = logging.getLogger('data-storage')
logger.setLevel(logging.DEBUG)

def shutdown_hook(consumer, session):
    logger.info('closing resource')
    consumer.close()
    session.shutdown()
    logger.info('release resource')

def save_data(stock_data, session):
    try:
        logger.debug('start to save data %s', stock_data)
        parsed = json.loads(stock_data)
        symbol  = parsed.get('symbol')
        price = float(parsed.get('price'))
        timestamp = parsed.get('last_trade_time')
        statement = "INSERT INTO %s (symbol, trade_time, price) VALUES ('%s', '%s', %f)" % (table, symbol,timestamp,price)
        session.execute(statement)
        logger.info('saved data into cassandra %s', stock_data)

    except Exception as e:
        logger.error('cannot save data %s', stock_data)

if __name__ == '__main__':
    #setup command line argument

    parser = argparse.ArgumentParser()
    parser.add_argument('topic_name', help = 'the kafka topic name to subscribe from')
    parser.add_argument('kafka_broker', help = 'the kafka broker address')
    parser.add_argument('cassandra_broker', help = 'the cassandra broker location')
    parser.add_argument('keyspace', help = 'the keyspace')
    parser.add_argument('table',help = 'the table in cassandra')

    # parse argument
    args = parser.parse_args()
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker
    cassandra_broker = args.cassandra_broker
    keyspace = args.keyspace
    table = args.table

    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers = kafka_broker
    )

    #create a cassandra session
    cassandra_cluster = Cluster(
        contact_points = cassandra_broker.split(',')
    )
    session = cassandra_cluster.connect()
    session.execute("CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {'class':'SimpleStrategy','replication_factor':'1'}"%keyspace)
    session.set_keyspace(keyspace)
    session.execute("CREATE TABLE IF NOT EXISTS %s (symbol text, trade_time timestamp, price float, PRIMARY KEY (symbol, trade_time) )" %table)

    atexit.register(shutdown_hook, consumer, session)
    for msg in consumer:
        save_data(msg.value, session)


