from apscheduler.schedulers.blocking import BlockingScheduler
import twitter_stream
import rate_module

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=5)
def timed_job():
    twitter_stream.tweet_crowler()
    rate_module.ranking()


sched.start()
