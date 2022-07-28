# Debugging module for Wptagent
Traces purpose is for debugging. It gives an idea of code flow and timings associated with each message.
Trace is a separate entity from the global logging.
Traces output is defaulted to Wptagent/logging/main.log
Both Logging entities will have very colorful logging output, and both show more debugging details like(threadName, ms_elapsed_start, ms_elapsed_last, ..etc).


### New
  - addLoggingLevel('TRACE', logging.DEBUG - 5)
  - logging.getLogger(__name__).setLevel("TRACE")
  - logging.getLogger(__name__).trace('that worked')
  - logging.trace('Trace message')
  - logging.TRACE

### Logging Format for logging.DEBUG 
asctime.msecs | threadName | ms_elapsed_start | ms_elapsed_last_log_time | levelname | message | filename) | funcName) | lineno

### Logging Format for logging.INFO and greater
asctime.msecs | levelname | message


### Usage/Examples of Trace

```python
from internal.debug import trace

# enable global console and disable file output
setup()

# Example setting logger level for global console
# Logger(True,False,_logger_cmd=LoggerBase(logging.INFO)) 

# Log some global messages
logging.debug("Debug message")
logging.info("Info message")
logging.warning("Warning message")
logging.trace("Trace message")

```

### Running Tests

To run tests, run the following command.

```bash
  python3 -m internal.debug.trace
```
### Running With Wptagent

To run with trace enabled in wptagent, run the following command.

```bash
  python3 wptagent.py -vvvvv -etc..
```