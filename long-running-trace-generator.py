import time
import uuid
import requests

def send_span_to_collector(span, otlp_endpoint, headers):
    """Send a single span to the OTLP collector."""
    payload = {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "example-service"}},
                        {"key": "service.version", "value": {"stringValue": "1.0.0"}},
                        {"key": "env", "value": {"stringValue": "staging"}},
                    ]
                },
                "scopeSpans": [
                    {
                        "spans": [span],
                    }
                ],
            }
        ]
    }
    response = requests.post(otlp_endpoint, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Failed to send span: {response.status_code}, {response.text}")
    else:
        print(f"Span sent successfully: {span['name']} (Version: {span.get('attributes', [])[-1]['value'].get('intValue', 'N/A')})")

def generate_long_running_trace():
    # Configuration
    otlp_endpoint = "http://localhost:4318/v1/traces"
    headers = {"Content-Type": "application/json"}
    trace_duration_seconds = 30 * 60  # 30 minutes
    update_interval_seconds = 60  # 1 minute
    child_start_delay_ms = 200 # Child span starts 200 milliseconds after parent
    # Generate IDs for the trace and spans
    trace_id = uuid.uuid4().hex
    parent_span_id = uuid.uuid4().hex[:16]
    child_span_id = uuid.uuid4().hex[:16]

    # Start timestamp (in nanoseconds)
    start_time_ns = int(time.time() * 1e9)
    end_time_ns = start_time_ns + int(trace_duration_seconds * 1e9)
    child_start_time_ns = start_time_ns + int(child_start_delay_ms * 1e6)

    # Simulate parent span updates
    parent_partial_version = 0
    child_partial_version = 0
    current_time_ns = start_time_ns

    while current_time_ns < end_time_ns:
        current_time_ns = int(time.time() * 1e9)

        # Update parent span
        parent_partial_version += 1
        parent_span = {
            "traceId": trace_id,
            "spanId": parent_span_id,
            "name": "parent-operation",
            "startTimeUnixNano": start_time_ns,
            "kind": "SPAN_KIND_SERVER",
            "attributes": [
                {"key": "service.name", "value": {"stringValue": "example-service"}},
                {"key": "service.version", "value": {"stringValue": "1.0.0"}},
                {"key": "env", "value": {"stringValue": "staging"}},
            ],
        }
        if current_time_ns < end_time_ns:
            parent_span["attributes"].append(
                {"key": "_dd.partial_version", "value": {"intValue": parent_partial_version}}
            )
        else:
            parent_span["attributes"].append(
                {"key": "_dd.was_long_running", "value": {"intValue": 1}}
            )
            parent_span["endTimeUnixNano"] = end_time_ns
            parent_span["status"] = {"code": "STATUS_CODE_OK"}

        parent_span["endTimeUnixNano"] = current_time_ns
        send_span_to_collector(parent_span, otlp_endpoint, headers)

        # Update child span
        if current_time_ns >= child_start_time_ns:
            child_partial_version += 1
            child_span = {
                "traceId": trace_id,
                "spanId": child_span_id,
                "parentSpanId": parent_span_id,
                "name": "child-span",
                "startTimeUnixNano": child_start_time_ns,
                "kind": "SPAN_KIND_INTERNAL",
                "attributes": [
                    {"key": "service.name", "value": {"stringValue": "example-service"}},
                    {"key": "service.version", "value": {"stringValue": "1.0.0"}},
                    {"key": "env", "value": {"stringValue": "staging"}},
                ],
            }
            if current_time_ns < end_time_ns:
                child_span["attributes"].append(
                    {"key": "_dd.partial_version", "value": {"intValue": child_partial_version}}
                )
            else:
                child_span["attributes"].append(
                    {"key": "_dd.was_long_running", "value": {"intValue": 1}}
                )
                child_span["endTimeUnixNano"] = end_time_ns
                child_span["status"] = {"code": "STATUS_CODE_OK"}

            child_span["endTimeUnixNano"] = current_time_ns
            send_span_to_collector(child_span, otlp_endpoint, headers)

        # Sleep for the update interval
        time.sleep(update_interval_seconds)

if __name__ == "__main__":
    generate_long_running_trace()
