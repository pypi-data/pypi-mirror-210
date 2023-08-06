import os
from pprint import pprint, pformat
import time
from pygqlc import GraphQLClient
from .worker import ValiotWorker, QueueType, PollingMode, JobConfigMode, LogLevel, LogStyle
# ! Create main helpers:
gql = GraphQLClient()
vw = ValiotWorker()
# * Initialize helpers:
gql.addEnvironment(
    'dev',
    url=os.environ.get('API'),
    wss=os.environ.get('WSS'),
    headers={'Authorization': os.environ.get('TOKEN')},
    default=True)
vw.setClient(gql)
vw.setWorker(os.environ.get('WORKER'))
vw.setPollingMode(PollingMode.SUBSCRIPTION)
vw.setJobConfigMode(JobConfigMode.SYNC)
if not os.environ.get('ENV') == 'prod':
    vw.setLoggingStyle(LogStyle.PREFIX_ALL_LINES)


@vw.job(
    name='TEST_JOB',
    alias='test job 1',
    description='',
    schedule='* * * * *',
    enabled=True,
    queueType=QueueType.FREQUENCY,
)
def test_job(log, **_):
    log(LogLevel.INFO, "Hi, I'm test job #1")
    time.sleep(0.2)
    log(LogLevel.INFO, "Hi, I'm test job #1 again")
    return {'result': 'ok 1'}


@vw.job(
    name='TEST_JOB_SIMPLE_OUTPUT',
    alias='test job simple output',
    description='',
    enabled=True,
    queueType=QueueType.ON_DEMAND,
)
def test_job(log, **_):
    log(LogLevel.INFO, "Hi, I'm test job simple output")
    return 'ok simple output'


@vw.job(
    name='TEST_JOB_LOCK_REQUIRED',
    alias='test job with lock',
    description='test job which requires lock',
    enabled=True,
    lockRequired=True,
    queueType=QueueType.ON_DEMAND,
)
def test_job(log, **_):
    log(LogLevel.INFO, "Hi, I'm test job simple output, but I acquire the lock for some time")
    time.sleep(5)
    return 'ok simple output'


@vw.job(
    name='TEST_JOB_2',
    alias='test job 2',
    description='',
    schedule='*/3 * * * *',
    enabled=True,
    queueType=QueueType.FREQUENCY,
)
def test_job_2(log, **_):
    log(LogLevel.INFO, "Hi, I'm test job #2")
    return {'result': 'ok 2'}


@vw.job(
    name='TEST_JOB_THAT_FAILS',
    alias='test job that fails',
    description='',
    enabled=True,
    queueType=QueueType.ON_DEMAND,
)
def test_job_that_fails(log, **_):
    log(LogLevel.INFO, "Hi, I'm test job #3")
    raise Exception('This job fails')


@vw.job(
    name='TEST_JOB_THAT_FAILS_BAD_ARGS',
    alias='test job that fails due to bad arguments',
    description='',
    enabled=True,
    queueType=QueueType.ON_DEMAND,
)
def test_job_that_fails(log):  # ! missing **_ at the end
    log(LogLevel.INFO, "Hi, I'm test job #4")
    raise Exception('This job fails')


@vw.job(
    name='TEST_EVENT_JOB',
    alias='test event job',
    description='',
    enabled=True,
    queueType=QueueType.EVENT,
    query='''subscription {datumCreated {successful messages {field message} result { id value variable {id name} }}}''',
    lockRequired=True,
    eventConfig={'timeout': 8.0, 'max_batch': 10}
)
def test_event_job(log, data, **_):
    log(LogLevel.INFO, "Hi, I'm test job #5, here is the data:")
    log(LogLevel.INFO, pformat(data))

# @vw.job(
#     name='MISSING_JOB',
#     alias='missing job',
#     description='job that causes an error (missing job) when called (comment it out after registering)',
#     enabled=True,
#     queueType=QueueType.ON_DEMAND,
# )
# def missing_job(log, **_):
#     log(LogLevel.ERROR, "Hi, I should not be called, please comment me")
#     return 'ok simple output'


def main():
    print('main for valiot worker')
    vw.run(interval=5.0)


if __name__ == "__main__":
    main()
