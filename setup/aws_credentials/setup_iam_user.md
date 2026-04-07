# AWS IAM User Setup (For College Demo)

## Why? 
To protect your main AWS account and stay within free tier limits!

## Steps:

### 1. Go to AWS Console
- Open https://console.aws.amazon.com
- Login with your main account

### 2. Create IAM User
- Search for "IAM" → Click "Users" on left
- Click "Create user"
- Name: `cloudguard-demo-user`
- Check "Provide user access to AWS Management Console"
- Set password: something simple for demo
- Click "Next"

### 3. Add Permissions
- Click "Attach policies directly"
- Search & select these policies:
  - `AmazonEC2FullAccess`
  - `AmazonRDSFullAccess`
  - `AmazonDynamoDBFullAccess`
  - `AmazonS3FullAccess`
  - `AWSCloudTrailFullAccess`
  - `AmazonSNSFullAccess`
  - `CloudWatchFullAccess`
- Click "Next" → "Create user"

### 4. Create Access Keys
- Click the new user
- Go to "Security credentials" tab
- Scroll to "Access keys"
- Click "Create access key"
- Select "Command Line Interface (CLI)"
- Click "Next" → "Create access key"
- **SAVE the CSV file!!**

### 5. Configure AWS CLI
```bash
aws configure

# When prompted, paste:
AWS Access Key ID: [from CSV]
AWS Secret Access Key: [from CSV]
Default region: us-east-1
Default output format: json