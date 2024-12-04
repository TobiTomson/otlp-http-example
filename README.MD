# Trace Generator with OpenTelemetry Collector

## Overview

There are cases where in a distributed system not all parts of the system have an easy way to implement tracing. Usually one wants to use a zero-code tracing agent, or at least a tracing library/SDK, like the one of Datadog or OpenTelemetry.
In cases where this is not possible, a different solution is needed. This project demonstrates how to generate OpenTelemetry (OTel) traces from an arbitrary source when no automatic instrumentation and no SDK are available.
This project uses Python code to illustrate how one can use OTLP/HTTP to send traces from ANY source via a plain HTTP POST request. Be aware that for Python simpler options for tracing exist. Python is only used for its ubiquity and to show a running prototype that is easy to understand.

## Alternatives to consider before resorting to manually sending traces via OTLP

- [Datadog Single Step Instrumentation](https://docs.datadoghq.com/tracing/trace_collection/automatic_instrumentation/single-step-apm)
- [Datadog Tracing Libraries](https://docs.datadoghq.com/tracing/trace_collection/automatic_instrumentation/dd_libraries/)
- [Datadog Tracing via Agent API](https://docs.datadoghq.com/tracing/guide/send_traces_to_agent_by_api/)
- [OTel zero-code instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/zero-code/)
- [OTel Libraries](https://opentelemetry.io/docs/concepts/instrumentation/libraries/) 

## Project Structure

- `trace-generator.py`:  
  A Python script that generates two spans (a parent and a child span) and sends them to the OpenTelemetry Collector via OTLP/HTTP in JSON format.

- `docker-compose.yml`:  
  A Docker Compose configuration to run the OpenTelemetry Collector, which allows debugging trace collection and forwarding to Datadog. In a productive setup, consider [using the OTLP ingest of the Datadog Agent](https://docs.datadoghq.com/opentelemetry/interoperability/otlp_ingest_in_the_agent).

- `otel-config.yaml`:  
  Configuration file for the OpenTelemetry Collector to process incoming spans and export them.

## How to run

### Prerequisites

1. Python 3.9 or higher
2. Docker including Docker Compose

### Setup

1. Create and activate a virtual environment:
   - `python3 -m venv venv`
   - `source venv/bin/activate`

2. Install required Python packages:

    `pip install requests`

3. Start the OpenTelemetry Collector

    Ensure the docker-compose.yml and otel-config.yaml files are in the same directory.
    Start the Collector with Docker Compose:

    `docker compose up -d`

3. Run the Trace Generator

    `python trace-generator.py`

    The script will generate a trace with one parent span and one child span, and send the trace to the OpenTelemetry Collector using the OTLP/HTTP protocol.

### Verify Results

Check the logs of the OpenTelemetry Collector to verify traces are being processed:

`docker compose logs -f otel-collector`

Verify traces in [Datadog](https://app.datadoghq.eu/apm/traces)