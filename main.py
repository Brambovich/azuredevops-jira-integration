
from azurejiraintegration.azuredevops.azureconnection import AzureConnection
from azurejiraintegration.jira.jiraconnection import JiraConnection
import yaml
from datetime import datetime
from time import sleep
from users import GitUsers

def runTimingLoop(config, azure, jira):
    secondSleep = 600
    if 'update_timer' in config['General']:
        secondSleep = config['General']['update_timer']
    while(1):
        print(f" --- {datetime.now()} ---")
        print("### Pull Requests ###")
        jira.postDevelopmentInformation(azure.retrievePullRequests())
        print("### Commits ###")
        jira.postDevelopmentInformation(azure.retrieveCommits())
        sleep(secondSleep)

if __name__ == "__main__":
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)

    if "Azure" not in config:
        print("Azure not in config")
    
    azure = AzureConnection(config['Azure']['organization_url'], config['Azure']['auth_token'])

    if 'team_whitelist' in config['Jira']:
        azure.setAllowedJiraProjects(config['Jira']['team_whitelist'])
    if 'projects_whitelist' in config['Azure']:
        azure.setAllowedAzureProjects(config['Azure']['projects_whitelist'])
    if 'repository_blacklist' in config['Azure']:
        azure.setRepositoryBlacklist(config['Azure']['repository_blacklist'])
    if 'min_minutes_ago_updated' in config['Azure']:
        azure.setMinMinutesAgoUpdated(config['Azure']['min_minutes_ago_updated'])
    if 'exclude_draft_pr' in config['Azure']:
        azure.setDraftExclusion(config['Azure']['exclude_draft_pr'])

    azure.setAzureJiraMap(GitUsers)
    jira = JiraConnection(config['Jira']['client_id'], config['Jira']['client_secret'], config['Jira']['cloud_id'])

    runTimingLoop(config, azure, jira)
