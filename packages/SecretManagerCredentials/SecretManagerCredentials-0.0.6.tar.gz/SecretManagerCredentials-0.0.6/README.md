# Vault Credential Fetcher
Convenient wrapper for executing codes on AWS for connecting and fetching credentials from vault.

## Install with pip
```bash
$ pip install SecretManagerCredentials
```

## Usage
1. Import the library.
    ```python
   from SecretManagerCredentials.SecretManagerFetcher import SecretManagerFetcher
    ```

1. Create an instance.
    ```python 
   SM = SecretManagerFetcher(project_path="",
                               logger=<your_logger_instance>,
                               environment="",
                               display_vault_info=True,
                               vault_config_path="")
    ```
    Arguments (all are mandatory):
    * `project_path`: Project name, which would serve as the logger's name (*if specified*), and the prefix for log filenames.
    * `logger`: your Logger Instance
    * `"environment"`: Execution Environment
    * `"display_vault_info"`: By default it is False, used for displaying vault info
    * `"vault_config_path"`: Path where vault config is kept, relative to project path
    
2. Get a logger and start logging.
    ```python
   VaultCreds = SM.get_vault_cred()
    ```

## Author

**&copy; 2022, [Priyansh Gupta](priyansh.gupta@gartner.com)**.