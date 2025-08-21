#!/usr/bin/env python3
import boto3
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AWSServiceException(Exception):
    """Custom exception for AWS service errors."""
    pass

class S3ConfigurationService:
    """Service to manage S3 bucket configurations."""
    
    # Configuration keys
    OWNERSHIP_CONTROLS_NOT_FOUND_ERROR = "OwnershipControlsNotFoundError"

    def configure_bucket_ownership_controls(self, source_client, dest_client, workflow_model):
        """Configure bucket ownership controls."""
        dest_bucket = workflow_model.get_dest_bucket_name()
        source_bucket = workflow_model.get_source_bucket_name()
        dest_account = workflow_model.get_dest_account_number()
        
        try:
            ownership_response = source_client.get_bucket_ownership_controls(Bucket=source_bucket)
            
            if 'Rules' in ownership_response.get('OwnershipControls', {}):
                source_ownership = ownership_response['OwnershipControls']['Rules'][0]['ObjectOwnership']
                
                if source_ownership == 'BucketOwnerEnforced':
                    logger.info("BucketOwnerEnforced default Rule is enabled, no action required")
                else:
                    logger.info(f"Non-default Rules! {ownership_response['OwnershipControls']['Rules']}")
                    logger.info(f"Copying bucket ownership controls from: {source_bucket} to {dest_bucket}")
                    
                    dest_client.put_bucket_ownership_controls(
                        Bucket=dest_bucket,
                        ExpectedBucketOwner=dest_account,
                        OwnershipControls={
                            'Rules': ownership_response['OwnershipControls']['Rules']
                        }
                    )
                    
                    self._copy_custom_bucket_acls(source_client, dest_client, source_bucket, dest_bucket, dest_account)
        except ClientError as e:
            if e.response['Error']['Code'] == self.OWNERSHIP_CONTROLS_NOT_FOUND_ERROR:
                logger.warning("OWNERSHIP_CONTROLS_NOT_FOUND_ERROR")
                self._handle_ownership_controls_not_found(source_client, dest_client, source_bucket, dest_bucket, dest_account)
            else:
                logger.error(f"Exception while configuring bucket: {e}")
                raise

    def _handle_ownership_controls_not_found(self, source_client, dest_client, source_bucket, dest_bucket, dest_account):
        """Handle case when ownership controls are not found."""
        logger.info("OwnershipControlsNotFoundError - This is an older bucket. "
                   "Applying DEL operation to destination bucket.")
        try:
            dest_client.delete_bucket_ownership_controls(Bucket=dest_bucket)
            logger.info(f"Successfully deleted bucket ownership controls for destination bucket: {dest_bucket}")
            
            self._copy_custom_bucket_acls(source_client, dest_client, source_bucket, dest_bucket, dest_account)
        except ClientError as e:
            logger.error(f"Error deleting bucket ownership controls: {e}")
            raise AWSServiceException(f"Error deleting bucket ownership controls: {e}")

    def _copy_custom_bucket_acls(self, source_client, dest_client, source_bucket, dest_bucket, dest_account):
        """Copy custom bucket ACLs from source to destination bucket."""
        # Get source bucket ACL
        source_acl_response = source_client.get_bucket_acl(Bucket=source_bucket)
        
        # Get destination bucket owner
        dest_acl_response = dest_client.get_bucket_acl(Bucket=dest_bucket)
        dest_owner = dest_acl_response['Owner']
        
        if 'Grants' in source_acl_response:
            logger.info(f"Source Bucket ACL: {source_acl_response}")
            dest_grants = []
            for grant in source_acl_response['Grants']:
                if grant['Grantee'].get('ID') != source_acl_response['Owner']['ID']:
                    dest_grants.append(grant)
            
            if dest_grants:
                logger.info(f"Dest Bucket ACL: {dest_grants}")
                dest_client.put_bucket_acl(
                    Bucket=dest_bucket,
                    ExpectedBucketOwner=dest_account,
                    AccessControlPolicy={
                        'Owner': dest_owner,
                        'Grants': dest_grants
                    }
                )