import requests
import json

class JiraConnection:
    def __init__(self, clientID, clientSecret, clientCloudId):
        self.clientId = clientID
        self.clientSecret = clientSecret
        self.cloudId = clientCloudId

    def retrieveOAuthToken(self):
        data_request = {
            'grant_type': 'client_credentials'
        }

        response = requests.post('https://auth.atlassian.com/oauth/token', data=data_request, allow_redirects=False, auth=(self.clientId, self.clientSecret))
        print("token response code: ", response.status_code)
        token = json.loads(response.text)
        access_token = token['access_token']
        return access_token

    def postDevelopmentInformation(self, payload):
        if len(payload["repositories"]) == 0:
            return
    
        access_token = self.retrieveOAuthToken()

        url = f"https://api.atlassian.com/jira/devinfo/0.1/cloud/{self.cloudId}/bulk"

        headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(access_token),
        }

        response = requests.request(
            "POST",
            url,
            data=json.dumps(payload),
            headers=headers
        )

        if (response.status_code != 202):
            print(response.__dict__)
            print("-------------")
            print(response.request.body)
        else:
            print(f"Upload to development information successful!: {response.status_code}!")

    def removeDevelopmentInformation(self, repoId, entityType, entityId):
        if (entityType not in ["commit", "branch", "pull_request"]):
            print("entity type should be in:", ["commit", "branch", "pull_request"])
            return 
        
        access_token = self.retrieveOAuthToken()

        requestHeaders = {
            "Authorization": "Bearer {}".format(access_token),
        }

        url = f"https://your-domain.atlassian.net/rest/devinfo/0.10/repository/{repoId}/{entityType}/{entityId}"

        response = requests.request(
            "DELETE",
            url,
            headers=requestHeaders
        )

        if (response.status_code != 202):
            print(response.__dict__)
            print("-------------")
            print(response.request.body)
        else:
            print(f"Upload to development information successful!: {response.status_code}!")