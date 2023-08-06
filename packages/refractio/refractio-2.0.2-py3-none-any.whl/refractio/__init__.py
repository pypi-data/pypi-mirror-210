from .refractio import get_dataframe, get_local_dataframe
from .snowflake import Snowflake
from .mysql import Mysql
from .hive import Hive
from .sftp import Sftp
from .amazons3 import AmazonS3
from .azure import Azure

snowflake = Snowflake()
mysql = Mysql()
hive = Hive()
sftp = Sftp()
s3 = AmazonS3()
azure = Azure()
