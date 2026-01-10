"""Terraform/OpenTofu component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class TerraformComponent(ComponentBase):
    """GitLab OpenTofu (Terraform) component wrapper.

    Provides infrastructure as code deployment with OpenTofu/Terraform.

    See: https://docs.gitlab.com/ee/user/infrastructure/iac/

    Attributes:
        terraform_root_dir: Root directory for Terraform files.
        terraform_state_name: State file name.
        version: Component version.
    """

    terraform_root_dir: str | None = None
    terraform_state_name: str | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/opentofu"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        if self.terraform_root_dir:
            inputs["TERRAFORM_ROOT_DIR"] = self.terraform_root_dir

        if self.terraform_state_name:
            inputs["TERRAFORM_STATE_NAME"] = self.terraform_state_name

        return inputs
