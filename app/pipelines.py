# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import redis
import pymongo
import pymysql
from scrapy.exceptions import DropItem
import dj_database_url


class AppPipeline(object):
    def open_spider(self, spider):
        self.file = open('apps.jl', mode='w', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item


class MongoPipeline(object):

    collection_name = 'app_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item


class AppRedisPipeline(object):

    def __init__(self, redis_host, redis_port):
        self.redis_host = redis_host
        self.redis_port = redis_port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_host=crawler.settings.get('REDIS_HOST'),
            redis_port=crawler.settings.get('REDIS_PORT', 6379)
        )

    def open_spider(self, spider):
        self.pool = redis.ConnectionPool(
            host=self.redis_host, port=self.redis_port)
        self.db = redis.Redis(connection_pool=self.pool)

    def close_spider(self, spider):
        self.pool.disconnect()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False)
        self.db.set(item['apk_name'], line)
        return item


class DuplicatesPipeline(object):

    def __init__(self):
        self.item_ids = set()

    def process_item(self, item, spider):
        if item['apk_name'] in self.item_ids:
            raise DropItem('apk: {} already exists!'.format(item['apk_name']))
        else:
            self.item_ids.add(item['apk_name'])
        return item

# CREATE TABLE apps(
#   app_name VARCHAR(100) COMMENT 'APP名称',
#   app_class VARCHAR(30) COMMENT '分类',
#   apk_name VARCHAR(100) NOT NULL PRIMARY KEY COMMENT '包名',
#   update_time DATETIME DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP
# )


class AppMySQLPipeline(object):

    # def __new__(cls, **kwargs):
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = super(cls, AppMySQLPipeline).__new__(**kwargs)
    #     return cls._instance

    def __init__(self, host, port, user, password, db=None, charset='utf8'):
        self.mysql_config = dict()
        self.mysql_config['host'] = host
        self.mysql_config['port'] = port
        self.mysql_config['user'] = user
        self.mysql_config['password'] = password
        self.mysql_config['db'] = db
        self.mysql_config['charset'] = 'utf8' if charset == 'utf-8' else charset

    @classmethod
    def from_crawler(cls, crawler=None):
        if not crawler:
            return cls(
                **cls.parse_mysql_url('mysql://root:138128@localhost:3306/scrapy?charset=utf-8')
            )

        return cls(
            **cls.parse_mysql_url(crawler.settings.get('MYSQL_URL')),
        )

    @staticmethod
    def parse_mysql_url(mysql_url):
        """
        Parses mysql url and prepares arguments for
        adbapi.ConnectionPool()
        """

        params = dj_database_url.parse(mysql_url)

        conn_kwargs = {}
        conn_kwargs['host'] = params['HOST']
        conn_kwargs['user'] = params['USER']
        conn_kwargs['password'] = params['PASSWORD']
        conn_kwargs['db'] = params['NAME']
        conn_kwargs['port'] = params['PORT']

        if 'OPTIONS' in params.keys():
            conn_kwargs.update(params['OPTIONS'])

        # Remove items with empty values
        conn_kwargs = dict((k, v) for k, v in conn_kwargs.items() if v)
        return conn_kwargs

    def open_spider(self, spider):
        # self.pool = mysql.ConnectionPool(
        #     host=self.mysql_host, port=self.mysql_port)
        self.db = pymysql.connect(**self.mysql_config)
        self.db.autocommit(1)
        self.cur = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        sql = """
            replace into scrapy.apps(app_name, app_class, apk_name)
            values('{app_name}', '{app_class}', '{apk_name}')
        """
        self.cur.execute(sql.format(**dict(item)))
        return item


if __name__ == '__main__':
    a = AppMySQLPipeline.from_crawler()
    a. open_spider(None)
    import traceback
    sql = """
            insert into apps(app_name, app_class, apk_name)
            values('{app_name}', '{app_class}', '{apk_name}')
        """
    item = {
        'app_name': 'test_app_name',
        'app_class': 'instant communication',
        'apk_name': 'com.test.test'}
    print(sql.format(**item))
    try:
        a.cur.execute(sql.format(**item))
        # a.db.commit()
    except Exception as e:
        print(e)
        print('=' * 80)
        print(traceback.format_exc())
