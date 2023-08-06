# Generic ETL

Setup logging:

```
from etl.utils.log import LogCommit

# Create a temporary log file path
log_file = tmpdir_factory.mktemp("logs").join("test_log.txt")

# Create an instance of the InjectingLogger with file streaming
logger = LogCommit("Log_Commit", log_file)
logger.setLevel(logging.DEBUG)

# Log a message
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Commit
# secrets is same as runtime
# database_type same as key in secrets
inserts = logger.log_commit(secrets: dict, database_type: str)

```