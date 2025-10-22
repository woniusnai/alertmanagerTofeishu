curl -X POST http://10.102.11.17:30900/webhook \
  -H "Content-Type: application/json" \
  -d '{
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "TestAlert",
        "environment": "lab",
        "severity": "warning",
        "instance": "test-node"
      },
      "annotations": {
        "summary": "测试告警",
        "description": "这是一条手动测试消息"
      },
      "startsAt": "2025-08-21T10:00:00Z"
    }
  ]
}'
