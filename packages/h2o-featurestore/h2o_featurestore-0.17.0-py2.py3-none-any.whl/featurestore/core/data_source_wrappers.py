import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
import ai.h2o.featurestore.api.v1.FeatureSetSearch_pb2 as pb_search
from ai.h2o.featurestore.api.v1.FeatureSetSearch_pb2 import BooleanFilter, NumericalFilter, TextualFilter

from .commons.spark_utils import SparkUtils


class DeltaTableFilter:
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value
        self._filter = self.__build()

    def __build(self):
        if isinstance(self.value, str):
            return pb_search.Filter(text=TextualFilter(field=self.column, operator=self.operator, value=[self.value]))
        elif isinstance(self.value, (int, float)):
            return pb_search.Filter(
                numeric=NumericalFilter(field=self.column, operator=self.operator, value=self.value)
            )
        elif isinstance(self.value, bool):
            return pb_search.Filter(boolean=BooleanFilter(field=self.column, operator=self.operator, value=self.value))


class SparkDataFrame:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self._write_path = None

    def _write_to_storage(self, stub):
        from pyspark.sql import SparkSession  # Local import

        spark = SparkSession.builder.getOrCreate()

        session_id = spark.conf.get("ai.h2o.featurestore.sessionId", "")
        request = pb.IngestWriteCredentialRequest()
        request.session_id = session_id
        write_info = stub.GetIngestWriteCredentials(request)

        SparkUtils.configure_user_spark(spark)
        spark.conf.set("ai.h2o.featurestore.sessionId", write_info.session_id)
        for k, v in write_info.options.items():
            spark.conf.set(k, v)
            if k.startswith("spark.hadoop."):
                spark.sparkContext._jsc.hadoopConfiguration().set(k.replace("spark.hadoop.", ""), v)
        spark.conf.set("spark.sql.session.timeZone", "UTC")
        self.dataframe.write.parquet(write_info.path)
        self._write_path = write_info.path

    def _get_storage_location(self):
        if not self._write_path:
            raise Exception("Write the spark frame into the storage before calling get method")
        parquet = pb.TempParquetFileSpec()
        parquet.path = self._write_path
        raw_data_location = pb.RawDataLocation()
        raw_data_location.temp_parquet.CopyFrom(parquet)
        return raw_data_location


class CSVFile:
    def __init__(self, path, delimiter=","):
        self.path = path
        self.delimiter = delimiter


class JSONFile:
    def __init__(self, path, multiline=False):
        self.path = path
        self.multiline = multiline


class ParquetFile:
    def __init__(self, path):
        self.path = path


class Proxy:
    def __init__(self, host="", port=0, user="", password=""):
        if port and not host:
            raise ValueError("Proxy port specified but host is missing!")
        if not port and host:
            raise ValueError("Proxy host specified but port is missing!")
        if port and host:
            if user and not password:
                raise ValueError("Proxy user specified but password is missing!")
            if not user and password:
                raise ValueError("Proxy password specified but user is missing!")
        self.host = host
        self.port = port
        self.user = user
        self.password = password


class SnowflakeTable:
    def __init__(
        self,
        url,
        warehouse,
        database,
        schema,
        table="",
        query="",
        insecure=False,
        proxy=None,
        role="",
        account="",
    ):
        if not (query or table):
            raise ValueError("table or query is required!")
        if query and table:
            raise ValueError("Only one of table or query is supported!")

        self.table = table
        self.database = database
        self.url = url
        self.query = query
        self.warehouse = warehouse
        self.schema = schema
        self.insecure = insecure
        self.proxy = proxy
        self.role = role
        self.account = account


class JdbcTable:
    def __init__(
        self,
        connection_url,
        table="",
        query="",
        partition_options=None,
    ):
        if not (table or query):
            raise ValueError("Table or query is required!")
        if table and query:
            raise ValueError("Only one of table or query is supported!")
        self.table = table
        self.query = query
        self.connection_url = connection_url
        self.partition_options = partition_options


class PartitionOptions:
    def __init__(
        self,
        num_partitions=None,
        partition_column=None,
        lower_bound=None,
        upper_bound=None,
        fetch_size=1000,
    ):
        self.num_partitions = num_partitions
        self.partition_column = partition_column
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.fetch_size = fetch_size


class SnowflakeCursor:
    def __init__(
        self,
        url,
        warehouse,
        database,
        schema,
        cursor,
        insecure=False,
        proxy=None,
        role="",
        account="",
    ):
        self.cursor = cursor
        self.database = database
        self.url = url
        self.warehouse = warehouse
        self.schema = schema
        self.insecure = insecure
        self.proxy = proxy
        self.role = role
        self.account = account

    def get_latest_query(self):
        query = (
            "SELECT QUERY_TEXT::VARCHAR "
            "FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_SESSION(RESULT_LIMIT => 10)) "
            "WHERE QUERY_ID=%s"
        )
        self.cursor.execute(query, (self.cursor.sfqid,))  # get the last executed query using the query id
        try:
            latest_query = self.cursor.fetchone()[0]
            if not latest_query.lower().startswith("select "):
                raise ValueError("Only select queries are supported for registering featuring sets")
        except IndexError:
            raise ValueError("No query seems to have been executed in this session")
        return latest_query


class DeltaTable:
    def __init__(self, path, version=-1, timestamp=None, filter=None):
        self.path = path
        self.version = version
        self.timestamp = timestamp
        self.filter = filter
        if version and timestamp:
            raise ValueError("Only one of version or timestamp is supported")


class CSVFolder:
    def __init__(self, root_folder, delimiter=",", filter_pattern=""):
        self.root_folder = root_folder
        self.filter_pattern = filter_pattern
        self.delimiter = delimiter


class ParquetFolder:
    def __init__(self, root_folder, filter_pattern=""):
        self.root_folder = root_folder
        self.filter_pattern = filter_pattern


class JSONFolder:
    def __init__(self, root_folder, multiline=False, filter_pattern=""):
        self.root_folder = root_folder
        self.multiline = multiline
        self.filter_pattern = filter_pattern


class MongoDbCollection:
    def __init__(self, connection_uri="mongodb://localhost:27017/", database="", collection=""):
        if not database:
            raise ValueError("Database name is required!")
        if not collection:
            raise ValueError("Collection name is required!")
        self.connection_uri = connection_uri
        self.database = database
        self.collection = collection


def get_raw_data_location(source):
    raw_data_location = pb.RawDataLocation()
    if isinstance(source, CSVFile):
        csv = pb.CSVFileSpec()
        csv.path = source.path
        csv.delimiter = source.delimiter
        raw_data_location.csv.CopyFrom(csv)
    elif isinstance(source, JSONFile):
        json = pb.JSONFileSpec()
        json.path = source.path
        json.multiline = source.multiline
        raw_data_location.json.CopyFrom(json)
    elif isinstance(source, ParquetFile):
        parquet = pb.ParquetFileSpec()
        parquet.path = source.path
        raw_data_location.parquet.CopyFrom(parquet)
    elif isinstance(source, SnowflakeTable):
        snowflake = pb.SnowflakeTableSpec()
        snowflake.table = source.table
        snowflake.database = source.database
        snowflake.url = source.url
        snowflake.warehouse = source.warehouse
        snowflake.schema = source.schema
        snowflake.query = source.query
        snowflake.insecure = source.insecure
        snowflake.role = source.role
        snowflake.account = source.account
        if source.proxy:
            snowflake.proxy.host = source.proxy.host
            snowflake.proxy.port = source.proxy.port
            snowflake.proxy.user = source.proxy.user
            snowflake.proxy.password = source.proxy.password
        raw_data_location.snowflake.CopyFrom(snowflake)
    elif isinstance(source, SnowflakeCursor):
        snowflake = pb.SnowflakeTableSpec()
        snowflake.table = ""
        snowflake.database = source.database
        snowflake.url = source.url
        snowflake.warehouse = source.warehouse
        snowflake.schema = source.schema
        snowflake.query = source.get_latest_query()
        snowflake.insecure = source.insecure
        snowflake.role = source.role
        if source.proxy:
            snowflake.proxy.host = source.proxy.host
            snowflake.proxy.port = source.proxy.port
            snowflake.proxy.user = source.proxy.user
            snowflake.proxy.password = source.proxy.password
        raw_data_location.snowflake.CopyFrom(snowflake)
    elif isinstance(source, JdbcTable):
        jdbc = pb.JDBCTableSpec()
        jdbc.table = source.table
        jdbc.connection_url = source.connection_url
        jdbc.query = source.query
        if source.partition_options is not None:
            jdbc.num_partitions = source.partition_options.num_partitions
            jdbc.partition_column = source.partition_options.partition_column
            jdbc.lower_bound = source.partition_options.lower_bound
            jdbc.upper_bound = source.partition_options.upper_bound
            jdbc.fetch_size = source.partition_options.fetch_size
        raw_data_location.jdbc.CopyFrom(jdbc)
    elif isinstance(source, DeltaTable):
        delta_table = pb.DeltaTableSpec()
        delta_table.path = source.path
        delta_table.version = source.version
        if source.timestamp:
            delta_table.timestamp = source.timestamp
        if source.filter:
            delta_table.filter.CopyFrom(source.filter._filter)
        raw_data_location.delta_table.CopyFrom(delta_table)
    elif isinstance(source, CSVFolder):
        csv_folder = pb.CSVFolderSpec()
        csv_folder.root_folder = source.root_folder
        csv_folder.filter_pattern = source.filter_pattern
        csv_folder.delimiter = source.delimiter
        raw_data_location.csv_folder.CopyFrom(csv_folder)
    elif isinstance(source, ParquetFolder):
        parquet_folder = pb.ParquetFolderSpec()
        parquet_folder.root_folder = source.root_folder
        parquet_folder.filter_pattern = source.filter_pattern
        raw_data_location.parquet_folder.CopyFrom(parquet_folder)
    elif isinstance(source, JSONFolder):
        json_folder = pb.JSONFolderSpec()
        json_folder.root_folder = source.root_folder
        json_folder.filter_pattern = source.filter_pattern
        json_folder.multiline = source.multiline
        raw_data_location.json_folder.CopyFrom(json_folder)
    elif isinstance(source, MongoDbCollection):
        mongo = pb.MongoDbCollectionSpec()
        mongo.connection_uri = source.connection_uri
        mongo.database = source.database
        mongo.collection = source.collection
        raw_data_location.mongo_db.CopyFrom(mongo)
    else:
        raise Exception("Unsupported external data source.")

    return raw_data_location


def get_source(raw_data_location):
    if raw_data_location.HasField("csv"):
        csv = raw_data_location.csv
        return CSVFile(path=csv.path, delimiter=csv.delimiter)
    elif raw_data_location.HasField("json"):
        json = raw_data_location.json
        return JSONFile(path=json.path, multiline=json.multiline)
    elif raw_data_location.HasField("parquet"):
        parquet = raw_data_location.parquet
        return ParquetFile(path=parquet.path)
    elif raw_data_location.HasField("snowflake"):
        snowflake = raw_data_location.snowflake
        proxy = (
            Proxy(
                host=snowflake.proxy.host,
                port=snowflake.proxy.port,
                user=snowflake.proxy.user,
                password=snowflake.proxy.password,
            )
            if snowflake.HasField("proxy")
            else None
        )

        return SnowflakeTable(
            table=snowflake.table,
            database=snowflake.database,
            url=snowflake.url,
            warehouse=snowflake.warehouse,
            schema=snowflake.schema,
            query=snowflake.query,
            insecure=snowflake.insecure,
            role=snowflake.role,
            account=snowflake.account,
            proxy=proxy,
        )
    elif raw_data_location.HasField("jdbc"):
        jdbc = raw_data_location.jdbc
        partition_options = PartitionOptions(
            num_partitions=jdbc.num_partitions,
            partition_column=jdbc.partition_column,
            lower_bound=jdbc.lower_bound,
            upper_bound=jdbc.upper_bound,
            fetch_size=jdbc.fetch_size,
        )
        return JdbcTable(
            connection_url=jdbc.connection_url, table=jdbc.table, query=jdbc.query, partition_options=partition_options
        )
    elif raw_data_location.HasField("delta_table"):
        delta_table = raw_data_location.delta_table
        filter = delta_table.filter if (delta_table.HasField("filter")) else None
        return DeltaTable(
            path=delta_table.path, version=delta_table.version, timestamp=delta_table.timestamp, filter=filter
        )
    elif raw_data_location.HasField("csv_folder"):
        csv_folder = raw_data_location.csv_folder
        return CSVFolder(
            root_folder=csv_folder.root_folder, filter_pattern=csv_folder.filter_pattern, delimiter=csv_folder.delimiter
        )
    elif raw_data_location.HasField("parquet_folder"):
        parquet_folder = raw_data_location.parquet_folder
        return ParquetFolder(root_folder=parquet_folder.root_folder, filter_pattern=parquet_folder.filter_pattern)
    elif raw_data_location.HasField("json_folder"):
        json_folder = raw_data_location.json_folder
        return JSONFolder(
            root_folder=json_folder.root_folder,
            filter_pattern=json_folder.filter_pattern,
            multiline=json_folder.multiline,
        )
    elif raw_data_location.HasField("mongo_db"):
        mongo_db = raw_data_location.mongo_db
        return MongoDbCollection(
            connection_uri=mongo_db.connection_uri, database=mongo_db.database, collection=mongo_db.collection
        )
    else:
        raise Exception("Unsupported external data source.")
