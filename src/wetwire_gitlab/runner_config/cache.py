"""Cache configuration for GitLab Runner."""

from dataclasses import dataclass
from typing import Any


@dataclass
class CacheS3Config:
    """S3 cache configuration.

    Attributes:
        server_address: S3-compatible server host:port.
        access_key: S3 access key.
        secret_key: S3 secret key.
        bucket_name: Storage bucket name.
        bucket_location: S3 region name.
        insecure: Use HTTP instead of HTTPS.
        authentication_type: Authentication method (access-key, iam).
    """

    server_address: str | None = None
    access_key: str | None = None
    secret_key: str | None = None
    bucket_name: str | None = None
    bucket_location: str | None = None
    insecure: bool = False
    authentication_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization.

        Returns:
            Dictionary with non-default values using TOML key names.
        """
        result: dict[str, Any] = {}

        if self.server_address is not None:
            result["ServerAddress"] = self.server_address
        if self.access_key is not None:
            result["AccessKey"] = self.access_key
        if self.secret_key is not None:
            result["SecretKey"] = self.secret_key
        if self.bucket_name is not None:
            result["BucketName"] = self.bucket_name
        if self.bucket_location is not None:
            result["BucketLocation"] = self.bucket_location
        if self.insecure:
            result["Insecure"] = self.insecure
        if self.authentication_type is not None:
            result["AuthenticationType"] = self.authentication_type

        return result


@dataclass
class CacheGCSConfig:
    """GCS cache configuration.

    Attributes:
        credentials_file: Path to Google JSON key file.
        access_id: GCP service account ID.
        private_key: GCP private key.
        bucket_name: Storage bucket name.
    """

    credentials_file: str | None = None
    access_id: str | None = None
    private_key: str | None = None
    bucket_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization.

        Returns:
            Dictionary with non-default values using TOML key names.
        """
        result: dict[str, Any] = {}

        if self.credentials_file is not None:
            result["CredentialsFile"] = self.credentials_file
        if self.access_id is not None:
            result["AccessID"] = self.access_id
        if self.private_key is not None:
            result["PrivateKey"] = self.private_key
        if self.bucket_name is not None:
            result["BucketName"] = self.bucket_name

        return result


@dataclass
class CacheConfig:
    """Cache configuration for a runner.

    Attributes:
        type: Cache backend (s3, gcs, azure).
        path: Path prefix for cache URL.
        shared: Enable cache sharing between runners.
        s3: S3 cache configuration.
        gcs: GCS cache configuration.
    """

    type: str | None = None
    path: str | None = None
    shared: bool = False
    s3: CacheS3Config | None = None
    gcs: CacheGCSConfig | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization.

        Returns:
            Dictionary with non-default values using TOML key names.
        """
        result: dict[str, Any] = {}

        if self.type is not None:
            result["Type"] = self.type
        if self.path is not None:
            result["Path"] = self.path
        if self.shared:
            result["Shared"] = self.shared

        return result
