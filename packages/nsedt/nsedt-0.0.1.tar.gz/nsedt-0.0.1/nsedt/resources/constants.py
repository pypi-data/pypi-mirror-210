window_size = 180
max_workers = 5
log_format = """{
    "time": "%(asctime)s",
    "lineno": "%(lineno)d",
    "name": "[%(name)s]",
    "levelname": "%(levelname)s",
    "process": "%(process)s",
    "filename": "%(filename)s",
    "funcName": "%(funcName)s",
    "logmessage": "%(message)s",
}"""

base_url = "https://www.nseindia.com/"
equity_price_histroy = "api/historical/securityArchives?"
equity_corpinfo = "api/corporates-corporateActions?"
