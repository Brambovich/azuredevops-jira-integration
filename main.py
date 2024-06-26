
from azurejiraintegration.azuredevops.azureconnection import AzureConnection
from azurejiraintegration.jira.jiraconnection import JiraConnection
import yaml
from datetime import datetime
from time import sleep
from users import GitUsers
import logging

logger = logging.getLogger("azurejiraintegration")
YAML_FILE_NAME = "config.yml"

def updateDateInConfig(config):
    config['General']['latest_date_updated'] = datetime.now()
    with open(YAML_FILE_NAME, 'w') as file:
        file.write( yaml.dump(config, default_flow_style=False))

def runTimingLoop(config, azure, jira):
    secondSleep = 600
    if 'update_timer' in config['General']:
        secondSleep = config['General']['update_timer']
    while(1):
        logger.debug(f" --- {datetime.now()} ---")
        logger.debug("### Pull Requests ###")
        jira.postDevelopmentInformation(azure.retrievePullRequests())
        logger.debug("### Commits ###")
        jira.postDevelopmentInformation(azure.retrieveCommits())
        azure.setMinMinutesAgoUpdated(config['Azure']['min_minutes_ago_updated'])
        updateDateInConfig(config)
        sleep(secondSleep)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    
    with open(YAML_FILE_NAME, 'r') as file:
        config = yaml.safe_load(file)

    if "Azure" not in config:
        logger.error("Azure not in config")

    azure = AzureConnection(config['Azure']['organization_url'], config['Azure']['auth_token'])

    if 'team_whitelist' in config['Jira']:
        azure.setAllowedJiraProjects(config['Jira']['team_whitelist'])
    if 'projects_whitelist' in config['Azure']:
        azure.setAllowedAzureProjects(config['Azure']['projects_whitelist'])
    if 'repository_blacklist' in config['Azure']:
        azure.setRepositoryBlacklist(config['Azure']['repository_blacklist'])
    if 'min_minutes_ago_updated' not in config['Azure']:
        logger.error("[ERROR] there should be a key in [Azure] called min_minutes_ago_updated")
    azure.setMinMinutesAgoUpdated(config['Azure']['min_minutes_ago_updated'])
    if 'exclude_draft_pr' in config['Azure']:
        azure.setDraftExclusion(config['Azure']['exclude_draft_pr'])

    azure.setAzureJiraMap(GitUsers)
    jira = JiraConnection(config['Jira']['client_id'], config['Jira']['client_secret'], config['Jira']['cloud_id'])

    if ('debug' in config['General']) and (config['General']['debug'] == True):
        logging.getLogger("azurejiraintegration").setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled!")

    if 'latest_date_updated' in config['General']:
        newUpdateTimer = round((datetime.now() - config['General']['latest_date_updated']).total_seconds() / 60)+5
        azure.setMinMinutesAgoUpdated(newUpdateTimer)
        logger.info(f"Latest run of this script was at: {config['General']['latest_date_updated']}")
        logger.info(f"setting updateTimer temporarily to {newUpdateTimer} minutes")

    runTimingLoop(config, azure, jira)
