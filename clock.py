from apscheduler.schedulers.blocking import BlockingScheduler
import twitter_stream

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=5)
def timed_job():
    twitter_stream.tweet_crowler()


sched.start()
