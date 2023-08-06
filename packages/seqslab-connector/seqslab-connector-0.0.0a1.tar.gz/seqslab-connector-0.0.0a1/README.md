# seqslab-connector

The SeqsLab Connector for Python based on [pyhive](https://github.com/dropbox/PyHive) allows you to create 
a Python DB API connection to Atgenomix SeqsLab interactive jobs (clusters) and develop Python-based workflow applications. 
It is a Hive-Thrift-based client with no dependencies on ODBC or JDBC. 
It also provides a [SQLAlchemy](https://www.sqlalchemy.org/) dialect and an [Apache Superset](https://superset.apache.org/)
database engine spec for use with tools to execute DQL.

You are welcome to file an issue for general use cases. You can also contact Atgenomix Support [here](https://console.seqslab.net).


### Requirements
Python 3.7 or above is required.


### Installation

Install using pip.

`pip install seqslab-connector` 

For Apache Superset integration install with

`pip install seqslab-connector[superset]`


### Usage

#### DB-API

```python
from seqslab import hive

cursor = hive.connect(database='run_name', http_path='job_run_id', username='user', password='pass', host='job_cluster_host')
cursor.execute('SHOW TABLES')
print(cursor.fetchall())
cursor.execute('SELECT * FROM my_workflow_table_name LIMIT 10')
print(cursor.fetchall())
cursor.close()
```

#### SQLAlchemy

```python
from sqlalchemy.engine import create_engine

engine = create_engine('seqslab+hive://user:pass@job_cluster_host/run_name?http_path=job_run_id')
```

#### Apache Superset

[Connecting to Databases](https://superset.apache.org/docs/databases/db-connection-ui)

#### Documentation
For the latest documentation, see [SeqsLab](https://docs.atgenomix.com).
