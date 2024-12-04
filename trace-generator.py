import time
import requests
import uuid

def generate_trace():
    # Generate trace and span IDs
    trace_id = uuid.uuid4().hex
    parent_span_id = uuid.uuid4().hex[:16]
    child_span_id = uuid.uuid4().hex[:16]

    # Current time in nanoseconds
    start_time_ns = int(time.time() * 1e9)
    duration_ns = int(1e9)  # 1 second for parent span

    # Parent span
    parent_span = {
        "traceId": trace_id,
        "spanId": parent_span_id,
        # "parentSpanId": parent_span_id, # set this if you want to do context propagation
        "name": "parent-operation",
        "startTimeUnixNano": start_time_ns,
        "endTimeUnixNano": start_time_ns + duration_ns,  # 1 second duration
        "kind": "SPAN_KIND_INTERNAL",
        "attributes": [
            {"key": "service.name", "value": {"stringValue": "example-service"}},
            {"key": "service.version", "value": {"stringValue": "1.0.0"}},
            {"key": "env", "value": {"stringValue": "staging"}},
            {"key": "example", "value": {"stringValue": "parent"}},
        ],
        "status": {
            "code": "STATUS_CODE_OK",  # Indicating successful operation
            "message": "Parent span completed successfully."
        },
    }

    # Child span
    child_span = {
        "traceId": trace_id,
        "spanId": child_span_id,
        "parentSpanId": parent_span_id,
        "name": "child-operation",
        "startTimeUnixNano": start_time_ns + int(0.2e9),  # Start 0.2s after parent
        "endTimeUnixNano": start_time_ns + int(0.8e9),    # End 0.8s after parent starts
        "kind": "SPAN_KIND_INTERNAL",
        "attributes": [
            {"key": "service.name", "value": {"stringValue": "example-service"}},
            {"key": "service.version", "value": {"stringValue": "1.0.0"}},
            {"key": "env", "value": {"stringValue": "staging"}},
            {"key": "example", "value": {"stringValue": "child"}},
        ],
        "status": {
            "code": "STATUS_CODE_OK",  # Indicating successful operation
            "message": "Child span completed successfully."
        },
    }

    # Prepare OTLP JSON payload
    payload = {
        "resourceSpans": [
            {
                # unified service tagging (https://docs.datadoghq.com/getting_started/tagging/unified_service_tagging/)
                "resource": {"attributes": [
                    {"key": "service.name", "value": {"stringValue": "example-service"}},
                    {"key": "service.version", "value": {"stringValue": "1.0.0"}},
                    {"key": "env", "value": {"stringValue": "staging"}}
                ]},
                "scopeSpans": [
                    {
                        "spans": [parent_span, child_span]
                    }
                ],
            }
        ]
    }

    # Send the trace to the OTLP receiver
    headers = {"Content-Type": "application/json"}
    otlp_endpoint = "http://localhost:4318/v1/traces"  # Default OTLP receiver port
    response = requests.post(otlp_endpoint, json=payload, headers=headers)

    print(f"Response: {response.status_code}, {response.text}")


if __name__ == "__main__":
    generate_trace()
