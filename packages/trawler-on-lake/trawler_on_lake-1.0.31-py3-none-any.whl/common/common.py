import builtins

from pyspark.conf import SparkConf
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.avro.functions import *
from pyspark.sql.column import _to_java_column
from confluent_kafka.schema_registry import SchemaRegistryClient

from delta.tables import *


#########
# SPARK #
#########
def get_spark_session(spark_conf: list, app_name: str, log_level: str) -> SparkSession:
    spark_conf = SparkConf().setAll(spark_conf)

    spark_session = SparkSession.builder.appName(app_name).config(conf=spark_conf).getOrCreate()

    spark_session.sparkContext.setLogLevel(log_level)

    return spark_session


def get_spark_conf(name: str, conf: list) -> dict:
    return dict(list(builtins.filter(lambda source: source['name'] == name, conf))[0])


#########
# KAFKA #
#########
def get_kafka_certificate_password() -> str:
    with open("/mnt/secrets/cluster-ca-cert/ca.password") as f:
        return f.read()


def get_kafka_user_password() -> str:
    with open("/mnt/secrets/my-user/user.password") as f:
        return f.read()


def read_kafka_stream(spark_session: SparkSession, spark_job_conf: dict, source_name: str) -> DataFrame:
    source_conf = get_spark_conf(source_name, spark_job_conf['sources'])
    raw_stream = spark_session \
        .readStream \
        .format("kafka") \
        .options(**source_conf['kafka_options']) \
        .load()

    deserialized_stream = deserialize_register_avro_stream(raw_stream, source_conf['kafka_deserialization'])

    return deserialized_stream


def read_kafka(spark_session: SparkSession, source_conf: dict) -> DataFrame:
    raw_stream = spark_session \
        .read \
        .format("kafka") \
        .options(**source_conf['kafka_options']) \
        .load()

    deserialized_stream = deserialize_register_avro_stream(raw_stream, source_conf['kafka_deserialization'])

    return deserialized_stream


def write_kafka_stream(stream: DataFrame, spark_job_conf: dict, output_name):
    output_stream_conf = get_spark_conf(output_name, spark_job_conf['outputs'])

    stream = serialize_register_avro_stream(stream, output_stream_conf['kafka_serialization'])

    if output_stream_conf.get('processing_time') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("kafka") \
            .options(**output_stream_conf['kafka_options']) \
            .trigger(processingTime=output_stream_conf['processing_time']) \
            .outputMode(output_stream_conf['mode']) \
            .start()
    elif output_stream_conf.get('availableNow') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("kafka") \
            .options(**output_stream_conf['kafka_options']) \
            .trigger(availableNow=output_stream_conf['availableNow']) \
            .outputMode(output_stream_conf['mode']) \
            .start()
    elif output_stream_conf.get("once") is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .queryName(output_stream_conf['name']) \
            .format("kafka") \
            .options(**output_stream_conf['kafka_options']) \
            .trigger(once=output_stream_conf['once']) \
            .outputMode(output_stream_conf['mode']) \
            .start()
    else:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("kafka") \
            .options(**output_stream_conf['kafka_options']) \
            .outputMode(output_stream_conf['mode']) \
            .start()


def write_kafka(dataframe: DataFrame, spark_job_conf: dict, output_name: str):
    output_stream_conf = get_spark_conf(output_name, spark_job_conf['outputs'])

    df = serialize_register_avro_stream(dataframe, output_stream_conf['kafka_serialization'])

    df.write.format("kafka").options(**output_stream_conf['kafka_options']).save()


######
# S3 #
######
def read_s3_compress_log_stream(spark_session: SparkSession, spark_job_conf: dict, source_name: str) -> DataFrame:
    source_stream_conf = get_spark_conf(source_name, spark_job_conf['sources'])
    return spark_session \
        .readStream \
        .options(**source_stream_conf['s3_options']) \
        .schema(source_stream_conf['schema']) \
        .text(source_stream_conf['location'])


##############
# DELTA LAKE #
##############
def create_delta_tables_if_not_exists(conf, schema):
    DeltaTable \
        .createIfNotExists() \
        .addColumns(schema) \
        .partitionedBy(conf["delta_options"]["partition_columns"]) \
        .location(conf["delta_options"]["location"]) \
        .property("delta.enableChangeDataFeed", conf["delta_options"]["enableChangeDataFeed"]) \
        .execute()


def create_delta_tables_if_not_exists_no_partitioning(conf, schema):
    DeltaTable \
        .createIfNotExists() \
        .addColumns(schema) \
        .location(conf["delta_options"]["location"]) \
        .execute()


def read_delta(spark_session: SparkSession, spark_job_conf: dict, source_name: str) -> DataFrame:
    source_conf = get_spark_conf(source_name, spark_job_conf['sources'])
    return spark_session \
        .read \
        .format("delta") \
        .options(**source_conf['delta_options']) \
        .load(source_conf["location"])


def read_delta_stream(spark_session: SparkSession, spark_job_conf: dict, source_name: str) -> DataFrame:
    source_stream_conf = get_spark_conf(source_name, spark_job_conf['sources'])
    return spark_session \
        .readStream \
        .format("delta") \
        .options(**source_stream_conf['delta_options']) \
        .load(source_stream_conf["location"])


def write_delta(spark_job_conf: dict, output_name: str, df: DataFrame):
    output_conf = get_spark_conf(output_name, spark_job_conf['outputs'])
    create_delta_tables_if_not_exists(output_conf, output_conf['delta_options']['schema'])
    (
        df
        .write
        .format("delta")
        .mode(output_conf['mode'])
        .partitionBy(output_conf['delta_options']['partition_columns'])
        .option("checkpointLocation", output_conf['checkpoint_location'])
        .option("partitionOverwriteMode", output_conf['delta_options']['partition_overwrite_mode'])
        .option("mergeSchema", output_conf['delta_options']['merge_schema'])
        .option("overwriteSchema", output_conf['delta_options']['overwrite_schema'])
        .save(output_conf['delta_options']['location'])
    )


def write_delta_no_partitioning(spark_job_conf: dict, output_name: str, df: DataFrame):
    output_conf = get_spark_conf(output_name, spark_job_conf['outputs'])
    create_delta_tables_if_not_exists(output_conf, output_conf['delta_options']['schema'])
    (
        df
        .write
        .format("delta")
        .mode(output_conf['delta_options']['mode'])
        .option("checkpointLocation", output_conf['checkpoint_location'])
        .option("partitionOverwriteMode", output_conf['delta_options']['partition_overwrite_mode'])
        .option("mergeSchema", output_conf['delta_options']['merge_schema'])
        .option("overwriteSchema", output_conf['delta_options']['overwrite_schema'])
        .save(output_conf['delta_options']['location'])
    )


def write_delta_stream(spark_job_conf: dict, output_name: str, stream: DataFrame):
    output_stream_conf = get_spark_conf(output_name, spark_job_conf['outputs'])
    create_delta_tables_if_not_exists(output_stream_conf, output_stream_conf['delta_options']['schema'])

    if output_stream_conf.get('processing_time') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(processingTime=output_stream_conf['processing_time']) \
            .partitionBy(output_stream_conf['delta_options']['partition_columns']) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start(output_stream_conf['delta_options']['location'])
    elif output_stream_conf.get('availableNow') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(availableNow=output_stream_conf.get('availableNow')) \
            .partitionBy(output_stream_conf['delta_options']['partition_columns']) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start(output_stream_conf['delta_options']['location'])
    elif output_stream_conf.get('once') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(once=output_stream_conf.get('once')) \
            .partitionBy(output_stream_conf['delta_options']['partition_columns']) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start(output_stream_conf['delta_options']['location'])
    else:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .partitionBy(output_stream_conf['delta_options']['partition_columns']) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start(output_stream_conf['delta_options']['location'])


def write_delta_stream_no_partitioning(spark_job_conf: dict, output_name: str, stream: DataFrame):
    output_stream_conf = get_spark_conf(output_name, spark_job_conf['outputs'])
    create_delta_tables_if_not_exists_no_partitioning(output_stream_conf, output_stream_conf['delta_options']['schema'])

    if output_stream_conf.get('processing_time') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(processingTime=output_stream_conf['processing_time']) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start(output_stream_conf['delta_options']['location'])
    elif output_stream_conf.get('availableNow') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(availableNow=output_stream_conf.get('availableNow')) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start(output_stream_conf['delta_options']['location'])
    elif output_stream_conf.get('once') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(once=output_stream_conf.get('once')) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start(output_stream_conf['delta_options']['location'])
    else:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start(output_stream_conf['delta_options']['location'])


def write_delta_stream_with_custom_fnc(spark_job_conf, output_name: str, stream: DataFrame, updater_function):
    output_stream_conf = get_spark_conf(output_name, spark_job_conf['outputs'])
    create_delta_tables_if_not_exists_no_partitioning(output_stream_conf, output_stream_conf['delta_options']['schema'])

    if output_stream_conf.get('processing_time') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(processingTime=output_stream_conf['processing_time']) \
            .foreachBatch(updater_function) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start()
    elif output_stream_conf.get('availableNow') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(availableNow=output_stream_conf['availableNow']) \
            .foreachBatch(updater_function) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start()
    elif output_stream_conf.get('once') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(once=output_stream_conf['once']) \
            .foreachBatch(updater_function) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start()
    else:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .foreachBatch(updater_function) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start()


def write_delta_stream_with_custom_fnc_same_foreach_batch(spark_job_conf: dict, output_name: str, stream: DataFrame,
                                                          updater_function):
    output_stream_conf = get_spark_conf(output_name, spark_job_conf['outputs'])
    # for output in output_stream_conf['delta_options']:
    #     DeltaTable \
    #         .createIfNotExists() \
    #         .addColumns(output['schema']) \
    #         .partitionedBy(output["partition_columns"]) \
    #         .location(output["location"]) \
    #         .execute()

    if output_stream_conf.get('processing_time') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(processingTime=output_stream_conf['processing_time']) \
            .foreachBatch(updater_function) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start()
    elif output_stream_conf.get('availableNow') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(availableNow=output_stream_conf['availableNow']) \
            .foreachBatch(updater_function) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start()
    elif output_stream_conf.get('once') is not None:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .trigger(once=output_stream_conf['once']) \
            .foreachBatch(updater_function) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start()
    else:
        stream \
            .writeStream \
            .queryName(output_stream_conf['name']) \
            .format("delta") \
            .outputMode(output_stream_conf['mode']) \
            .foreachBatch(updater_function) \
            .option("checkpointLocation", output_stream_conf['checkpoint_location']) \
            .option("mergeSchema", output_stream_conf['delta_options']['merge_schema']) \
            .option("overwriteSchema", output_stream_conf['delta_options']['overwrite_schema']) \
            .start()


########
# AVRO #
########
def get_register_avro_schema(kafka_deserialization_conf: dict) -> str:
    kafka_schema_registry_conf = {
        'url': kafka_deserialization_conf['kafka_schema_registry_url']
    }

    kafka_schema_registry_subject = kafka_deserialization_conf['kafka_schema_registry_subject_name']

    json_format_schema = SchemaRegistryClient(kafka_schema_registry_conf) \
        .get_latest_version(kafka_schema_registry_subject) \
        .schema \
        .schema_str

    return json_format_schema


def deserialize_register_avro_stream(stream: DataFrame, kafka_deserialization_conf: dict) -> DataFrame:
    from_avro_abris_settings = from_avro_abris_config({
        'schema.registry.url': kafka_deserialization_conf['schema.registry.url']
    }, kafka_deserialization_conf['topic'], False)

    deserialized_stream = stream \
        .withColumn("parsed", from_avro("value", from_avro_abris_settings)) \
        .select('parsed.*')

    return deserialized_stream


def serialize_register_avro_stream(stream: DataFrame, kafka_serialization_conf: dict) -> DataFrame:
    to_avro_abris_settings = to_avro_abris_config({
        'schema.registry.url': kafka_serialization_conf['schema.registry.url']
    }, kafka_serialization_conf['topic'], False)

    serialized_stream = stream \
        .select(to_avro(struct(stream.columns), to_avro_abris_settings).alias("value"))

    return serialized_stream


def from_avro(col, config):
    """
    avro deserialize

    :param col (PySpark column / str): column name "key" or "value"
    :param config (za.co.absa.abris.config.FromAvroConfig): abris config, generated from abris_config helper function
    :return: PySpark Column
    """
    jvm_gateway = SparkContext._active_spark_context._gateway.jvm
    abris_avro = jvm_gateway.za.co.absa.abris.avro

    return Column(abris_avro.functions.from_avro(_to_java_column(col), config))


def from_avro_abris_config(config_map, topic, is_key):
    """
    Create from avro abris config with a schema url

    :param config_map (dict[str, str]): configuration map to pass to deserializer, ex: {'schema.registry.url': 'http://localhost:8081'}
    :param topic (str): kafka topic
    :param is_key (bool): boolean
    :return: za.co.absa.abris.config.FromAvroConfig
    """
    jvm_gateway = SparkContext._active_spark_context._gateway.jvm
    scala_map = jvm_gateway.PythonUtils.toScalaMap(config_map)

    return jvm_gateway.za.co.absa.abris.config \
        .AbrisConfig \
        .fromConfluentAvro() \
        .downloadReaderSchemaByLatestVersion() \
        .andTopicNameStrategy(topic, is_key) \
        .usingSchemaRegistry(scala_map)


def to_avro(col, config):
    """
    avro serialize
    :param col (PySpark column / str): column name "key" or "value"
    :param config (za.co.absa.abris.config.ToAvroConfig): abris config, generated from abris_config helper function
    :return: PySpark Column
    """
    jvm_gateway = SparkContext._active_spark_context._gateway.jvm
    abris_avro = jvm_gateway.za.co.absa.abris.avro

    return Column(abris_avro.functions.to_avro(_to_java_column(col), config))


def to_avro_abris_config(config_map, topic, is_key):
    """
    Create to avro abris config with a schema url

    :param config_map (dict[str, str]): configuration map to pass to the serializer, ex: {'schema.registry.url': 'http://localhost:8081'}
    :param topic (str): kafka topic
    :param is_key (bool): boolean
    :return: za.co.absa.abris.config.ToAvroConfig
    """
    jvm_gateway = SparkContext._active_spark_context._gateway.jvm
    scala_map = jvm_gateway.PythonUtils.toScalaMap(config_map)

    return jvm_gateway.za.co.absa.abris.config \
        .AbrisConfig \
        .toConfluentAvro() \
        .downloadSchemaByLatestVersion() \
        .andTopicNameStrategy(topic, is_key) \
        .usingSchemaRegistry(scala_map)


def instantiate_delta_table(spark_session: SparkSession, spark_job_conf: dict, table_name: str):
    table_conf = get_spark_conf(table_name, spark_job_conf['outputs'])
    create_delta_tables_if_not_exists(table_conf, table_conf['delta_options']['schema'])
    return DeltaTable.forPath(spark_session, table_conf['delta_options']['location'])


def instantiate_delta_tables(spark_session: SparkSession, spark_job_conf: dict, tables_name: str):
    tables_conf = get_spark_conf(tables_name, spark_job_conf['outputs'])

    results = dict()
    for table in tables_conf['delta_options']:
        DeltaTable \
            .createIfNotExists() \
            .addColumns(table['schema']) \
            .partitionedBy(table["partition_columns"]) \
            .location(table["location"]) \
            .execute()
        results[table['name']] = DeltaTable.forPath(spark_session, table['location'])

    return results
