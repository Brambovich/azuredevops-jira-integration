
from azurejiraintegration.azuredevops.azureconnection import AzureConnection
from azurejiraintegration.jira.jiraconnection import JiraConnection

import settings
from users import GitUsers

if __name__ == "__main__":
    azure = AzureConnection(settings.azure_organization_url, settings.azure_auth_token)
    azure.setAllowedJiraProjects(settings.JIRA_TEAMS)
    azure.setAllowedAzureProjects(settings.AZURE_PROJECTS)
    azure.setAzureJiraMap(GitUsers)
    azure.setExcludedAzureRepositories(settings.EXCLUDED_REPOS)

    jira = JiraConnection(settings.jira_oauth_clientid, settings.jira_oauth_clientsecret, settings.jira_cloud_id)

    jira.postDevelopmentInformation(azure.retrievePullRequests())
    jira.postDevelopmentInformation(azure.retrieveCommits())
