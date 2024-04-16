
import re
import time

from azure.devops.credentials import BasicAuthentication
from azure.devops.connection import Connection
from azure.devops.v7_1.git.models import GitQueryCommitsCriteria, GitPullRequestSearchCriteria

from types import SimpleNamespace
from datetime import timedelta, timezone, datetime
import pandas as pd
    
def formatDate(inputDate):
    outputString = pd.to_datetime(inputDate, utc=True).strftime('%Y-%m-%dT%H:%M:%S+00:00')

class AzureConnection():
    def __init__(self, organization_url, auth_token):
        self.context = SimpleNamespace()
        self.context.runner_cache = SimpleNamespace()
        self.organization_url = organization_url
        self.context.connection = Connection(
            base_url=organization_url,
            creds=BasicAuthentication('PAT', auth_token)
        )
        self.git_client = self.context.connection.clients.get_git_client()

    def setAllowedJiraProjects(self, projectList):
        self.allowedJiraProjects = projectList

    def checkAllowedTicket(self, ticketNumber):
        if any(jiraTeamName in ticketNumber for jiraTeamName in self.allowedJiraProjects):
            return True
        else:
            return False

    def FindProjects(self):
        totalProjects = []
        core_client = self.context.connection.clients.get_core_client()
        projects = core_client.get_projects()
        if (len(projects) == 0):
            raise Exception('Your account doesn''t appear to have any projects available.')
        for project in projects:
            if project.name in self.allowedAzureProjects:
                totalProjects.append(project)
        return totalProjects
    
    def setAllowedAzureProjects(self, azureProjects):
        self.allowedAzureProjects = azureProjects

    def setAzureJiraMap(self, map):
        self.azureJiraMap = map

    def setExcludedAzureRepositories(self, repos):
        self.excludedAzureRepositories = repos

    def createUserJson(self, userName):
        if userName in self.azureJiraMap:
            userDict = {"accountId" : self.azureJiraMap[userName]}
        else:
            print(userName, " is not in GitUsers dictionary")
            userDict = {"name" : userName}
        return userDict
    
    def createReviewerJson(self, reviewer):
        if reviewer.display_name in self.azureJiraMap:
            reviewerDict = {"accountId" : self.azureJiraMap[reviewer.display_name]}
        else:
            print(reviewer.display_name, " is not in GitUsers dictionary")
            reviewerDict = {"name" : reviewer.display_name}
        reviewerDict["approvalStatus"] = "APPROVED" if reviewer.vote == 10 else "UNAPPROVED"
        return reviewerDict

    def retrieveLastUpdatedDate(self, pr, repo):
        dates = []
        if pr.closed_date:
            return pr.closed_date
        
        dates.append(pr.creation_date)
        threads = self.git_client.get_threads(repo.id, pr.pull_request_id)
        for thread in threads:
            dates.append(thread.last_updated_date)
        return max(dates).strftime('%Y-%m-%dT%H:%M:%S+00:00')


    def retrievePullRequests(self):
        start_time = time.time()
        projects = self.FindProjects()
        fullJson = {}
        fullJson["repositories"] = []
        for project in projects:
            repos = self.git_client.get_repositories(project.id)
            for repo in repos:
                if (repo.name in self.excludedAzureRepositories):
                    continue
                try:
                    searchCriteria  = GitPullRequestSearchCriteria()
                    pullRequests = self.git_client.get_pull_requests(repo.id, search_criteria=searchCriteria, top=3)
                except:
                    continue
                prList = []
                for pr in pullRequests:
                    regexMatch = re.search("[A-Z][A-Z0-9_]+-[1-9][0-9]*", pr.title)
                    if regexMatch:
                        ticketNumber = regexMatch.group()
                        if self.checkAllowedTicket(ticketNumber):
                            print(f"[{self.retrieveLastUpdatedDate(pr, repo)[0:10]}] --> {pr.created_by.display_name} : {pr.title}")
                            prDict = {}
                            prDict["title"] = pr.title
                            prDict["id"] = pr.pull_request_id
                            prDict["url"] = f"{self.organization_url}/{project.name}/_git/{repo.name}/pullrequest/{pr.pull_request_id}"
                            prDict["author"] = self.createUserJson(pr.created_by.display_name)
                            prDict["status"] = "OPEN" if pr.status == "active" else "CLOSED"
                            prDict["issueKeys"] = [str(ticketNumber)]
                            prDict["updateSequenceId"] = int(round(time.time() * 1000))
                            prDict["commentCount"] = len(self.git_client.get_threads(repo.id, pr.pull_request_id))
                            prDict["sourceBranch"] = pr.source_ref_name.split("heads/", 1)[1]
                            prDict["destinationBranch"] = pr.target_ref_name.split("heads/", 1)[1]
                            prDict["displayId"] = str(pr.pull_request_id)
                            prDict["lastUpdate"] = self.retrieveLastUpdatedDate(pr, repo)
                            prDict["reviewers"] = [self.createReviewerJson(reviewer) for reviewer in pr.reviewers]
                            prList.append(prDict)
                if len(prList) != 0:
                    fullJson["repositories"].append({"name":repo.name, "url":repo.remote_url, "id": repo.id, "updateSequenceId": int(round(time.time() * 1000)), "pullRequests":prList})
        print("retrieve Commit time spent:", round(time.time() - start_time,1), "seconds")
        return fullJson

    def retrieveCommits(self):
        start_time = time.time()
        projects = self.FindProjects()
        fullJson = {}
        fullJson["repositories"] = []
        for project in projects:
            repos = self.git_client.get_repositories(project.id)
            for repo in repos:
                if (repo.name in self.excludedAzureRepositories):
                    continue
                searchCriteria  = GitQueryCommitsCriteria()
                searchCriteria.top = 5
                try:
                    commits = self.git_client.get_commits(repo.id, search_criteria=searchCriteria)
                except:
                    continue
                commitList = []
                
                for commit in reversed(commits):
                    regexMatch = re.search("[A-Z][A-Z0-9_]+-[1-9][0-9]*", commit.comment)
                    if regexMatch:
                        ticketNumber = regexMatch.group()
                        if self.checkAllowedTicket(ticketNumber):
                            print(f"[{commit.author.date.strftime('%Y-%m-%d')}] --> {commit.author.name} : {commit.comment}")
                            commitDict = {}
                            commitDict["issueKeys"] = [str(ticketNumber)]
                            commitDict["id"] = commit.commit_id
                            commitDict["updateSequenceId"] = int(round(time.time() * 1000))
                            commitDict["message"] = commit.comment
                            commitDict["author"] = self.createUserJson(commit.author.name)
                            commitDict["authorTimestamp"] = commit.author.date.strftime('%Y-%m-%dT%H:%M:%S+00:00')
                            commitDict["displayId"] = commit.commit_id[0:8]
                            commitDict["fileCount"] = commit.change_counts["Add"] + commit.change_counts["Edit"] + commit.change_counts["Delete"]
                            commitDict["url"] = commit.remote_url
                            commitList.append(commitDict)
                if len(commitList) != 0:
                    fullJson["repositories"].append({"name":repo.name, "url":repo.remote_url, "id": repo.id, "updateSequenceId": int(round(time.time() * 1000)), "commits":commitList})
        print("retrieve Commit time spent:", time.time() - start_time, "seconds")
        return fullJson

