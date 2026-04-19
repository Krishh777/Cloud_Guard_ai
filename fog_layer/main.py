"""
Fog Layer - Enrichment & Caching
NO DOCKER VERSION - Runs directly on your laptop
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

from fog_layer.enrichment import RiskEnrichment

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="CloudGuard AI - Fog Layer",
    description="Enrichment & Caching",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache
findings_cache = {}

CLOUD_API = os.getenv('CLOUD_API_ENDPOINT', 'http://localhost:8000')

class RawFinding(BaseModel):
    finding_id: str
    resource_type: str
    finding_type: str
    is_public: int
    is_encrypted: int
    port_exposed: int
    description: str
    resource_id: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Fog Layer",
        "cache_type": "In-Memory",
        "cached_findings": len(findings_cache)
    }

@app.post("/enrich")
async def enrich_finding(finding: RawFinding):
    logger.info(f"🌫️  Enriching finding: {finding.finding_id}")
    
    try:
        finding_dict = finding.dict()
        enriched = RiskEnrichment.enrich_finding(finding_dict)
        findings_cache[finding.finding_id] = enriched
        
        logger.debug(f"💾 Cached in memory: {finding.finding_id}")
        
        # Send to Cloud Layer
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{CLOUD_API}/analyze",
                    json=enriched
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Sent to Cloud Layer: {finding.finding_id}")
                else:
                    logger.warning(f"⚠️  Cloud Layer returned {response.status_code}")
        
        except Exception as e:
            logger.warning(f"⚠️  Could not reach Cloud Layer: {e}")
        
        return enriched
    
    except Exception as e:
        logger.error(f"❌ Enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/findings")
def get_cached_findings(severity: str = None):
    findings = list(findings_cache.values())
    
    if severity:
        findings = [f for f in findings if f.get('severity') == severity]
        return {"severity": severity, "count": len(findings), "findings": findings}
    
    return {"count": len(findings), "findings": findings}

@app.get("/stats")
def get_stats():
    findings = list(findings_cache.values())
    severity_count = {}
    
    for f in findings:
        severity = f.get('severity', 'unknown')
        severity_count[severity] = severity_count.get(severity, 0) + 1
    
    avg_risk = sum(f.get('risk_score', 0) for f in findings) / len(findings) if findings else 0
    total_cost = sum(f.get('estimated_cost', 0) for f in findings)
    
    return {
        "total_findings": len(findings),
        "severity_breakdown": severity_count,
        "average_risk_score": round(avg_risk, 2),
        "total_estimated_cost": f"${total_cost:,}",
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("\n" + "="*60)
    logger.info("🌫️  Starting Fog Layer")
    logger.info("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")