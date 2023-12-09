# Find process running python script and kill it

```
kill $(ps -ef | grep 'scriptName.py' | grep -v grep | awk '{print $2}')
```

# Run script with `nohup` and redirect the output to log

```
nohup python scriptName.py > output.log 2>&1 &
```

# Add logging

```
import logging

# Initialize logger
logging.basicConfig(filename='log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Loger usage
logging.debug("This is a debug message")
logging.info("This is an info message")
logging.warning("This is a warning message")
logging.error("This is an error message")
logging.critical("This is a critical message")
```
