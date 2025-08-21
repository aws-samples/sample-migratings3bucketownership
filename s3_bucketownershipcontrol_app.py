#!/usr/bin/env python3
import boto3
import argparse
import logging
import configparser
import os
from s3_configuration_service import S3ConfigurationService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class WorkflowModel:
    """Simple workflow model to store bucket and account information."""
    
    def __init__(self, source_bucket, dest_bucket, dest_account, dest_region):
        self.source_bucket = source_bucket
        self.dest_bucket = dest_bucket
        self.dest_account = dest_account
        self.dest_region = dest_region
    
    def get_source_bucket_name(self):
        return self.source_bucket
    
    def get_dest_bucket_name(self):
        return self.dest_bucket
    
    def get_dest_account_number(self):
        return self.dest_account
    
    def get_dest_region(self):
        return self.dest_region
    
    def get_dest_role_arn(self):
        return f"arn:aws:iam::{self.dest_account}:role/S3MigrationRole"

def main():
    """Application to configure bucket ownership controls."""
    parser = argparse.ArgumentParser(description='Configure S3 bucket ownership controls')
    parser.add_argument('--source-region', required=True, help='Source AWS region')
    parser.add_argument('--dest-region', required=True, help='Destination AWS region')
    parser.add_argument('--source-bucket', required=True, help='Source bucket name')
    parser.add_argument('--dest-bucket', required=True, help='Destination bucket name')
    parser.add_argument('--dest_account_number', required=True, help='Destination AWS account number')
    parser.add_argument('--config', default='config.ini', help='Path to config file')
    
    args = parser.parse_args()
    
    # Read AWS credentials from config file
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.config)
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return
    
    config.read(config_path)
    aws_access_key = config.get('aws', 'aws_access_key_id')
    aws_secret_key = config.get('aws', 'aws_secret_access_key')
    
    # Initialize clients with credentials
    source_s3 = boto3.client(
        's3', 
        region_name=args.source_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )
    dest_s3 = boto3.client(
        's3', 
        region_name=args.dest_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )
    
    # Create workflow model
    workflow_model = WorkflowModel(
        args.source_bucket,
        args.dest_bucket,
        args.dest_account_number,
        args.dest_region
    )
    
    # Initialize service
    config_service = S3ConfigurationService()
    
    # Configure bucket ownership controls
    logger.info(f"Configuring bucket ownership controls from {args.source_bucket} to {args.dest_bucket}")
    config_service.configure_bucket_ownership_controls(
        source_s3,
        dest_s3,
        workflow_model
    )
    
    logger.info("Bucket ownership controls configuration completed successfully")

if __name__ == "__main__":
    main()