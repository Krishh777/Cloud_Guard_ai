"""
Quick test to verify database configuration
Run this before using the system
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("🔍 TESTING DATABASE CONFIGURATION")
print("="*60 + "\n")

# Check .env values
print("📋 Environment Variables:")
print(f"  DB_HOST: {os.getenv('DB_HOST')}")
print(f"  DB_USER: {os.getenv('DB_USER')}")
print(f"  DB_NAME: {os.getenv('DB_NAME')}")
print(f"  DB_PORT: {os.getenv('DB_PORT')}")
print()

# Test connection
print("🔗 Testing Connection...")
try:
    from cloud_layer.database_handler import DatabaseHandler
    
    db = DatabaseHandler()
    print("✅ Connection successful!")
    
    # Test query
    findings = db.get_findings(limit=5)
    print(f"✅ Query successful! Found {len(findings)} findings")
    
    # Get stats
    stats = db.get_finding_stats()
    print(f"✅ Statistics retrieved")
    for stat in stats:
        print(f"   {stat['severity'].upper()}: {stat['count']} findings")
    
    db.close()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\n💡 Troubleshooting:")
    print("   1. Check AWS_ACCOUNT_ID is correct")
    print("   2. Check RDS is PUBLICLY ACCESSIBLE")
    print("   3. Check security group allows port 5432")
    print("   4. Check RDS is in 'Available' state")
    print("   5. Try: psql -h <DB_HOST> -U postgres -d cloudguard")

print("\n" + "="*60 + "\n")