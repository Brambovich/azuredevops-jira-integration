# azuredevops-jira-integration
Lightweight python server to automatically sync commits/pr's from azure devops to Jira via their REST api's.

This small python script is able to connect to both Azure devops and Atlassian Jira to sync all commits and pull-requests. The git items are retrieved from azure via their [Python SDK](https://github.com/microsoft/azure-devops-python-api). These are then sent with the Atlassian Jira REST api to fill the development tab. 

Commits and pull-requests have to be linked by using the Jira issue inside of the comment/title.

## Authentication
How to authenticate the tool to both online environments.
### Azure Devops
Azure devops connection is made very simple with a access token. Make sure that you are using an account which has the correct access rights on the projects you are trying to sync. Afterwards create a Access Token and insert it into your copy of [config.yml](config.yml).
### Atlassian Jira
For Jira we require a few more steps, since the development information is locked behind a OAuth token. Let an administrator create this OAuth token on the following page (Apps->Oauth)
![oauth](docs/images/OAuth.PNG?raw=true "Code tab inside of Jira")
This new credential should have the "Development information" access rights. You can name it anything you like. Then copy the Client ID and client Secret to your copy of [config.yml](config.yml).

For the atlassian authentication we also need your organizations "cloud id" this variable is gained by using the following website with your organization URL: (example my-site-name)
https://my-site-name.atlassian.net/_edge/tenant_info

Save this cloud ID to [config.yml](config.yml).

## Configuration

The [config.yml](config.yml) file can be used for personal configuration. The variables are explained below:

| Environment variable          | ValueType    | Explanation/usage                                                                                                                                                                                    |
|-------------------------------|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Azure.organization_url        | string       | Your azure devops organizational URL.                                                                                                                                                                |
| Azure.auth_token              | string       | Your Azure Personal Access Token (PAT)                                                                                                                                                               |
| Azure.projects_whitelist      | list(string) | A list of string with the Azure Devops Projects you want to monitor.                                                                                                                                 |
| Azure.repository_blacklist    | list(string) | A list of string with the global repositories (accross all projects) that you would want to exclude.  This could be used for speedup, since some repositories are huge, wich will take a long time.  |
| Azure.exclude_draft_pr        | bool         | Option to exlcude draft pull-requests.                                                                                                                                                               |
| Azure.min_minutes_ago_updated | int          | Minimum minutes ago that a Git Item was updated in Minutes. When set, it will only trigger on  commits and pull-requests that are updated in that timespan.                                          |
| Jira.cloud_id                 | string       | Your Jira cloud-id. Explained in Atlassian Jira configuration.                                                                                                                                       |
| Jira.client_id                | string       | Your Jira client-id                                                                                                                                                                                  |
| Jira.client_secret            | string       | Your Jira client-secret                                                                                                                                                                              |
| Jira.team_whitelist           | list(string) | A whitelist with all teams that you want to monitor within Jira.  The list should exist of the alphabetic code of the Team. (e.g. KAN)                                                               |
| General.debug                 | bool         | When enabled, debug messaging is showed.                                                                                                                                                             |
| General.update_timer          | int          | Timer in seconds. How long the code waits in between pulling the commits/pull-requests.                                                                                                              |
| General.updated_properties    | list(string) | [Work in progress] An option list of items which the tool should sync.  options: ["commit", "pull_request", "branch"]                                                                                |


## Usage
When running main.py it is advised to setup a virtualenv for this. You can install the requirements.txt to instantly have all requirements. Then running main.py without any variables is sufficient. 

Now all commits and pull-requests that have a jira issue number (e.g KAN-123) inside their comment/title are linked to their Jira issue.

Now your commits and pull-requests are synced every N minutes, depending on your configuration. In the code tab of Jira you can sees all open pull-requests:
![code_tab](docs/images/Code_tab.PNG?raw=true "Code tab inside of Jira")

Also in your tickets the development information is available, for a ticket specific view:
![development_tab](docs/images/Development_tab.PNG?raw=true "Code tab inside of Jira")
