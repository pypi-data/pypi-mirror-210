"""
Workflow to extract a secret to config
"""

from archimedes_config.workflows.workflow_base import WorkflowBase


class ExtractSecret(WorkflowBase):
    """Class for extraction of secret"""

    def set_encrypted_key(self, encryption_key=None):
        """Sets encryption key"""

        if self.config_has_remote_conn_parameters():
            self.conf.set_default_key_from_key_vault()
        else:
            self.conf.set_default_key(encryption_key)

    def get_secret(self, file_name, group, key_name, encryption_key):
        """Extracts a secret from config"""
        self.load_file(file_name)
        self.set_encrypted_key(encryption_key)
        self.conf.decrypt_configs()
        return self.conf.get(group, key_name)
