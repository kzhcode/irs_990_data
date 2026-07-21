
# Base Image
FROM apache/airflow:2.9.3-python3.11

# Dependencies
COPY requirements.txt /requirements.txt

# Install
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

# Switching a user to root priv
USER root

# Creating a directory with root priv and changing dir ownership to airflow
RUN mkdir -p /opt/airflow/data && chown -R airflow /opt/airflow/data

# Changing a user priv back to airflow
USER airflow


