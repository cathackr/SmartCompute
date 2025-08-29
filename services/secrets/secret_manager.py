#!/usr/bin/env python3
"""
SmartCompute Secret Manager
Handles integration with HashiCorp Vault and AWS Secrets Manager
"""

import os
import json
import asyncio
import logging
from typing import Dict, Optional, Any, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SecretManagerInterface(ABC):
    """Abstract interface for secret managers"""
    
    @abstractmethod
    async def get_secret(self, key: str) -> Optional[str]:
        """Get a secret by key"""
        pass
    
    @abstractmethod
    async def set_secret(self, key: str, value: str) -> bool:
        """Set a secret"""
        pass
    
    @abstractmethod
    async def delete_secret(self, key: str) -> bool:
        """Delete a secret"""
        pass
    
    @abstractmethod
    async def list_secrets(self) -> list:
        """List available secrets"""
        pass


class HashiCorpVaultManager(SecretManagerInterface):
    """HashiCorp Vault secret manager implementation"""
    
    def __init__(self, vault_addr: str = None, vault_token: str = None):
        self.vault_addr = vault_addr or os.getenv('VAULT_ADDR', 'http://localhost:8200')
        self.vault_token = vault_token or os.getenv('VAULT_TOKEN')
        self.mount_point = 'secret'
        
        if not self.vault_token:
            logger.warning("No VAULT_TOKEN provided, Vault operations will fail")
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make HTTP request to Vault API"""
        try:
            import httpx
            
            headers = {
                'X-Vault-Token': self.vault_token,
                'Content-Type': 'application/json'
            }
            
            url = f"{self.vault_addr}/v1/{endpoint}"
            
            async with httpx.AsyncClient() as client:
                if method.upper() == 'GET':
                    response = await client.get(url, headers=headers, timeout=10)
                elif method.upper() == 'POST':
                    response = await client.post(url, headers=headers, json=data, timeout=10)
                elif method.upper() == 'DELETE':
                    response = await client.delete(url, headers=headers, timeout=10)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                
                if response.status_code == 204:  # No content
                    return {}
                
                return response.json()
                
        except ImportError:
            logger.error("httpx not installed. Install with: pip install httpx")
            return None
        except Exception as e:
            logger.error(f"Vault request failed: {e}")
            return None
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret from Vault KV store"""
        endpoint = f"{self.mount_point}/data/{key}"
        response = await self._make_request('GET', endpoint)
        
        if response and 'data' in response and 'data' in response['data']:
            return response['data']['data'].get('value')
        
        return None
    
    async def set_secret(self, key: str, value: str) -> bool:
        """Set secret in Vault KV store"""
        endpoint = f"{self.mount_point}/data/{key}"
        data = {
            'data': {
                'value': value
            }
        }
        
        response = await self._make_request('POST', endpoint, data)
        return response is not None
    
    async def delete_secret(self, key: str) -> bool:
        """Delete secret from Vault"""
        endpoint = f"{self.mount_point}/metadata/{key}"
        response = await self._make_request('DELETE', endpoint)
        return response is not None
    
    async def list_secrets(self) -> list:
        """List secrets in Vault"""
        endpoint = f"{self.mount_point}/metadata?list=true"
        response = await self._make_request('GET', endpoint)
        
        if response and 'data' in response and 'keys' in response['data']:
            return response['data']['keys']
        
        return []


class AWSSecretsManager(SecretManagerInterface):
    """AWS Secrets Manager implementation"""
    
    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.client = None
        
    async def _get_client(self):
        """Get boto3 secrets manager client"""
        if self.client is None:
            try:
                import boto3
                self.client = boto3.client('secretsmanager', region_name=self.region_name)
            except ImportError:
                logger.error("boto3 not installed. Install with: pip install boto3")
                return None
        return self.client
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        client = await self._get_client()
        if not client:
            return None
        
        try:
            response = client.get_secret_value(SecretId=key)
            return response.get('SecretString')
        except Exception as e:
            logger.error(f"Failed to get AWS secret {key}: {e}")
            return None
    
    async def set_secret(self, key: str, value: str) -> bool:
        """Set secret in AWS Secrets Manager"""
        client = await self._get_client()
        if not client:
            return False
        
        try:
            # Try to update first
            try:
                client.update_secret(SecretId=key, SecretString=value)
                return True
            except client.exceptions.ResourceNotFoundException:
                # Create new secret if it doesn't exist
                client.create_secret(Name=key, SecretString=value)
                return True
        except Exception as e:
            logger.error(f"Failed to set AWS secret {key}: {e}")
            return False
    
    async def delete_secret(self, key: str) -> bool:
        """Delete secret from AWS Secrets Manager"""
        client = await self._get_client()
        if not client:
            return False
        
        try:
            client.delete_secret(SecretId=key, ForceDeleteWithoutRecovery=True)
            return True
        except Exception as e:
            logger.error(f"Failed to delete AWS secret {key}: {e}")
            return False
    
    async def list_secrets(self) -> list:
        """List secrets in AWS Secrets Manager"""
        client = await self._get_client()
        if not client:
            return []
        
        try:
            response = client.list_secrets()
            return [secret['Name'] for secret in response.get('SecretList', [])]
        except Exception as e:
            logger.error(f"Failed to list AWS secrets: {e}")
            return []


class EnvironmentSecretManager(SecretManagerInterface):
    """Environment variables secret manager (fallback)"""
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret from environment variables"""
        return os.getenv(key)
    
    async def set_secret(self, key: str, value: str) -> bool:
        """Set environment variable (not persistent)"""
        os.environ[key] = value
        return True
    
    async def delete_secret(self, key: str) -> bool:
        """Delete environment variable"""
        if key in os.environ:
            del os.environ[key]
            return True
        return False
    
    async def list_secrets(self) -> list:
        """List environment variables (filtered)"""
        # Return common secret keys only
        secret_keys = []
        for key in os.environ:
            if any(pattern in key.lower() for pattern in ['password', 'secret', 'token', 'key', 'api']):
                secret_keys.append(key)
        return secret_keys


class SmartComputeSecretManager:
    """Main secret manager with fallback support"""
    
    def __init__(self, primary_backend: str = 'vault'):
        self.primary_backend = primary_backend
        self.managers = {}
        
        # Initialize managers
        if primary_backend == 'vault':
            self.managers['vault'] = HashiCorpVaultManager()
            self.managers['aws'] = AWSSecretsManager()
            self.managers['env'] = EnvironmentSecretManager()
            self.fallback_order = ['vault', 'aws', 'env']
        elif primary_backend == 'aws':
            self.managers['aws'] = AWSSecretsManager()
            self.managers['vault'] = HashiCorpVaultManager()
            self.managers['env'] = EnvironmentSecretManager()
            self.fallback_order = ['aws', 'vault', 'env']
        else:
            self.managers['env'] = EnvironmentSecretManager()
            self.fallback_order = ['env']
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret with fallback support"""
        for backend in self.fallback_order:
            if backend in self.managers:
                try:
                    value = await self.managers[backend].get_secret(key)
                    if value:
                        logger.debug(f"Retrieved secret '{key}' from {backend}")
                        return value
                except Exception as e:
                    logger.warning(f"Failed to get secret from {backend}: {e}")
                    continue
        
        logger.error(f"Failed to retrieve secret '{key}' from any backend")
        return None
    
    async def set_secret(self, key: str, value: str, backend: str = None) -> bool:
        """Set secret in specified backend or primary"""
        target_backend = backend or self.primary_backend
        
        if target_backend in self.managers:
            try:
                success = await self.managers[target_backend].set_secret(key, value)
                if success:
                    logger.info(f"Set secret '{key}' in {target_backend}")
                return success
            except Exception as e:
                logger.error(f"Failed to set secret in {target_backend}: {e}")
        
        return False
    
    async def get_database_credentials(self) -> Dict[str, str]:
        """Get database connection credentials"""
        credentials = {}
        
        # Get main database credentials
        credentials['DB_PASSWORD'] = await self.get_secret('DB_PASSWORD') or 'password'
        credentials['DATABASE_URL'] = await self.get_secret('DATABASE_URL') or f"postgresql://smartcompute:{credentials['DB_PASSWORD']}@localhost:5432/smartcompute"
        
        # Get payment database credentials
        credentials['PAYMENT_DB_PASSWORD'] = await self.get_secret('PAYMENT_DB_PASSWORD') or 'payment_password'
        
        # Get monitoring database credentials
        credentials['MONITORING_DB_PASSWORD'] = await self.get_secret('MONITORING_DB_PASSWORD') or 'monitoring_password'
        
        return credentials
    
    async def get_service_credentials(self) -> Dict[str, str]:
        """Get service-specific credentials"""
        credentials = {}
        
        # Redis credentials
        credentials['REDIS_PASSWORD'] = await self.get_secret('REDIS_PASSWORD') or 'redis_password'
        
        # JWT secrets
        credentials['JWT_SECRET'] = await self.get_secret('JWT_SECRET') or 'your-secret-key-change-in-production'
        
        # Payment webhook secrets
        credentials['PAYMENT_WEBHOOK_SECRET'] = await self.get_secret('PAYMENT_WEBHOOK_SECRET') or 'webhook_secret'
        
        # Vault credentials
        credentials['VAULT_ROOT_TOKEN'] = await self.get_secret('VAULT_ROOT_TOKEN') or 'dev-only-token'
        
        # Grafana password
        credentials['GRAFANA_PASSWORD'] = await self.get_secret('GRAFANA_PASSWORD') or 'admin123'
        
        return credentials
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all secret manager backends"""
        health = {}
        
        for backend_name, manager in self.managers.items():
            try:
                # Try to list secrets as a health check
                await asyncio.wait_for(manager.list_secrets(), timeout=5.0)
                health[backend_name] = True
            except Exception as e:
                logger.warning(f"Health check failed for {backend_name}: {e}")
                health[backend_name] = False
        
        return health


# Global secret manager instance
secret_manager = SmartComputeSecretManager(
    primary_backend=os.getenv('SECRET_BACKEND', 'vault')
)


async def main():
    """Test secret manager functionality"""
    logger.info("Testing SmartCompute Secret Manager...")
    
    # Health check
    health = await secret_manager.health_check()
    logger.info(f"Backend health: {health}")
    
    # Test database credentials
    db_creds = await secret_manager.get_database_credentials()
    logger.info(f"Database credentials loaded: {list(db_creds.keys())}")
    
    # Test service credentials
    service_creds = await secret_manager.get_service_credentials()
    logger.info(f"Service credentials loaded: {list(service_creds.keys())}")
    
    logger.info("Secret manager test completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())