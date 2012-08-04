# import time
import json
import redis
import zmq
from datetime import datetime


def console_stats():

    try:
        context = zmq.Context()
        sub = context.socket(zmq.SUB)
        sub.bind('ipc:///tmp/collective.firehose.sock')
        sub.setsockopt(zmq.SUBSCRIBE, '')
        while True:
            print "Receiving"
            print sub.recv()

    except (KeyboardInterrupt, SystemExit):
        pass

def record_stats():

    try:
        context = zmq.Context()
        sub = context.socket(zmq.SUB)
        sub.bind('ipc:///tmp/collective.firehose.sock')
        sub.setsockopt(zmq.SUBSCRIBE, '')

        r = redis.StrictRedis(host='localhost', port=6379, db=0)

        while True:

            msg = sub.recv()
            msg = json.loads(msg)

            pipe = r.pipeline()
            if msg['msg_type'] == "hit":
                try:
                    section = msg['path'][0]
                except IndexError:
                    section = None

                pipe.incr('hits|%s' % msg['date'])
                pipe.hincrby('users_visits|%s' % msg['date'], msg['userid'], 1)
                if section:
                    pipe.hincrby('visited_sections|%s' % msg['date'], section, 1)

            if msg['msg_type'] == "visit_time":
                pipe.rpush('visit_time|%s' % msg['date'], msg['visited_time'])

            #full_date = datetime.strptime("%s %s"%(date,time), "%Y-%m-%d %H:%M:%S.%f")

            pipe.execute()

    except (KeyboardInterrupt, SystemExit):
        pass
    except:
        raise
    finally:
        sub.close()

# What data do I want to fetch?
# 1. What URL is each client serving right now -- set of client:URL
# 2. What are the most popular URLs? -- sorted set of URL scored by weight
# 3. What are the most popular URLs within the past hour? -- sorted set of URLs scored by weight for each hour + cron job that updates a union of the past N buckets
# 4. What are the slowest URLs? -- sorted set of URLs scored by request time
