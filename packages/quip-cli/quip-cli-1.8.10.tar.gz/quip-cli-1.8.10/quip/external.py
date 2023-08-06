import sys
import os
from quip import cprint, yes_or_no
import json
import logging
import requests
import gitlab
import jenkins
import configparser
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_git_info(git_config, remote):
    config = configparser.ConfigParser()
    config.read(git_config)
    try:
        # expected format of the URLs are like this
        # git@gitlab.stonebranch.com:integration-prototypes/ue-talend-cloud.git
        # https://gitlab.stonebranch.com/integration-prototypes/ue-talend-cloud.git
        if "remote \"origin\"" in config.sections():
            url = config[f'remote "{remote}"']['url']
            if url.startswith("git@"):
                matches = re.match(string=url, pattern=r"git@[^:]+:([\w\-\/]+).git")
                repository_name = matches[1]
            else:
                matches = re.match(string=url, pattern=r"http[s]{0,1}:\/\/[^\/]+\/([\w\-\/]+).git")
                repository_name = matches[1]
            
            return repository_name
    except TypeError:
        cprint("There is a problem with the .git/config file. Be sure that git remote origin is correct.", "red")
        cprint("To remove the git origin use the following command", "red")
        cprint("git remote remove origin", "yellow")

    return None
    

def parse_repository_full_path(repository_name, groups, group_mapping):
    result = repository = ""
    for group in groups:
        if isinstance(group, str):
            group_path = group
        elif isinstance(group, dict):
            group_path = list(group.keys())[0]
            # group_path = list(group.values())[0]
        if repository_name.startswith(group_path):
            # get the most matched group
            if len(group_path) > len(result):
                result = group_path
                repository = repository_name[len(result)+1:]
    
    logging.debug(f"Group found: {result}")
    if result in group_mapping:
        result = group_mapping.get(result)
        logging.debug(f"Group found in config: {result}")
    
    if len(result) > 0:
        return result, repository
    else:
        return None, repository_name

class HtttpClient():
    def __init__(self, base_url, credentials, ssl_verify=False, resource_prefix="/") -> None:
        self.log = logging
        logging.basicConfig(level="DEBUG", format=' %(asctime)s - %(levelname)s - %(message)s')

        self.base_url = base_url.rstrip(" /") # clean end of the url
        self.credentials = credentials
        self.ssl_verify = ssl_verify
        if not resource_prefix.startswith("/"):
            resource_prefix = "/" + resource_prefix
        self.resource_prefix = resource_prefix

    def post(self, resource, query="", json_data=None):
        return self.call("POST", resource, query, json_data)

    def put(self, resource, query="", json_data=None):
        return self.call("PUT", resource, query, json_data)

    def get(self, resource, query=""):
        return self.call("GET", resource, query, json_data=None)

    def delete(self, resource, query="", json_data=None):
        return self.call("DELETE", resource, query, json_data)

    def call(self, method, resource, query, json_data):
        self.log.debug("rest_call start")
        headers = {"content-type": "application/json", "Accept": "application/json"}
        if len(query) > 0:
            query = "?" + "&".join(query)
        uri = f"{self.base_url}{self.resource_prefix}{resource}{query}"
        self.log.info(f"URL = {uri}")
        try:
            if method == "GET":
                response = requests.get(uri,
                                        headers=headers,
                                        auth=self.credentials,
                                        verify=self.ssl_verify)
            elif method == "POST":
                response = requests.post(uri,
                                        headers=headers,
                                        json=json_data,
                                        auth=self.credentials,
                                        verify=self.ssl_verify)
            elif method == "DELETE":
                response = requests.delete(uri,
                                        headers=headers,
                                        json=json_data,
                                        auth=self.credentials,
                                        verify=self.ssl_verify)
            elif method == "PUT":
                response = requests.put(uri,
                                        headers=headers,
                                        json=json_data,
                                        auth=self.credentials,
                                        verify=self.ssl_verify)
            else:
                self.log.error(f"Unknown method {method}")
                raise
        except Exception as unknown_exception:
            self.log.error(f"Error Calling{self.base_url} API {sys.exc_info()}")
            raise

        return response

class SonarQube():
    def __init__(self, base_url, credentials, ssl_verify=False) -> None:
        self.log = logging
        logging.basicConfig(level="DEBUG", format=' %(asctime)s - %(levelname)s - %(message)s')

        self.base_url = base_url.rstrip(" /") # clean end of the url
        self.credentials = credentials
        self.ssl_verify = ssl_verify
        self.http = HtttpClient(base_url, credentials, ssl_verify, resource_prefix="/api")

    def create_project(self, name, quality_gate="CS UAC and Community QG"):
        # echo -e "INFO:Create sonarqube project:${PROJECT} "
        # curl  --request   GET -k --fail -u squ_39bb405492e9cacc02b9c84f4eae90d3d66b5807: "https://sonarqube.stonebranch.com/api/projects?project=${PROJECT}&name=${PROJECT}"
        # echo $?

        # echo -e "INFO:Assign Quality gate"
        # curl --request   POST -k --fail -u aakeykey: "https://sonarqube.stonebranch.com/api/qualitygates/select?gateName=CS%20UAC%20and%20Community%20QG&projectKey=${PROJECT}"
        # echo $?
        try:
            response = self.http.post(resource="/projects/create", query=[f"project={name}", f"name={name}"])
        except Exception as e:
            self.log.error(f"Failed with reason : {e}")
        if not response.ok:
            #_json = json.loads(response.text)
            self.log.error(f"Response: {response.text}")
            if "key already exists:" not in response.text:
                return False
            else:
                cprint(f"SonarQube project already exists: {name}", "yellow")
        else:
            cprint(f"SonarQube project created: {name}", "green")

        try:
            response = self.http.post(resource="/qualitygates/select", query=[f"gateName={quality_gate}", f"projectKey={name}"])
        except Exception as e:
            self.log.error(f"Failed with reason : {e}")
        if not response.ok:
            #_json = json.loads(response.text)
            self.log.error(f"Response: {response.text}")
            return False
        else:
            cprint(f"SonarQube Quality Gate changed.", "green")
        
        return True


class GitLab():
    def __init__(self, base_url, token, ssl_verify=False, default_group=None) -> None:
        self.log = logging
        logging.basicConfig(level="DEBUG", format=' %(asctime)s - %(levelname)s - %(message)s')

        self.base_url = base_url.rstrip(" /") # clean end of the url
        self.default_group = default_group
        self.gl = gitlab.Gitlab(url=self.base_url, private_token=token, ssl_verify=ssl_verify, per_page=100)
        self.project_id = None
        self.project = None
        self.default_branch = None
        self.repository_name = None
        
    def get_groups(self, summary=True):
        groups = self.gl.groups.list(order_by="path", sort="asc")
        if summary:
            result = []
            for group in groups:
                result.append((group.full_path, group.id))
        
            return result
        
        return groups

    def get_group_projects(self, group_id, summary=True):
        group = self.gl.groups.get(group_id)
        projects = group.projects.list()
        if summary:
            result = []
            for project in projects:
                result.append((project.path_with_namespace, project.id))
            
            return result
        
        return projects
    
    def get_projects(self, summary=True):
        projects = self.gl.projects.list(get_all=True)
        if summary:
            result = []
            for project in projects:
                result.append((project.path_with_namespace, project.id))
            
            return result
        
        return projects

    def create_project(self, name, group_id, config=None):
        self.log.info(f"Creating repository name={name} namespace={group_id}")
        self.project = self.gl.projects.create({"name": name, "namespace_id": group_id})
        if config is not None:
            if "protected_branch" in config:
                self.log.info("Creating protected branch for the repository.")
                protected_branch = config.get("protected_branch", None)
                if protected_branch is not None:
                    result = self.create_protected_branch(protected_branch)
                    if result is False:
                        cprint("Failed to create projected branch", "red")
            
            if "default_branch" in config:
                branch_name = config.get("default_branch", None)
                if branch_name is not None:
                    self.default_branch = branch_name
                    self.log.info(f"Creating default branch {branch_name}.")
                    self.project.branches.create({ "branch": branch_name, "ref": "main" })
    
    def create_webhook(self, jenkins_url):
        if self.project is None:
            if self.project_id is not None:
                self.project = self.gl.projects.get(self.project_id)
        
        if self.project is None:
            self.log.error("GitLab Project not found.")
            return False
        
        hooks = self.project.hooks.list()
        for hook in hooks:
            if hook.url == jenkins_url:
                self.log.warning("GitLab Hook for that URL is already exists.")
                return False
        
        self.hook = self.project.hooks.create({"url": jenkins_url, "push_events": True, "merge_requests_events": True, "enable_ssl_verification": True, "note_events": True, "token":"e88b637a31ca6ec4f107bb54a716d2c9"})
        return True
    
    def create_badge(self, jenkins_url, jenkins_base_url, jnks_group_name, jnks_repository_name):
        if self.project is None:
            if self.project_id is not None:
                self.project = self.gl.projects.get(self.project_id)
        
        if self.project is None:
            self.log.error("GitLab Project not found.")
            return False
        
        link_url = jenkins_url + "/lastBuild/"
        image_url = f"{jenkins_base_url}/buildStatus/icon?subject=jenkins&job={jnks_group_name}%2F{jnks_repository_name}"
        badges = self.project.badges.list()
        for badge in badges:
            if badge.link_url == link_url:
                self.log.warning("GitLab Badge for that URL is already exists.")
                return False
        
        self.badge = self.project.badges.create({'link_url': link_url, 'image_url': image_url})
        return True
    
    def create_protected_branch(self, protected_branch):
        branch_name = protected_branch.get("name", None)
        if branch_name is None:
            cprint("Protected branch name is missing!", "red")
            return False
        
        gitlab_access_level = {
            "DEVELOPER": gitlab.const.AccessLevel.DEVELOPER,
            "MAINTAINER": gitlab.const.AccessLevel.MAINTAINER,
            "ADMIN": gitlab.const.AccessLevel.ADMIN,
            "GUEST": gitlab.const.AccessLevel.GUEST,
            "NO_ACCESS": gitlab.const.AccessLevel.NO_ACCESS,
            "OWNER": gitlab.const.AccessLevel.OWNER,
            "REPORTER": gitlab.const.AccessLevel.REPORTER
        }
        merge_config = protected_branch.get("merge", "DEVELOPER")
        merge_level = gitlab_access_level[merge_config]

        push_config = protected_branch.get("push", "MAINTAINER")
        push_level = gitlab_access_level[push_config]

        self.project.protectedbranches.create({
            'name': branch_name,
            'merge_access_level': merge_level,
            'push_access_level': push_level
        })

        return True


class Jenkins():
    def __init__(self, base_url, credentials, ssl_verify=False) -> None:
        self.log = logging
        logging.basicConfig(level="DEBUG", format=' %(asctime)s - %(levelname)s - %(message)s')

        self.base_url = base_url.rstrip(" /") # clean end of the url
        self.credentials = credentials
        self.job_url = None
        self.job = None
        if not ssl_verify:
            os.environ["PYTHONHTTPSVERIFY"] = "0"

        self.jnks = jenkins.Jenkins(self.base_url, username=credentials[0], password=credentials[1])

    def check_job_exists(self, group_name, repository_name):
        job_name = f"{group_name}/{repository_name}"
        if self.jnks.job_exists(job_name):
            return True
        
        return False
    
    def get_url(self, group_name, repository_name):
        return f"{self.base_url}/project/{group_name}/{repository_name}"

    def create_job(self, group_name, repository_name, description, gitlab_url, gitlab_repository_name, jenkins_credential):
        repository_full_name = f"{group_name}/{repository_name}"
        config = self.get_default_job_config(gitlab_url, group_name, repository_name, description, gitlab_repository_name, jenkins_credential)
        self.jnks.create_job(repository_full_name, config)

    def get_default_job_config(self, gitlab_url, group_name, repository_name, description, gitlab_repository_name, jenkins_credential):
        DEFAULT_CONFIG = """<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.42">
  <actions>
    <org.jenkinsci.plugins.pipeline.modeldefinition.actions.DeclarativeJobAction plugin="pipeline-model-definition@1.9.2"/>
    <org.jenkinsci.plugins.pipeline.modeldefinition.actions.DeclarativeJobPropertyTrackerAction plugin="pipeline-model-definition@1.9.2">
      <jobProperties/>
      <triggers/>
      <parameters/>
      <options/>
    </org.jenkinsci.plugins.pipeline.modeldefinition.actions.DeclarativeJobPropertyTrackerAction>
  </actions>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <org.jenkinsci.plugins.workflow.job.properties.DisableConcurrentBuildsJobProperty>
      <abortPrevious>false</abortPrevious>
    </org.jenkinsci.plugins.workflow.job.properties.DisableConcurrentBuildsJobProperty>
    <com.coravy.hudson.plugins.github.GithubProjectProperty plugin="github@1.33.1">
      <projectUrl>{gitlab_url}/{repository}/</projectUrl>
      <displayName></displayName>
    </com.coravy.hudson.plugins.github.GithubProjectProperty>
    <com.dabsquared.gitlabjenkins.connection.GitLabConnectionProperty plugin="gitlab-plugin@1.5.22">
      <gitLabConnection>jenkins@gitlab</gitLabConnection>
      <jobCredentialId>cs_jenkins_gitlab</jobCredentialId>
      <useAlternativeCredential>true</useAlternativeCredential>
    </com.dabsquared.gitlabjenkins.connection.GitLabConnectionProperty>
    <org.jenkinsci.plugins.gitlablogo.GitlabLogoProperty plugin="gitlab-logo@1.0.5">
      <repositoryName>{repository}</repositoryName>
    </org.jenkinsci.plugins.gitlablogo.GitlabLogoProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.StringParameterDefinition>
          <name>SourceBranch</name>
          <description>Gitlab branch to build.</description>
          <defaultValue>$gitlabSourceBranch</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>SourceRepoHomepage</name>
          <description>{gitlab_url}/{repository}</description>
          <defaultValue>$gitlabSourceRepoHomepage</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>DeployOnSendSafely</name>
          <description>Flag to indicate whether the built package will be deployed on Send Safely.
    Should only be set to true for final build on main branch.</description>
          <defaultValue>false</defaultValue>
        </hudson.model.BooleanParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
    <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
      <triggers>
        <com.dabsquared.gitlabjenkins.GitLabPushTrigger plugin="gitlab-plugin@1.5.22">
          <spec></spec>
          <triggerOnPush>true</triggerOnPush>
          <triggerToBranchDeleteRequest>false</triggerToBranchDeleteRequest>
          <triggerOnMergeRequest>true</triggerOnMergeRequest>
          <triggerOnlyIfNewCommitsPushed>true</triggerOnlyIfNewCommitsPushed>
          <triggerOnPipelineEvent>false</triggerOnPipelineEvent>
          <triggerOnAcceptedMergeRequest>false</triggerOnAcceptedMergeRequest>
          <triggerOnClosedMergeRequest>false</triggerOnClosedMergeRequest>
          <triggerOnApprovedMergeRequest>false</triggerOnApprovedMergeRequest>
          <triggerOpenMergeRequestOnPush>never</triggerOpenMergeRequestOnPush>
          <triggerOnNoteRequest>true</triggerOnNoteRequest>
          <noteRegex>Jenkins please retry a build</noteRegex>
          <ciSkip>true</ciSkip>
          <skipWorkInProgressMergeRequest>true</skipWorkInProgressMergeRequest>
          <labelsThatForcesBuildIfAdded></labelsThatForcesBuildIfAdded>
          <setBuildDescription>true</setBuildDescription>
          <branchFilterType>All</branchFilterType>
          <includeBranchesSpec></includeBranchesSpec>
          <excludeBranchesSpec></excludeBranchesSpec>
          <sourceBranchRegex></sourceBranchRegex>
          <targetBranchRegex></targetBranchRegex>
          <secretToken>{token}</secretToken>
          <pendingBuildName></pendingBuildName>
          <cancelPendingBuildsOnUpdate>false</cancelPendingBuildsOnUpdate>
        </com.dabsquared.gitlabjenkins.GitLabPushTrigger>
      </triggers>
    </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.94">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@4.9.0">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>{gitlab_url}/{repository}.git</url>
          <credentialsId>{credential}</credentialsId>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>origin/$SourceBranch</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <browser class="hudson.plugins.git.browser.GitLab">
        <url>{gitlab_url}/{repository}</url>
        <version>14.0</version>
      </browser>
      <submoduleCfg class="empty-list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""
        return DEFAULT_CONFIG.format(
            repository=gitlab_repository_name,
            description=description,
            token="{AQAAABAAAAAwn0PMV7WTFCnRSkwbTfvm7603mkro7e+5PvP0NTkPaQIr4W1q6U2c6FvDwBq3Uq+PV3zDPI4vRD+YohxEdVgxRg==}",
            gitlab_url=gitlab_url,
            credential=jenkins_credential)