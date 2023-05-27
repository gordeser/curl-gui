# cURL GUI application

## Description

The application main functions are **downloading and uploading files** to server. 
It also supports setting a **speed limit**\
\
In addition, the application allows you to configure a **proxy server**, select a **user-agent** 
from the list (or set your own)\
\
If you need, you also can input username and password for **HTTP Basic authentication** and input needed **cookies**\
\
In case of **an error**, the application **will show** it to the user with a brief description\
\
For advanced users, the application has **debug mode**, where you can also **enable verbose mode**, **clear curl logs** and **export curl logs** to file 

## Requirements

Install requirements using `pip install -r requirements.txt`

In case of errors, try `pip3 install -r requirements.txt`

## Start application

Start application using `python main.py`

In case of errors, try `python3 main.py`

## Run tests

Run tests from CLI using `python -m unittest tests/run_tests.py`


In case of errors, try `python -m unittest tests/run_tests.py` \
or try to install module unittest using `pip install unittest` or `pip3 install unittest` \

In case of `TclError` run tests again
