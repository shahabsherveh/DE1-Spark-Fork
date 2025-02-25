#!/bin/bash

# Stop all Hadoop Services
$HADOOP_HOME/bin/hdfs --daemon stop datanode
$HADOOP_HOME/bin/yarn --daemon stop nodemanager

# Stop all Apache Spark Services
$SPARK_HOME/sbin/stop-worker.sh
