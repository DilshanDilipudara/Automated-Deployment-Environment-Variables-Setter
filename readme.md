# Automated Deployment Environment Variables Setter

This script automates the process of setting environment variables in Kubernetes deployment YAML files based on specific criteria. It is particularly useful for managing multiple microservices with different configurations in a Kubernetes environment.

## Overview

The script performs the following tasks:

1. **Download Repository**: Clones all projects within a specified GitLab group into a local directory.
2. **Process Deployment Files**: Iterates through each project's `deployment.yaml` files, setting environment variables based on predefined rules.
3. **Upload Repository**: Commits the modified `deployment.yaml` files and pushes them back to the GitLab repository.

## Prerequisites

- Python 3.x
- GitLab API Access Token
- GitLab Group ID

## Usage

1. Clone this repository to your local machine.
2. Replace the placeholder values in the script with your GitLab URL, access token, group ID, and root directory.
3. Run the script using `python main.py`.

## Configuration

Modify the script's variables as needed:

- `url`: URL of your GitLab instance.
- `private_token`: GitLab API access token.
- `group_id`: ID of the GitLab group containing the projects.
- `rootdir`: Root directory to clone the projects.
- `depth`: Depth to which the script should clone repositories.

