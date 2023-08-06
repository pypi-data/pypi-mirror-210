# QUIP - Quick Universal Integration Development Tool

- [QUIP - Quick Universal Integration Development Tool](#quip---quick-universal-integration-development-tool)
  - [Description](#description)
  - [Setup](#setup)
    - [Troubleshooting](#troubleshooting)
    - [Sample Config](#sample-config)
  - [Help](#help)
  - [Universal Extension Operations](#universal-extension-operations)
    - [Create empty extension](#create-empty-extension)
    - [Bootstrap an extension](#bootstrap-an-extension)
    - [Clone existing extension](#clone-existing-extension)
    - [Update Existing Extension](#update-existing-extension)
    - [Delete an extension folder](#delete-an-extension-folder)
    - [Create ICON file](#create-icon-file)
  - [Universal Template Operations](#universal-template-operations)
    - [Create empty template](#create-empty-template)
    - [Bootstrap a Universal Template](#bootstrap-a-universal-template)
    - [Clone existing template](#clone-existing-template)
    - [Download a Universal Template](#download-a-universal-template)
    - [Upload Universal Template](#upload-universal-template)
    - [Update Existing Template](#update-existing-template)
    - [Delete a template folder](#delete-a-template-folder)
    - [Build an Universal Template](#build-an-universal-template)
  - [Create ICON file](#create-icon-file-1)
  - [Using different config file](#using-different-config-file)
  - [Display and update the version of the template/extension](#display-and-update-the-version-of-the-templateextension)
  - [Version Files configuration](#version-files-configuration)
  - [Updating Universal Template/Extesion Fields](#updating-universal-templateextesion-fields)
    - [Update Fields](#update-fields)
    - [Dump Fields](#dump-fields)
    - [Print Sample Code](#print-sample-code)
    - [Format of fields.yml file](#format-of-fieldsyml-file)

## Description
This tool is for rapid universal extension and universal template project creation. This tool is written on Python and can work on Windows or Linux platforms. 

All the configuration is located in .uip_config.yml file located on the script folder or home folder of the user or you can use a configuration by using --config option.

## Setup

* Install quip from pip
  ```
  pip install --upgrade quip-cli
  ```

* Check the version
  ```
  quip --version
  ```

* Check configuration
  ```
  quip config
  ```

* Set the path of the baseline projects to `source:` and `template_source:` fields in `.uip_config.yml` file. Folder paths must be full path not relative paths.
* Update the fields in the `.uip_config.yml` file

### Troubleshooting
* Contact: huseyin.gomleksizoglu@stonebranch.com for any questions.

### Sample Config

```yaml
defaults:     # Default values
  template: ue-task                     # default template for uip init command
  bootstrap:
    source: /projects/dev/ue/ue-baseline           # path of extension baseline project
    template_source: /projects/dev/ut/ut-baseline  # path of universal template baseline project
    exclude:                # folders that will be excluded for extension
      - .git
      - .uip
    template-exclude:       # folders that will be excluded for universal template
      - .git
    icon_font: cour.ttf       # Font for the default icon
    use_keyring: true         # Keep the passwords in OS level Keyring [Recommended]
    project_prefix: cs        # This keyword will be added to the folder name and repositories
external:
  gitlab:
    url: https://gitlab.stonebranch.com
    ssl_verify: false
    username: <username>
    default_group: cs-uac          # default group for new repositories
    groups:                        # List of repositories that can be used for new repositories
    - integration-prototypes
    - cs-uac
    protected_branch:             # information about protected branch
      name: main
      merge: DEVELOPER            # possible options are: 
      push: NO_ACCESS             # DEVELOPER, MAINTAINER, ADMIN, GUEST, NO_ACCESS, OWNER, REPORTER
    default_branch: develop       # Name of the default branch
    git-init: true                # it will run some git commands to initialize default branch
  jenkins:
    url: https://jenkins.stonebranch.com/
    ssl_verify: false
    username: <username>
    default_group: cs-uac
    groups:                     # Group mapping between GitLab and Jenkins
      integration-prototypes: integration-prototypes
      cs-uac: cs-uac
  sonarqube:
    url: https://sonarqube.stonebranch.com
    username: <username>
    use_token: true            # Use Username/Password or Token
    ssl_verify: false
    groups:                   # Group mapping between Jenkins and SonarQube
      cs-uac: cs-uac
extension.yml:              # default values for extension.yml
  extension:
    name: ""
    version: "1.0.0"
    api_level: "1.2.0"
    requires_python: ">=3.7"
  owner:
    name: Developer Name
    organization: Stonebranch Inc.
  comments: Created using ue-task template
uip.yml:                    # dafault values for .uip/config/uip.yml
  userid: ops.admin
  url: http://localhost:8090/uc
```

## Help
```
quip --help
```

```
======= QUIP (v.1.7.0-BETA) =======
usage: quip [-h] [--version] [--config CONFIG] [--debug] {new,update,u,up,fields,f,fi,delete,d,del,clone,c,cl,copy,bootstrap,bs,boot,bst,baseline,upload,push,download,pull,build,b,dist,zip,icon,resize-icon,ri,resize,clean,clear,setup,version,config} ...

Wrapper for UIP command.

positional arguments:
  {new,update,u,up,fields,f,fi,delete,d,del,clone,c,cl,copy,bootstrap,bs,boot,bst,baseline,upload,push,download,pull,build,b,dist,zip,icon,resize-icon,ri,resize,clean,clear,setup,version,config}
    new                 Creates new integration
    update (u, up)      Updates existing integration
    fields (f, fi)      Updates or dumps template.json fields.
    delete (d, del)     Deletes the integration folder
    clone (c, cl, copy)
                        Clones existing integration with a new name
    bootstrap (bs, boot, bst, baseline)
                        Bootstrap new integration from baseline project
    upload (push)       Uploads the template to Universal Controller. (Template Only)
    download (pull)     Download the template from Universal Controller. (Template Only)
    build (b, dist, zip)
                        Builds a zip file to import to Universal Controller. (Template Only)
    icon (resize-icon, ri, resize)
                        Resize the images to 48x48 in src/templates/
    clean (clear)       Clears the dist folders
    setup               Setup External Systems
    version             shows the version of the template/extension
    config              show the configuration

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --config CONFIG, -c CONFIG
                        path of the global config. Default is ~/.uip_config.yml
  --debug, -v           show debug logs
```

## Universal Extension Operations

### Create empty extension

```cmd
quip new ue-new-extension
```

### Bootstrap an extension

This command will 
* initialize a new extension 
* copy all files from ue-baseline project (except some folders)
* update the config files
* update the SysID of the template.json file
* create fields.yml file

```
quip bootstrap ue-bs-extension
```

### Clone existing extension

This command will 
* initialize a new extension 
* copy the `src` folder from the source project
* update the config files
* update the SysID of the template.json file

```
quip clone ue-cloned-extension ..\ue\ue-aws-m2
```

### Update Existing Extension

```
quip update ue-cloned-extension
``` 

To update the SysID values add --update-uuid (or -u) parameter
```
quip update ue-cloned-extension --uuid
``` 

To update the new_uuid values add --new-uuid (or -n) parameter. For any new object you can use a keyword like "new_uuid" as value and it will be automatically updated with this command.
```
quip update ue-cloned-extension --new-uuid
``` 

### Delete an extension folder
```
quip delete ue-cloned-extension
```

### Create ICON file
This command will find all the image files under `src/templates/` folder (it will ignore template_icon.png and any file that ends with "_48x48.png") and convert them to 48x48 size PNG files. quip will create new files with name *_48x48.png for each image file. If there is only one image file than it will also update the template_icon.png file.

```
quip icon
```

If you don't have any image file, you can also create one by using `--generate` parameter.

## Universal Template Operations

### Create empty template

```cmd
quip new ue-new-extension
```
### Bootstrap a Universal Template

This command will 
* copy all files from ut-baseline project (except some folders)
* update the config files
* update the SysID of the template.json file
* Upload the new template to controller
* create fields.yml file

```
quip bootstrap ut-bs-extension --template
```

### Clone existing template

This command will 
* initialize a new template
* copy the `src` folder from the source project
* update the config files
* update the SysID of the template.json file
* create fields.yml file
  
```
quip clone ut-cloned-extension ..\ue\ut-aws-m2 --template
```

### Download a Universal Template

This command will download the template.json, script files and ICON of the template.

This command will
* if the folder does not exists
  * bootstrap a new universal template
* download the teplate zip
* extract template.json and template_icon.png from zip
* create script files
* create fields.yml file
  
```
quip download Snowflake --template
```

### Upload Universal Template

This command will not update the Universal Template and the ICON.

```
quip upload Snowflake --template
```

### Update Existing Template

```
quip update ut-cloned-extension
``` 

To update the SysID values add --update-uuid (or -u) parameter
```
quip update ut-cloned-extension --uuid
``` 

To update the new_uuid values add --new-uuid (or -n) parameter. For any new object you can use a keyword like "new_uuid" as value and it will be automatically updated with this command.
```
quip update ut-cloned-extension --new-uuid
``` 


### Delete a template folder
```
quip delete ut-cloned-extension
```

### Build an Universal Template

This command will create a zip file for universal templates. This command will not work for universal extensions because `uip build` command already has this function.

The zip file will be created under `build` folder.

```
quip build ut-databricks -t
```

## Create ICON file
This command will find all the image files under `src/templates/` folder (it will ignore template_icon.png and any file that ends with "_48x48.png") and convert them to 48x48 size PNG files. quip will create new files with name *_48x48.png for each image file. If there is only one image file than it will also update the template_icon.png file.

```
quip icon
```

If you don't have any image file, you can also create one by using `--generate` parameter.

## Using different config file

You can use `--config` option to select the config file you want to use. This option will allow to use different controllers while downloading or uploading or using different baseline projects based on the project you will create. For example in the following example, quip will download Snowflake universal template from Atlanta Controller.
```
quip download Snowflake --template --config ~/.uip_config_atlanta.yml
```

## Display and update the version of the template/extension

This command will look for multiple files and will try to find the version information. It will show the versions in the files and also will display the possible new versions.

```
quip version
```

You can update the version by using 3 different update level: minor, major or release. Minor will update the last part of the version, major will update the middle value and release will update the first value. For example if the current version is 5.22.0, these are the possible next versions;

``` 
RELEASE:  6.0.0
MAJOR:  5.23.0
MINOR:  5.22.1
```

To update the version you can use this command.

```
quip version minor
```

if you want to change the version to a specific value, you can use the `--force` option. For example the following command will change the version to 5.22.4

```
quip version --force 5.22.4
```

If you have different version in the different files, in this case you can also use `--force` option to update them to a specific version. If there are multiple versions you can not use minor, major or release options. 

## Version Files configuration

By default `quip` will check the following files.
* src/extension.yml
* script.yml
* src/extension.py
* src/__init__.py
* src/templates/script*

You can change this configuration in your `.uip_config.yml` file. Here is a sample configuration. Quip will use the default configuration if you don't have any configuration in the config. 

```yaml
defaults:     # Default values
  template: ue-task                     # default template for uip init command
  bootstrap:
    source: /Users/HuseyinGomleksizoglu/SE_Projects/dev/ue/ue-baseline           # path of extension baseline project
    template_source: /Users/HuseyinGomleksizoglu/SE_Projects/dev/ut/ut-baseline  # path of universal template baseline project
    exclude:                # folders that will be excluded for extension
      - .git
      - .uip
    template-exclude:       # folders that will be excluded for universal template
      - .git
extension.yml:              # default values for extension.yml
  extension:
    name: ""
    version: "1.0.0"
    api_level: "1.2.0"
    requires_python: ">=3.7"
  owner:
    name: Huseyin Gomleksizoglu
    organization: Stonebranch Inc.
  comments: Created using ue-task template
uip.yml:                    # dafault values for .uip/config/uip.yml
  userid: ops.admin
  url: http://localhost:8090/uc
version_files:
- file: "src/extension.yml"
  format: "yml"
  location: "extension.version"
- file: "script.yml"
  format: "yml"
  location: "script.version"
- file: "src/extension.py"
  format: "regex"
  location: "^\\s*(gl_version|version|__version__)\\s*=\\s*[\\\"']+([^\\\"']+)[\\\"']+"
  group: 2
- file: "src/__init__.py"
  format: "regex"
  location: "^\\s*(gl_version|version|__version__)\\s*=\\s*[\\\"']+([^\\\"']+)[\\\"']+"
  group: 2
- file: "src/templates/script*"
  format: "regex"
  location: "^\\s*(gl_version|version|__version__)\\s*=\\s*[\\\"']+([^\\\"']+)[\\\"']+"
  group: 2
- file: "quip/__init__.py"
  format: "regex"
  location: "^\\s*(gl_version|version|__version__)\\s*=\\s*[\\\"']+([^\\\"']+)[\\\"']+"
  group: 2
- file: src/templates/template.json
  format: "regex"
  location: "\"description\"\\s*:\\s*\"v([\\d\\.]+)"
  group: 1
```

You can also use different configuration files if needed.

```
quip -c ~/.uip_config_sample.yml version
```

## Updating Universal Template/Extesion Fields

quip will automatically create a file called `fields.yml` on the root of the project folder. This will will have yaml representation of the fields. You can modify this file and update the template.json file with the new values.

### Update Fields

This command will
* Convert the yaml file into json format
* Update the template.json file
* Dump the new fields back to fields.yml file to add the Field Mapping values

``` quip fields --update ```

### Dump Fields

This command will convert the fields information from template.json file and create/update fields.yml file.

``` quip fields --dump ```

### Print Sample Code

This command will print some sample code to assign the fields or define dynamic choice fields.

``` quip fields --update --code```

Output: 

```
self.action = fields.get("action", [None])[0]
self.credentials = { "user": fields.get("credentials.user", None), "password": fields.get("credentials.password", None) }
self.end_point = fields.get("end_point", None)
self.region = fields.get("region", None)
self.application = fields.get("application", [None])[0]
self.batch_format = fields.get("batch_format", [None])[0]
self.jcl_file_name = fields.get("jcl_file_name", None)
self.jcl_file_path = fields.get("jcl_file_path", None)
self.script_name = fields.get("script_name", None)
self.jcl_file_name_temp = fields.get("jcl_file_name_temp", None)
self.application_id = fields.get("application_id", None)
self.batch_execution_id = fields.get("batch_execution_id", None)
self.step_name = fields.get("step_name", None)
self.procstep_name = fields.get("procstep_name", None)
self.templib = fields.get("templib", None)
self.parameters = fields.get("parameters", None)

@dynamic_choice_command("application")
def get_application(self, fields):
    _fields = []
    return ExtensionResult(
    rc = 0,
    message = "Available Fields: '{}'".format(_fields),
    values = _fields
    )
```

### Format of fields.yml file

A simple file will look like this.

```yaml
name: AWS Mainframe Modernization
template_type: Extension
agent_type: Any
description: AWS M2 - Mainframe Modernization
extension: aws-m2
min_release: 7.0.0.0
var_prefix: ext
sys_id: fb7fc3a05eac4d57a74fe1b1342b3938
fields:

- action: Choice
  hint: Select the action you want to run
  start: true
  field_mapping: Choice Field 1
  items:
  - list-environments
  - list-applications
  - start-batch
  - sync-start-batch

- credentials: Credential
  hint: Put Access key to Runtime User and Secret Key to Password fields
  label: AWS Credentials
  end: true
  field_mapping: Credential Field 1

- end_point: Text
  hint: This field is optional. If you don't put the value it will be generated by
    using the region value.
  start: true
  default: https://m2.us-east-1.amazonaws.com
  field_mapping: Text Field 4

- application: Choice
  hint: Application will be retrieved from AWS automatically
  span: 2
  dynamic: true
  field_mapping: Choice Field 2
  items: []
  dependencies:
  - end_point
  - region
  - credentials
  show_if:
    action: start-batch,sync-start-batch

- application_id: Text
  start: true
  restriction: Output Only
  field_mapping: Text Field 1
  show_if:
    action: start-batch,sync-start-batch

- parameters: Array
  start: true
  name_title: Parameter Name
  value_title: Parameter Value
  field_mapping: Array Field 1
  span: 2

```

Format of the child elements are like this.

* First value will be the name of the field and the value of that element will be the type of the field.
* Field Types can be one of these items
    * Text
    * Large Text (aliases: large, largetext, textarea, text area)
    * Integer
    * Boolean (aliases: bool, check, checkbox, check box)
    * Choice (aliases: items, select, option, options, list)
    * Credential (aliases: creds, cred, credentials)
    * Script
    * Array (aliases: grid)
    * Float
* Other Fields:
    * label: By default field name will be converted as a label but if you want to overwrite that value you can use that field
    * hint: The hint message of the field
    * field_mapping: This is the mapping for the database fields. If this value is missing, quip will automatically assign the next available field. It is safe to not provide this value for new extension/template. The assigned values will be automatically added to the file.
    * default: If there is a default value, you can use that field. 
    * required: If the field is required, you can use that field. Default: false
    * start: If you want the field to be in the left side of the row, set value to true. Default: false
    * end: If you want the field to be on the right side of the row, set value to true. Default: false
    * span: If you want the field to fill the row set value to 2. Default: 1
    * text_type: If the text field has YAML or JSON content, set value to YAML or JSON. Default: Plain
    * dynamic: If the field is a dynamic choice field, set the value to true. Default: false
    * restriction: If the field has restrictions like output only, set the value to "Output Only". Default: No Restriction
    * name_title: This field is only for Array types. This field is the label of the first field.
    * value_title: This field is only for Array types. This field is the label of the second field.
    * titles: (alias: headers) This field is another representation of the name_title and value_title fields. You can set the name and value field title in a comma seperated string. For example: `titles: Field Name, Field Value`
    * allow_multiple: This field is only for Choice types. To allow selecting multiple values, set value to true. Default: false
    * allow_empty: This field is only for Choice types. To allow not selecting any value, set value to true. Default: false
    * length: Sets the max lenght of the field.
    * max: Sets the maximum allowed number for that field.
    * min: Set the minimum allowed number for that field.
    
    ### items
    This field is required for Choice type. This field will include the items of the choice field. Items can be a simple string without a space and it will be used as the name of the item and label will be generated from the names. If you want to give a specific label, in this case set it like this. `- use_ssl: Use SSL`

    ```yaml
      - action: Choice
        hint: Select the action you want to run
        start: true
        field_mapping: Choice Field 1
        items:
        - list-environments
        - list-applications
        - start-batch
        - sync-start-batch: Start Batch and Wait
    ```

    ### Dependencies
    This field is only for dynamic choice fields. This field will include the list of dependencies of the the dynamic choice field. Dependencies will be the list of field names.

    ```yaml
      - application: Choice
        hint: Application will be retrieved from AWS automatically
        span: 2
        dynamic: true
        field_mapping: Choice Field 2
        items: []
        dependencies:
        - end_point
        - region
        - credentials
    ```

    ### Show If
    If the field will be displayed based on another field, in this case you can use the `show_if` option. First element will be name of the dependent field and value of the element will be the condition. If the field will be required if it is visible, than `required: true` option must be added.

    The following example will show the `application_id` field if the `action` field is `start-batch` or `sync-start-batch`
    ```yaml
      - application_id: Text
        start: true
        restriction: Output Only
        field_mapping: Text Field 1
        show_if:
          action: start-batch,sync-start-batch
    ```
    Other options:
    * required: If the field will be required if visible, set the value to true.
    * no_space: If the field will not reserve any space if hidden, set the value to false. Default: true
    * preserve_value: The value of this field will be stored even the field is not visible. Default: false

    ### Require If
    If the field will be required based on another field, in this case you can use the `require_if` option. First element will be name of the dependent field and value of the element will be the condition.

    ```yaml
      - task_name: Text
        start: true
        field_mapping: Text Field 1
        require_if:
          action: start-batch,sync-start-batch
    ```

    ### Raw Values
    Some of the options not implemented in quip because they are not common options. For these options you can use the `raw:` option. This item will include the list of items and values of them.

    ```yaml
      - backup_folder: Text
        field_mapping: Text Field 6
        show_if:
          backup: true
          required: true
        raw:
          preserveOutputOnRerun: true
    ```

    List of raw options:
    * booleanNoValue
    * booleanValueType
    * booleanYesValue
    * choiceSortOption
    * defaultListView
    * preserveOutputOnRerun


## Setup External Systems

Quip will automatically create Repositories or Jobs in external systems. The main purpose is to have GitLab Repository, Jenkins Job, SonarQube Project and WebHook configuration between GitLab and Jenkins.

``` quip setup ```

The output of the command will be similar to that one.

```
======= QUIP (v.1.7.0-BETA) =======
Namespace(action='setup', config=None, debug=False, sonarqube=False, name=None)
INFO:root:Reading template.json file
INFO:root:Project name: ue-AWS Mainframe Modernization
INFO:root:Using config from file : C:\Users\HuseyinGomleksizoglu\.uip_config.yml

==== GITLAB SETUP ====
There is a saved password. To used the saved password just press [Enter]
Please enter Personal Access Key:
Do you want to create Gitlab repository?(Y/n): 
INFO:root:Creating GitLab Repository.
Gitlab Groups
=============
(1) cs-uac
(2) integration-prototypes
(3) uac-extensions
(4) uac-extensions/community
(5) uac-extensions/onboarding
(6) uac-extensions/universal-extensions-frameworks
Choose one (1-6) [1]:  1
INFO:root:Checking GitLab if the repository exists.
Repository created cs-uac/ue-aws-mainframe-modernization
Run `git init`
Run `git remote add origin https://gitlab.stonebranch.com/cs-uac/ue-aws-mainframe-modernization.git`

==== JENKINS SETUP ====
INFO:root:Connecting to Jenkins Server.
There is a saved password. To used the saved password just press [Enter]
Please enter Jenkins Password for (h.gomleksizoglu):
INFO:root:Repository doesn't exist and will be created. cs-uac/ue-aws-mainframe-modernization
Do you want to create Jenkins pipeline?(Y/n):

==== SONARQUBE SETUP ====
Do you want to create SonarQube projects?(Y/n):
There is a saved password. To used the saved password just press [Enter]
Please enter Personal Access Key:
INFO:root:URL = https://sonarqube.stonebranch.com/api/projects/create?project=cs-uac-ue-aws-mainframe-modernization&name=cs-uac-ue-aws-mainframe-modernization
SonarQube project created: cs-uac-ue-aws-mainframe-modernization
INFO:root:URL = https://sonarqube.stonebranch.com/api/qualitygates/select?gateName=CS UAC and Community QG&projectKey=cs-uac-ue-aws-mainframe-modernization
SonarQube Quality Gate changed.
```

### GitLab Setup
The processing logic of `quip` is like this
* Check if there is .git/config file. 
  * If so, 
    * check the repository name of remote system with name `origin`
    * Check if the repository exists in GitLab
  * If not create the repository
* Ask for new repository group. It will list the group from GitLab system.
* Check if there is a repository already exists in GitLab
  * If so,
    * Print information how to add a remote system
  * If not create the repository

### Jenkins Setup
The processing logic of `quip` is like this
* Map the GitLab group to group in Jenkins. This will be importan if the group names are different GitLab and Jenkins.
* Check if Jenkin Job exists
* If not,
  * Create the Jenkins Job. Job will be created with some default values. They are hard coded for now. Planning to have configuration in future.
  * Create WebHook from GitLab to Jenkins Job for any Push, Merge Request and Comment event.

### SonarQube Setup
The processing logic of `quip` is like this
* Check if there is a mapping for the Jenkins Group
* If so,
  * Create the Project if it doesn't exists
  * Update Security Gate of the Project
* If not,
  * No need to create SonarQube project for that group