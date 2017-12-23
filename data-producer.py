# write data to any kafka cluster
# write data to any kafka topic
# scheduled fetch price from yahoo finance
# configurable stock symbol

# parse command line argument
import argparse
from kafka import KafkaProducer
import json
import logging
from yahoo_finance import Share
import schedule
import time
# use atexit to use register shutdown_hooker
import atexit
import random

logging.basicConfig()
logger = logging.getLogger('data-producer')
# debug, info, warn, error, fatal
logger.setLevel(logging.DEBUG)

symbol = ''
topic_name = ''
kafka_broker = ''

def shutdown_hock(producer):
    logger.info('closing kafka producer')
    producer.flush(10)
    producer.close(10)
    logger.info('kafka producer closed')

def fetch_price_and_send(producer, stock=None):
    logger.debug('about to fetch price')
    #stock.refresh()
    #price = stock.get_price()
    price = random.randrange(30,100)
    #trade_time = stock.get_trade_datetime()
    trade_time = 'Template Time'
    data = {
        'symbol' : symbol,
        'last_trade_time': trade_time,
        'price': price
    }
    data = json.dumps(data)
    logger.debug('retrieved stock stock price %s', data)
    # send data to producer
    try:
        producer.send(topic = topic_name, value = data)
        logger.debug('send data to kafka %s', data)
    except Exception as e:
        logger.warn('failed to send price to kafka')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol', help = 'the symbol of the stock')
    parser.add_argument('topic_name', help = 'the name of the topic')
    parser.add_argument('kafka_broker', help = 'the location of the kafka')

    args = parser.parse_args()
    symbol = args.symbol
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker

    producer = KafkaProducer(
        bootstrap_servers = kafka_broker
    )

    #stock = Share(symbol)
    # fetch stock every 1 sec, producer and stock are para.
    schedule.every(1).second.do(fetch_price_and_send, producer) #stock from Share(stock)

    # register shutdown_hook to release producer
    atexit.register(shutdown_hock, producer)

    while True:
        schedule.run_pending()
        time.sleep(1)