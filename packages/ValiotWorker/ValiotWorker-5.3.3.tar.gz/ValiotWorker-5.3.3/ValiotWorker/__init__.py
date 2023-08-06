from .__version__ import __version__
from .worker import ValiotWorker
from .worker import QueueType, JobStatus, PollingMode, JobConfigMode, QueryOrderBy, LogLevel, LogStyle
from .uploaders import update_job

# * Package name:
name = 'ValiotWorker'
# * required here for pypi upload exceptions:
