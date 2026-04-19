# CloudGuard AI - API Documentation

## Cloud Layer API (Port 8000)

### Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "service": "Cloud Layer with ML",
  "model_loaded": true
}
```

### Analyze Finding
```
POST /analyze

Body:
{
  "finding_id": "uuid",
  "resource_type": "s3",
  "finding_type": "public_s3_bucket",
  "is_public": 1,
  "is_encrypted": 0,
  "port_exposed": 0,
  "description": "S3 bucket is public",
  "resource_id": "my-bucket"
}

Response:
{
  "finding_id": "uuid",
  "severity": "critical",
  "risk_score": 95.0,
  "estimated_cost": 500000,
  "recommendation": {
    "title": "Block S3 Public Access",
    "steps": [...]
  },
  "confidence": 0.95
}
```

### Get Findings
```
GET /findings?severity=critical

Response:
{
  "count": 5,
  "findings": [...]
}
```

---

## Fog Layer API (Port 8001)

### Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "service": "Fog Layer",
  "cache": "DynamoDB"
}
```

### Enrich Finding
```
POST /enrich

Body:
{
  "finding_id": "uuid",
  "resource_type": "s3",
  ...
}

Response:
{
  "finding_id": "uuid",
  "risk_score": 95.0,
  "severity": "critical",
  "estimated_cost": 500000,
  "recommendation": {...}
}
```

### Get Cached Findings
```
GET /cache/findings?severity=critical

Response:
{
  "severity": "critical",
  "count": 5,
  "findings": [...]
}
```

### Get Statistics
```
GET /stats

Response:
{
  "total_findings": 25,
  "severity_breakdown": {
    "critical": 5,
    "high": 8,
    "medium": 10,
    "low": 2
  },
  "average_risk_score": 72.5,
  "total_estimated_cost": "$5,000,000"
}
```

---

## Testing APIs

```bash
# Test Cloud Layer
curl http://localhost:8000/health

# Test Fog Layer
curl http://localhost:8001/health

# Post test finding to Fog Layer
curl -X POST http://localhost:8001/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "finding_id": "test-1",
    "resource_type": "s3",
    "finding_type": "public_s3_bucket",
    "is_public": 1,
    "is_encrypted": 0,
    "port_exposed": 0,
    "description": "Test bucket",
    "resource_id": "test-bucket"
  }'
```