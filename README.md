# S3 Bucket Ownership Migration code

The Python-based code is a sample code written for migrating S3 bucket ownership controls between AWS accounts. The code is written to help developers handle the error “OwnershipControlsNotFoundError” when get-bucket-ownership-controls API is used to read the S3 bucket ownership from buckets created prior to April 2023 when the bucket ownership was defaulted to “Object Writer”


## 📋 Prerequisites

- Python 3.7 or higher
- AWS CLI configured or AWS credentials available
- Appropriate IAM permissions for source and destination buckets
- Network connectivity to AWS S3 endpoints

### Required IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketOwnershipControls",
                "s3:PutBucketOwnershipControls",
                "s3:DeleteBucketOwnershipControls",
                "s3:GetBucketAcl",
                "s3:PutBucketAcl"
            ],
            "Resource": [
                "arn:aws:s3:::source-bucket-name",
                "arn:aws:s3:::destination-bucket-name"
            ]
        }
    ]
}
```

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aws-samples/sample-migratings3bucketownership.git
   cd S3Migration
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### 1. Create Configuration File

Create a `config.ini` file in the project root:

```ini
[aws]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
```

### 2. Environment Variables (Alternative)

You can also use environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=us-east-1
```

## 📖 Usage

### Basic Command

```bash
python s3_bucketownershipcontrol_app.py \
    --source-region us-east-1 \
    --dest-region us-west-2 \
    --source-bucket my-source-bucket \
    --dest-bucket my-dest-bucket \
    --dest_account_number 123456789012 \
    --config config.ini
```

### Command Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--source-region` | Yes | AWS region of the source bucket |
| `--dest-region` | Yes | AWS region of the destination bucket |
| `--source-bucket` | Yes | Name of the source S3 bucket |
| `--dest-bucket` | Yes | Name of the destination S3 bucket |
| `--dest_account_number` | Yes | AWS account number for the destination |
| `--config` | No | Path to configuration file (default: config.ini) |


## 🛠️ Error Handling

The tool implements comprehensive error handling:

### Exception Types

1. **OwnershipControlsNotFoundError**: Handles legacy buckets without ownership controls
2. **ClientError**: AWS API errors with specific error code handling
3. **AWSServiceException**: Custom exceptions for service-specific errors

**Note**: This tool modifies S3 bucket configurations. Always test in a non-production environment first and ensure you have proper backups before running migrations on production buckets.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

