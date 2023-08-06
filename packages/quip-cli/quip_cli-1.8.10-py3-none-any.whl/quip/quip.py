#!/usr/bin/env python3
# Author  : Huseyin Gomleksizoglu
# Date    : "26-May-2022"
# Version : quip.py: 20220526
#
# 1.0.0     Huseyin G.    Jun/2/2022    Icon feature added, build option added
#
# Copyright (c) Stonebranch Inc, 2019.  All rights reserved.


import argparse
import os, sys
import yaml
import shutil
import subprocess
import json
import uuid
import re
import logging
from distutils.dir_util import copy_tree
from getpass import getpass
import requests
from shutil import make_archive, unpack_archive, move
import tempfile
from datetime import datetime
import quip.field_builder as fb
import quip.version_builder as vb
import quip.external as external
from argparse import RawTextHelpFormatter
from quip import __version__, yes_or_no, cprint, choose_one, color_text
import keyring
import platform

version = __version__
UPDATE_ACTION = ["update", "u", "up"]
FIELD_ACTION = ["fields", "f", "fi"]
ICON_ACTION = ["icon", "resize-icon", "ri", "resize"]
DELETE_ACTION = ["delete", "d", "del"]
CLONE_ACTION = ["clone", "c", "cl", "copy"]
BOOTSTRAP_ACTION = ["bootstrap", "bs", "boot", "bst", "baseline"]
DOWNLOAD_ACTION = ["download", "pull"]
UPLOAD_ACTION = ["upload", "push"]
BUILD_ACTION = ["build", "b", "dist", "zip"]
CLEAN_ACTION = ["clean", "clear"]

class Quip:
    def __init__(self, log_level=logging.INFO) -> None:
        cprint(f"======= QUIP (v.{version}-BETA) =======", color="cyan")
        logging.basicConfig(level=log_level)
        self.in_project_folder = False
        self.args = self.parse_arguments()
        self.set_global_configs(self.args.name, self.args.config)

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Wrapper for UIP command.', formatter_class=RawTextHelpFormatter)
        parser.add_argument('--version', action='version', version=f'quip {version}-BETA')
        subparsers = parser.add_subparsers(dest='action')
        parser.add_argument('--config', '-c', default=None,
                             help='path of the global config. Default is ~/.uip_config.yml')
        parser.add_argument('--debug', '-v', action='store_true',
                            help='show debug logs')

        parser_new = subparsers.add_parser('new', help='Creates new integration')
        parser_new.add_argument('name', help='name of the project')
        parser_new.add_argument('--template', '-t', action='store_true',
                             help='create template instead of extension')

        parser_update = subparsers.add_parser('update', aliases=UPDATE_ACTION[1:], help='Updates existing integration')
        parser_update.add_argument('name', nargs="?", help='name of the project')
        parser_update.add_argument('--uuid', '-u', action='store_true',
                             help='Update UUID of the template')
        parser_update.add_argument('--new-uuid', '-n', action='store_true',
                             help='Update only new_uuid with a valid UUID in the template')
        parser_update.add_argument('--template', '-t', action='store_true',
                             help='create template instead of extension')
        parser_update.add_argument('--rename_scripts', action='store_true',
                             help='add .py extensions to script files.')
        
        parser_fields = subparsers.add_parser('fields', aliases=FIELD_ACTION[1:], help='Updates or dumps template.json fields.')
        parser_fields.add_argument('name', nargs="?", help='name of the project')
        parser_fields.add_argument('--update', '-u', action='store_true',
                             help='Update fields from fields.yml')
        parser_fields.add_argument('--dump', '-d', action='store_true',
                             help='dump fields to fields.yml')
        parser_fields.add_argument('--code', action='store_true',
                            help='Give some code samples')

        parser_delete = subparsers.add_parser('delete', aliases=DELETE_ACTION[1:], help='Deletes the integration folder')
        parser_delete.add_argument('name', help='name of the project')

        parser_clone = subparsers.add_parser('clone', aliases=CLONE_ACTION[1:], help='Clones existing integration with a new name')
        parser_clone.add_argument('name', help='name of the project')
        parser_clone.add_argument('source', help='source project path')
        parser_clone.add_argument('--template', '-t', action='store_true',
                             help='create template instead of extension')

        parser_bootstrap = subparsers.add_parser('bootstrap', aliases=BOOTSTRAP_ACTION[1:], help='Bootstrap new integration from baseline project')
        parser_bootstrap.add_argument('name', nargs="?", help='name of the project')
        parser_bootstrap.add_argument('--template', '-t', action='store_true',
                             help='create template instead of extension')

        parser_upload = subparsers.add_parser('upload', aliases=UPLOAD_ACTION[1:], help='Uploads the template to Universal Controller. (Template Only)')
        parser_upload.add_argument('name', nargs="?", help='name of the project')
        parser_upload.add_argument('--template', '-t', action='store_true',
                             help='create template instead of extension')

        parser_download = subparsers.add_parser('download', aliases=DOWNLOAD_ACTION[1:], help='Download the template from Universal Controller.')
        parser_download.add_argument('name', nargs="?", help='name of the project')
        parser_download.add_argument('--template', '-t', action='store_true',
                             help='create template instead of extension')

        parser_build = subparsers.add_parser('build', aliases=BUILD_ACTION[1:], help='Builds a zip file to import to Universal Controller. (Template Only)')
        parser_build.add_argument('name', nargs="?", help='name of the project')
        parser_build.add_argument('--template', '-t', action='store_true',
                             help='create template instead of extension')

        parser_icon = subparsers.add_parser('icon', aliases=ICON_ACTION[1:], help='Resize the images to 48x48 in src/templates/')
        parser_icon.add_argument('name', nargs="?", help='name of the project')
        parser_icon.add_argument('--generate', '-g', action='store_true',
                             help='generate new icon')

        parser_clean = subparsers.add_parser('clean', aliases=CLEAN_ACTION[1:], help='Clears the dist folders')
        parser_clean.add_argument('name', nargs="?", help='name of the project')
        parser_clean.add_argument('--macfilesonly', '-m', action='store_true',
                             help='Delete only MacOS Hidden files like ._* or .DS_Store')

        parser_setup = subparsers.add_parser('setup', help='Setup External Systems')
        parser_setup.add_argument('name', nargs="?", help='name of the project')

        parser_version = subparsers.add_parser('version', help='shows the version of the template/extension')
        parser_version.add_argument('version_method', nargs="?", choices=["minor", "major", "release", "beta", "rc"], help='update the version of the project. Options: beta,minor,major,release,rc.')
        parser_version.add_argument('--force', dest="forced_version", help='Force to change the version in all possible files')

        parser_config = subparsers.add_parser('config', help='show the configuration')

        args = parser.parse_args()
        print(args)
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        if args.action is None:
            parser.print_help()
            sys.exit(0)
        
        if args.action in ["config", "version"]:
            # give a fake name because name is mandatory
            args.name = ""
        
        if args.action in (["clean"] + CLEAN_ACTION):
            # Ignore project name to clean macfiles
            if args.macfilesonly:
                args.name = ""

        if args.name is None:
            current_folder = os.getcwd()
            template_path = os.path.join(current_folder, "src", "templates", "template.json")
            if os.path.exists(template_path):
                # args.name = os.path.basename(current_folder)
                _json = self.read_template_json(template_path=template_path)
                template = (_json["templateType"] == "Script")
                if template:
                    args.name = "ut-" + _json["name"]
                    args.template = True
                else:
                    args.name = "ue-" + _json["name"]
                logging.info(f"Project name: {args.name}")
                self.in_project_folder = True
            else:
                logging.error("You are not in a project folder. Please specify the project name.")
                sys.exit(1)

        if "template" not in dir(args):
            args.template = False
            logging.debug("No template keyword in args")
        elif args.template is False and args.name.startswith("ut-"):
            args.template = True
            logging.debug("Project is a template because name starts with UT")
        elif args.name.startswith("ue-"):
            args.template = False
            logging.debug("Project is an extension because name starts with UE")
        elif args.action in DOWNLOAD_ACTION and not self.in_project_folder:
            args.template = True
            logging.debug("Project is a template because download action executed with a name")
        
        logging.info(f"The project is template={args.template}")
        return args
    
    def main(self):
        action = self.args.action
        if action == "new":
            if self.args.template:
                logging.info("creating new template")
                self.new_template()
            else:
                self.new_project()
                self.dump_fields(write=True)
            self.create_icon_safe()
        elif action in ICON_ACTION:
            if self.args.generate:
                self.create_icon()
            else:
                self.update_icon()
        elif action in FIELD_ACTION:
            if self.args.dump:
                self.dump_fields(write=True)
            else:
                self.update_fields(self.args.code)
        elif action in UPDATE_ACTION:
            if self.args.rename_scripts:
                self.update_rename_scripts()
            else:
                self.update_project(self.args.uuid, self.args.new_uuid, new_project=False)
            self.dump_fields(write=True)
        elif action in DELETE_ACTION:
            self.delete_project()
        elif action in CLONE_ACTION:
            if self.args.template:
                exclude_list = self._global_conf_defaults.get("bootstrap", {}).get("template-exclude", None)
            else:
                exclude_list = self._global_conf_defaults.get("bootstrap", {}).get("exclude", None)
            self.clone_project(self.args.source, all_files=True, exclude_list=exclude_list)
            self.dump_fields(write=True)
        elif action in BOOTSTRAP_ACTION:
            if self.args.template:
                self.bootstrap_template()
            else:
                self.bootstrap_project()
            self.dump_fields(write=True)
            self.create_icon_safe()
        elif action in UPLOAD_ACTION:
            self.update_fields_if_needed()
            if not self.args.template:
                self.run_uip("push_all")
            else:
                self.upload_template()
        elif action in DOWNLOAD_ACTION:
            if not self.args.template:
                self.run_uip("pull")
            else:
                if os.path.exists(self.project_folder_name) or self.in_project_folder:
                    self.download_template()
                else:
                    self.bootstrap_template(ask_for_upload=False)
                    self.download_template()
            self.dump_fields(write=True)
        elif action == "build":
            self.update_fields_if_needed()
            if self.args.template:
                self.build_zip(self.project_name)
            else:
                self.run_uip("build")
                self.curr_version = vb.find_current_version(version_files=self._version_files)
                if len(self.curr_version) == 1:
                    self.rename_build_package(self.curr_version[0])
        elif action == "config":
            if not self.uip_global_config.get("new", False):
                QuipGlobalConfig().check_config(self.uip_global_config)
            sys.exit(0)
        elif action == "setup":
            self.create_external_systems()
        elif action in CLEAN_ACTION:
            if self.args.macfilesonly:
                self.delete_macos_hidden_files(".")
            else:
                self.clean_project()
            sys.exit(0)
        elif action == "version":
            self.curr_version = vb.find_current_version(version_files=self._version_files)
            if len(self.curr_version) == 0:
                logging.warning("There is no version information found.")
                cprint("There is no version information found.", color="red")
                sys.exit(1)
            
            self.show_version(self.curr_version, self.args.version_method)
            if self.args.version_method is not None:
                if len(self.curr_version) > 1:
                    logging.error("There are multiple versions. Fix that first.")
                    sys.exit(1)
                
                self.update_version(self.args.version_method, self.curr_version[0])
                self.clean_project(False)
            
            if self.args.forced_version is not None:
                if len(self.curr_version) > 1:
                    logging.warning(f"There are multiple versions but you forced to update them all to {self.args.forced_version}")
                
                for old_version in self.curr_version:
                    if old_version == self.args.forced_version:
                        continue
                    self.update_version("forced", old_version, self.args.forced_version)
                    self.clean_project(False)

    def set_global_configs(self, project_name, config_path=None):
        if config_path is not None:
            logging.info(f"Using config from file : {config_path}")
        self.uip_global_config = QuipGlobalConfig(config_file=config_path).conf
        logging.debug(self.uip_global_config)

        self._global_conf_defaults = self.uip_global_config.get("defaults", {})
        self._global_conf_extension = self.uip_global_config.get("extension.yml", {})
        self._global_conf_uip = self.uip_global_config.get("uip.yml", {})
        self._global_conf_external = self.uip_global_config.get("external", {})
        self._version_files = self.uip_global_config.get("version_files", None)
        self.default_template = self._global_conf_defaults.get("template", "ue-task")
        self.project_prefix = self._global_conf_defaults.get("project_prefix", None)
        self.project_name = self.format_ext_name(project_name)
        self.extension_name = self.project_folder_name = self.format_project_folder_name(project_name.lower(), self.args.template, self.project_prefix)
        self.template_name = self.titleize(project_name)
        self.use_keyring = self._global_conf_defaults.get("use_keyring", True)
        logging.debug(f"Project Name: {self.project_name}")
        logging.debug(f"Template Name: {self.template_name}")
        logging.debug(f"Folder Name: {self.project_folder_name}")

    def new_template(self):
        logging.info(f"creating new template {self.template_name}")
        if os.path.exists(self.project_folder_name):
            logging.error("Folder already exists")
            sys.exit(1)

        os.makedirs(self.project_folder_name)
        os.makedirs(self.join_path("src"))
        os.makedirs(self.join_path("src", "templates"))

    def new_project(self):
        logging.info(f"creating new extension {self.template_name}")
        if os.path.exists(self.project_folder_name):
            print("ERROR: Folder already exists")
            sys.exit(1)
        
        os.makedirs(self.project_folder_name)
        self.uip_init(self.project_folder_name, self.default_template)
        self.update_extension_yaml(self.extension_name)
        self.update_uip_config(self.project_name, new_project=True)
        self.update_template_json(self.project_name, new_project=True)

    def update_project(self, update_uuid=False, update_new_uuid=False, new_project=True):
        logging.info(f"Updating extension {self.template_name}")
        if not self.args.template:
            self.update_extension_yaml(self.extension_name, new_project=new_project)
            self.update_uip_config(self.project_name, new_project=new_project)
        else:
            self.update_script_config(self.project_folder_name)
        self.update_template_json(self.project_name, update_uuid, update_new_uuid)

    def update_rename_scripts(self):
        for _script in ["script", "scriptUnix", "scriptWindows"]:
            script_path = self.join_path("src", "templates", _script)
            if os.path.exists(script_path):
                os.rename(script_path, script_path + ".py")
                cprint(f"Script renamed: {script_path} => {script_path}.py", "yellow")

    def update_icon(self):
        from PIL import Image
        import PIL

        logging.info(f"Updating icon for {self.template_name}")
        template_path = self.join_path("src", "templates")
        converted = []
        for path in os.scandir(template_path):
            logging.debug(f"Scanning file : {path}")
            if path.is_file():
                if path.name in ["template_icon.png"]:
                    continue
                if path.name.lower().endswith("48x48.png"):
                    continue
                filename = self.join_path("src", "templates", path.name)
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    logging.debug(f"Image file : {filename}")
                    output_file = os.path.splitext(filename)[0] + "_48x48.png"
                    converted.append(output_file)
                    logging.debug(f"Output Image file : {output_file}")
                    with Image.open(filename) as im:
                        im_resized = im.resize((48, 48), resample=PIL.Image.LANCZOS)
                        im_resized.save(output_file, "PNG")
        if len(converted) == 1:
            logging.info(f"Updating icon file {converted[0]} => template_icon.png")
            shutil.copy2(converted[0], os.path.join(template_path, "template_icon.png"))
        elif len(converted) == 0:
            logging.info(f"Nothing to convert. Put an image file under templates folder and make sure the file name is not 'template_icon.png'")

    def create_icon_safe(self, message=None):
        try:
            self.create_icon(message=message)
        except Exception as ex:
            logging.error(f"WARNING: Couldn't create a new ICON")
            logging.error(f"Error: {ex}")
            return

    def create_icon(self, message=None):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception as ex:
            logging.error(f"WARNING: PIL module is missing. Install it using 'pip install Pillow'")
            logging.error(f"WARNING: Couldn't create a new ICON")
            return

        logging.info(f"Creating a new icon based on the name of the template/extension.")

        width = 48
        height = 48
        if message is None:
            message = self.get_icon_message(self.template_name)
        logging.info(f"Text in the ICON will be '{message}'")
        font_size = 38
        correction_x = 3
        correction_y = -5
        if len(message) == 1:
            font_size = 38
            correction_x = 3
            correction_y = -7
        elif len(message) == 2:
            font_size = 24
            correction_x = 3
            correction_y = -5
        elif len(message) == 3:
            font_size = 18
            correction_x = 3
            correction_y = -5
        
        font_name = self._global_conf_defaults.get("icon_font", "cour.ttf")
        font = ImageFont.truetype(font_name, size=font_size)
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        imgDraw = ImageDraw.Draw(img)

        textWidth = font.getbbox(message)[2]
        textHeight = font.getbbox(message)[3]
        xText = (width - textWidth + correction_x) / 2
        yText = (height - textHeight + correction_y) / 2

        imgDraw.ellipse((4, 4, 44, 44), outline=(50, 110, 230), fill=(50, 110, 230))
        imgDraw.text((xText, yText), message, font=font, fill='white', stroke_width=1)

        template_path = self.join_path("src", "templates")
        img.save(os.path.join(template_path, "template_icon.png"))
    
    def get_icon_message(self, message):
        result = []
        message = message.upper()
        message = message.replace("-", " ")
        message = message.replace("  ", " ")
        words = message.split(" ")
        if words[0] in ["UT", "UE"]:
            words = words[1:]

        if self.project_prefix is not None and words[0] == self.project_prefix.upper():
            words = words[1:]

        if len(words[-1]) < 4:
            return words[-1]
        else:
            for word in words:
                result.append(word[0])
        
        if len("".join(result)) < 3:
            match = re.search("(\d+)$", words[-1])
            if match is not None:
                result.append(match.group(0))

        return "".join(result)[:3]

    def delete_project(self):
        logging.info(f"Deleting extension {self.template_name}")
        if not os.path.exists(self.project_folder_name):
            logging.error("Folder doesn't exist")
            sys.exit(1)

        shutil.rmtree(self.project_folder_name)

    def delete_macos_hidden_files(self, dir_path):
        logging.debug(f"Deleting MacOS Hidden Files: {dir_path}")
        for filename in os.listdir(dir_path):
            if filename.startswith('.') or filename.startswith('._'):
                if filename == '.DS_Store' or filename == '.localized':
                    os.remove(os.path.join(dir_path, filename))
                elif filename.startswith('._'):
                    original_filename = filename[2:]
                    original_file_path = os.path.join(dir_path, original_filename)
                    if os.path.exists(original_file_path):
                        os.remove(os.path.join(dir_path, filename))
                    else:
                        logging.info(f"Skipping {filename} (corresponding original file not found)")
            elif os.path.isdir(os.path.join(dir_path, filename)):
                self.delete_macos_hidden_files(os.path.join(dir_path, filename))


    def clean_project(self, full=True):
        if full:
            folders = ["build", "dist", "temp", "downloads"]
        else:
            folders = ["build", "dist"]
        
        # Clean Mac specific files
        if platform.system() == 'Darwin':  # Check if the OS is macOS
            self.delete_macos_hidden_files(self.join_path("."))
        
        if not self.args.template:
            self.run_uip("clean")

        for folder in folders:
            folder_path = self.join_path(folder)
        
            if os.path.exists(folder_path):
                cprint(f"Deleting content of {folder_path}", color="blue")
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))
                try:
                    shutil.rmtree(folder_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (folder_path, e))

    def clone_project(self, from_project_path, all_files=False, exclude_list=None):
        if not os.path.exists(from_project_path):
            logging.error(f"From path does NOT exists. {from_project_path}")
            sys.exit(1)
        
        from_project_src_path = os.path.join(from_project_path, "src")
        if not os.path.exists(from_project_src_path):
            logging.error("From path is not a extension path")
            sys.exit(1)

        if os.path.exists(self.project_folder_name):
            logging.error("Folder already exists")
            sys.exit(1)
        
        os.makedirs(self.project_folder_name)
        if not self.args.template:
            self.uip_init(self.project_folder_name, self.default_template)

        if not all_files:
            logging.debug("Copying all files to new folder.")
            files = copy_tree(from_project_src_path, self.join_path("src"))
        else:
            source_files = os.listdir(from_project_path)
            if exclude_list is not None:
                logging.info(f"Ignoring following items: {exclude_list}")
                source_files = list(set(source_files) - set(exclude_list))
            for source_file in sorted(source_files):
                source_file_path = os.path.join(from_project_path, source_file)
                if os.path.isdir(source_file_path):
                    files = copy_tree(source_file_path, self.join_path(source_file))
                    for f in files:
                        logging.info(f"Copying file {f}")
                else:
                    shutil.copy2(source_file_path, self.join_path(source_file))
                    logging.info(f"Copying file {source_file}")
        
        self.update_project(update_uuid=True, update_new_uuid=True, new_project=True)

    def bootstrap_project(self):
        # get bootstrap source
        from_project_path = self._global_conf_defaults.get("bootstrap", {}).get("source", None)
        if from_project_path is None:
            logging.error("Bootstrap source not found. Please check the config file.")
            sys.exit(2)
        
        exclude_list = self._global_conf_defaults.get("bootstrap", {}).get("exclude", None)
        
        self.clone_project(from_project_path, all_files=True, exclude_list=exclude_list)

    def bootstrap_template(self, ask_for_upload=True):
        # get bootstrap source
        from_project_path = self._global_conf_defaults.get("bootstrap", {}).get("template_source", None)
        if from_project_path is None:
            logging.error("Bootstrap template source not found. Please check the config file.")
            sys.exit(2)
        
        exclude_list = self._global_conf_defaults.get("bootstrap", {}).get("template-exclude", None)
        
        self.clone_project(from_project_path, all_files=True, exclude_list=exclude_list)
        if ask_for_upload:
            answer = yes_or_no("Do you want to push the template to controller? ", default=True)
            if answer == True:
                self.upload_template()

    def upload_template(self):
        zip_file_path = self.build_zip(self.project_name)

        uac_url = self._global_conf_uip.get("url", "http://localhost:8080/uc")
        uac_user = self._global_conf_uip.get("userid", "ops.admin")
        # uac_pass = input(f"Enter password for {uac_user}: ")
        uac_pass = self.ask_password(uac_url, uac_user)

        template_url = uac_url + "/resources/universaltemplate/importtemplate"
        logging.info(f"Uploading to controller ({uac_url})")
        with open(zip_file_path, "rb") as zipfile:
            zipfile_data = zipfile.read()
        result = requests.post(template_url, data=zipfile_data, auth=(uac_user, uac_pass), verify=False)
        if result.ok:
            logging.info(f"Template {self.template_name} pushed to {uac_url}")
        else:
            logging.error(f"Error while pushing {self.template_name} to {uac_url}")
            logging.error(f"Error detail: {result.text}")
            sys.exit(3)

    def upload_template_json(self):
        uac_user = self._global_conf_uip.get("userid", "ops.admin")
        uac_url = self._global_conf_uip.get("url", "http://localhost:8080/uc")
        template_url = uac_url + "/resources/universaltemplate"
        logging.info(f"Uploading to controller ({uac_url})")
        uac_pass = self.ask_password(uac_url, uac_user)
        payload = self.merge_template_scripts(self.project_name)
        logging.debug(f"Payload = {self.format_json(payload)}")
        
        answer = yes_or_no("Are you updating existing template? ", default=True)
        if answer == True:
            logging.info("Updating existing template")
            result = requests.put(template_url, json=payload, auth=(uac_user, uac_pass), verify=False)
        else:
            logging.info("Creating new template")
            result = requests.post(template_url, json=payload, auth=(uac_user, uac_pass), verify=False)
        
        if result.ok:
            logging.info(f"Template {self.template_name} pushed to {uac_url}")
        else:
            logging.error(f"Error while pushing {self.template_name} to {uac_url}")
            logging.error(f"Error detail: {result.text}")
            sys.exit(3)
        
        logging.info("Uploading icon")
        template_icon_url = uac_url + "/resources/universaltemplate/seticon?templatename=" + self.template_name
        # application/octet-stream, image/png
        headers = {"content-type": "image/png", "Accept": "plain/text"}
        with open(self.join_path("src", "templates", "template_icon.png"), "rb") as icon:
            icon_data = icon.read()
        icon_result = requests.post(template_icon_url, data=icon_data, auth=(uac_user, uac_pass), verify=False)
        
    def download_template(self, template_name=None):
        uac_user = self._global_conf_uip.get("userid", "ops.admin")
        uac_url = self._global_conf_uip.get("url", "http://localhost:8080/uc")
        logging.info(f"Downloading template from controller ({uac_url})")
        uac_pass = self.ask_password(uac_url, uac_user)

        if template_name is None:
            template_name = self.template_name

        #template_url = uac_url + "/resources/universaltemplate?templatename=" + self.template_name
        #headers = {"content-type": "application/json", "Accept": "application/json"}
        #logging.debug(f"Template URL is {template_url}")
        #result = requests.get(template_url, auth=(uac_user, uac_pass), headers=headers, verify=False)
        
        logging.info("Downloading template zip")
        template_url = uac_url + "/resources/universaltemplate/exporttemplate?templatename=" + self.template_name
        headers = {"Accept": "application/octet-stream"}
        logging.debug(f"Template URL is {template_url}")
        result = requests.get(template_url, auth=(uac_user, uac_pass), headers=headers, verify=False, allow_redirects=True)
        if result.ok:
            with tempfile.TemporaryDirectory() as tmpdirname:
                with open(os.path.join(tmpdirname, "template.zip"), "wb") as f:
                    f.write(result.content)
                download_folder = self.join_path("downloads")
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)
                shutil.copy2(os.path.join(tmpdirname, "template.zip"), os.path.join(download_folder, "template.zip"))
                logging.info(f"Download file archived in download folder {download_folder}")
                logging.info("Unpacking the zip file")
                unpack_archive(os.path.join(tmpdirname, "template.zip"), extract_dir=tmpdirname, format="zip")
                with open(os.path.join(tmpdirname, "template.json")) as json_f:
                    json_data = json_f.read()
                if os.path.exists(os.path.join(tmpdirname, "template_icon.png")):
                    logging.info("Icon updated from zip file")
                    shutil.copy2(os.path.join(tmpdirname, "template_icon.png"), self.join_path("src", "templates", "template_icon.png"))
                else:
                    logging.warn("Icon file is missing")
            
            self.split_template_scripts(json.loads(json_data))
        else:
            logging.error(f"Error while downloading {self.template_name} from {uac_url}")
            logging.error(f"Error detail: {result.text}")
            sys.exit(3)

    def update_fields(self, code=False):
        fields_path = self.join_path("fields.yml")
        if os.path.exists(fields_path):
            with open(fields_path) as f:
                conf = yaml.safe_load(f)
                template_dict = fb.prepare_template_fields(conf)
                new_fields = conf.get("fields", [])
                
                logging.debug("FIELDS: ", new_fields)
                fields_dict = fb.prepare_fields(new_fields, code)
                template_dict["fields"] = fields_dict

                new_events = conf.get("events", [])
                logging.debug("EVENTS: ", new_events)
                events_dict = fb.prepare_event_fields(new_events)
                template_dict["events"] = events_dict
            
            logging.info("Updating template.json file")
            template = self.join_path("src", "templates", "template.json")
            if os.path.exists(template):
                with open(template, "r") as f:
                    template_content = f.read()
                    
                _json = json.loads(template_content)
                _json.update(template_dict)
                
                with open(template, "w") as f:
                    f.write(self.format_json(_json))
                    logging.debug("template.json file is updated")
                self.dump_fields(write=True)
                logging.debug("fields.yml updated")
                
                # have modified time of template be later than fields.yml
                os.utime(template)
            else:
                logging.error(f"ERROR: template.json file is missing! Path= {template}")
                sys.exit(1)
        else:
            logging.error(f"fields.yml file is missing")
            sys.exit(4)

    def update_fields_if_needed(self):
        template_json_path = self.join_path("src", "templates", "template.json")
        fields_path = self.join_path("fields.yml")
        if os.path.getmtime(fields_path) > os.path.getmtime(template_json_path):
            cprint("It looks like fields.yml file changed.", "cyan")
            if yes_or_no("Do you want to update template.json?", default=True, color="cyan"):
                self.update_fields()

    def dump_fields(self, write=False):
        logging.info("Writing fields to fields.yml file")
        template = self.join_path("src", "templates", "template.json")
        if os.path.exists(template):
            with open(template, "r") as f:
                template_content = f.read()
                _json = json.loads(template_content)
                template_dict = fb.dump_template_fields(_json)
                fields_dict = fb.dump_fields(_json.get("fields"))
                template_dict["fields"] = fields_dict
                events_dict = fb.dump_events(_json.get("events", None))
                template_dict["events"] = events_dict
                yaml_dump = yaml.dump(template_dict, Dumper=MyDumper, default_flow_style=False, sort_keys=False, width=1000)
                yaml_dump = yaml_dump.replace('fields:\n', '\nfields:')
                yaml_dump = yaml_dump.replace('events:\n', '\nevents:')
                if not write:
                    print(yaml_dump)
                else:
                    fields_path = self.join_path("fields.yml")
                    with open(fields_path, "w") as f:
                        f.write(yaml_dump)
            
            # Update template.json time
            os.utime(template)
        else:
            logging.error(f"ERROR: template.json file is missing! Path= {template}")
            sys.exit(1)

    def create_external_systems(self):
        repository_name = None
        gl_config = self._global_conf_external.get("gitlab", None)
        jnks_config = self._global_conf_external.get("jenkins", None)
        sq_config = self._global_conf_external.get("sonarqube", None)
        if gl_config is None:
            logging.warn("Gitlab configuration is missing in the uip_config file.")
        if jnks_config is None:
            logging.warn("Jenkins configuration is missing in the uip_config file.")
        if sq_config is None:
            logging.warn("SonarQube configuration is missing in the uip_config file.")
        
        if gl_config is not None:
            cprint("\n==== GITLAB SETUP ====", "blue")
            gl = self.initialize_gitlab(gl_config)
            self.setup_gitlab(gl, gl_config)
            repository_name = gl.repository_name

        if repository_name is None:
            # can not continue without repository_name
            logging.warn("Cannot continue without GitLab repository.")
            sys.exit(0)

        if jnks_config is not None:
            cprint("\n==== JENKINS SETUP ====", "blue")
            jnks = self.initialize_jenkins(jnks_config)

            gl_groups = gl_config.get("groups", [])
            jnks_groups = jnks_config.get("groups", {})
            jnks_group_details, jnks_repository_name = external.parse_repository_full_path(repository_name, gl_groups, jnks_groups)
            jnks_group_name = jenkins_credential = None
            if jnks_group_details:
                if isinstance(jnks_group_details, str):
                    jnks_group_name = jnks_group_details
                    jenkins_credential = "cs_prototype_api_personal_access_token"
                elif isinstance(jnks_group_details, dict):
                    jnks_group_name = jnks_group_details["name"]
                    jenkins_credential = jnks_group_details["credential"]
            self.setup_jenkins(jnks, jnks_group_name, jnks_repository_name, gl.base_url, repository_name, jenkins_credential)
            
        # create webhook for Jenkins
        if gl_config is not None and jnks_config is not None:
            jenkins_url = jnks.get_url(jnks_group_name, jnks_repository_name)
            if gl.create_webhook(jenkins_url):
                cprint("Webhook created", "green")
            if gl.create_badge(jenkins_url, jnks_config.get("url"), jnks_group_name, jnks_repository_name):
                cprint("Badge created", "green")

        if sq_config is not None:
            cprint("\n==== SONARQUBE SETUP ====", "blue")
            # check if SonarQube project exists
            sq_groups = sq_config.get("groups", {})
            if jnks_group_name in sq_groups:
                sq_group_name = sq_groups.get(jnks_group_name)
                if yes_or_no("Do you want to create SonarQube projects?", default=True):
                    self.create_sonarqube(sq_group_name, jnks_repository_name, sq_config)
            else:
                cprint("No need to create SonarQube Project.", "green")
    
    def setup_gitlab(self, gl, gl_config):
        repository_name = None
        
        git_path = template = self.join_path(".git", "config")
        if os.path.exists(git_path):
            repository_name = external.get_git_info(git_path, "origin")
        
        if repository_name is not None:
            cprint(f"Repository exists in git config: {repository_name}", "magenta")

            if self.check_gitlab_repository_exists(gl, repository_name):
                cprint(f"Repository exists in GitLab: {repository_name}", "green")
            else:
                cprint(f"Repository doesn't exist in GitLab: {repository_name}", "red")
                if yes_or_no("Do you want to create GitLab repository?", default=True):
                    repository_name = self.create_gitlab(gl, repository_name, config=gl_config)
        else:
            if yes_or_no("Do you want to create Gitlab repository?", default=True):
                repository_name = self.create_gitlab(gl, config=gl_config)
        
        gl.repository_name = repository_name
        return gl
    
    def setup_jenkins(self, jnks, jnks_group_name, jnks_repository_name, gitlab_url, repository_name, jenkins_credential):
        logging.debug(f"Group: {jnks_group_name}, Repository: {jnks_repository_name}")
        # Check if Jenkins Pipeline exists
        if jnks.check_job_exists(jnks_group_name, jnks_repository_name):
            cprint(f"Job exists in Jenkins: {jnks_group_name}/{jnks_repository_name}", "magenta")
        else:
            logging.info(f"Repository doesn't exist and will be created. {jnks_group_name}/{jnks_repository_name}")
            if yes_or_no("Do you want to create Jenkins Job?", default=True):
                jnks.create_job(jnks_group_name, jnks_repository_name, self.project_name, gitlab_url, repository_name, jenkins_credential)
                cprint(f"Jenkins job created: {jnks_group_name}/{jnks_repository_name}", "green")

    def create_sonarqube(self, group_name, repository_name, sq_config):
        sq_url = sq_config.get("url", None)
        use_token = sq_config.get("use_token", True)
        if use_token:
            sq_pass = self.ask_password(sq_url, "token", prompt="Please enter Personal Access Key: ")
            username = sq_pass
            sq_pass = ""
        else:
            username = sq_config.get("username", None)
            if username is None:
                logging.error("Sonarqube username configuration is missing in the uip_config file.")
                return False

            sq_pass = self.ask_password(sq_url, username, prompt=f"Please enter SonarQube password for {username}: ")
        
        ssl_verify = sq_config.get("ssl_verify", True)
        sq = external.SonarQube(sq_url, (username, sq_pass), ssl_verify)
        prefix = group_name
        sq_project_name = prefix + "_" + repository_name
        sq.create_project(sq_project_name)

    def create_gitlab(self, gl, repository_name=None, config=None):
        logging.info("Creating GitLab Repository.")
        
        if repository_name is None:
            groups = gl.get_groups()
            logging.debug(f"Groups = {groups}")
            group = choose_one(groups, title="Gitlab Groups", default=gl.default_group)
            logging.debug(f"Selected group = {group}")
            group_id = group[1]
            logging.debug(f"group_id = {group_id}")
            _group = gl.gl.groups.get(group_id)
            logging.debug(f"_group = {_group}")
            group_path = _group.full_path
            logging.debug(f"group_path = {group_path}")
            repository_name = f"{group_path}/{self.extension_name}"
        
        if self.check_gitlab_repository_exists(gl, repository_name):
            cprint(f"There is a repository already exists in GitLab. ({repository_name})", "yellow")
            cprint(f"Run `git remote add origin {gl.base_url}/{repository_name}.git", "yellow")
        else:
            gl.create_project(self.extension_name, group_id, config=config)
            cprint(f"Repository created {repository_name}", "green")
        
            if config.get("git-init", False):
                self.run_git("init")
                self.run_git(f"remote add origin {gl.base_url}/{repository_name}.git")
                if gl.default_branch is not None:
                    if os.path.exists(self.join_path("README.md")):
                        os.rename(self.join_path("README.md"), self.join_path("README.md.temp"))
                    self.run_git(f"checkout -b {gl.default_branch}")
                    self.run_git(f"pull origin {gl.default_branch}")
                    if os.path.exists(self.join_path("README.md.temp")):
                        os.remove(self.join_path("README.md"))
                        os.rename(self.join_path("README.md.temp"), self.join_path("README.md"))

            else:
                cprint(f"Run `git init`", "green")
                cprint(f"Run `git remote add origin {gl.base_url}/{repository_name}.git`", "green")

                if gl.default_branch is not None:
                    cprint(f"Default branch created. There will be an initial commit for that branch for README.md file", "yellow")
                    cprint(f"Be sure you rename README.md file and run ", "yellow")
                    cprint(f"     git checkout -b {gl.default_branch}", "yellow")
                    cprint(f"     git pull origin {gl.default_branch}", "yellow")
            
        return repository_name
    
    def check_gitlab_repository_exists(self, gl, repository_name):
        logging.info(f"Checking GitLab if the repository exists. Repository={repository_name}")
            
        projects = gl.get_projects()
        for project in projects:
            if repository_name == project[0]:
                gl.project_id = project[1]
                return True
        
        return False

    def initialize_gitlab(self, gl_config):
        gl_url = gl_config.get("url", None)
        gl_token = self.ask_password(gl_url, "token", prompt="Please enter Personal Access Key: ")
        ssl_verify = gl_config.get("ssl_verify", True)
        default_group = gl_config.get("default_group", None)
        gl = external.GitLab(gl_url, gl_token, ssl_verify, default_group)
        return gl

    
    def initialize_jenkins(self, jnks_config):
        logging.info("Connecting to Jenkins Server.")
        jnks_url = jnks_config.get("url", None)
        username = jnks_config.get("username", True)
        ssl_verify = jnks_config.get("ssl_verify", True)
        jnks_token = self.ask_password(jnks_url, username, prompt=f"Please enter Jenkins Password for ({username}): ")
        jnks = external.Jenkins(jnks_url, (username, jnks_token), ssl_verify)
        return jnks

    
    def create_jenkins(self, repository_name, jnks=None):
        if jnks is None:
            jnks_config = self._global_conf_external.get("gitlab", {})
            jnks_url = jnks_config.get("url", None)
            if jnks_url is None:
                logging.warn("Jenkins configuration is missing in the uip_config file.")
                return None

            username = jnks_config.get("username", True)
            jnks_token = self.ask_password(jnks_url, username, prompt=f"Please enter Jenkins Password for ({username}): ")
            ssl_verify = jnks_config.get("ssl_verify", True)
            default_group = jnks_config.get("default_group", None)
            jnks = external.Jenkins(jnks_url, (username, jnks_token), ssl_verify, default_group)
        projects = jnks.get_projects()
        for project in projects:
            if repository_name == project[0]:
                return True
        
        return False

    def build_zip(self, project_name):
        with tempfile.TemporaryDirectory() as tmpdirname:
            logging.debug(f"Created temporary directory {tmpdirname}")
            payload = self.merge_template_scripts(self.project_name)
            template = os.path.join(tmpdirname, "template.json")
            with open(template, "w") as f:
                f.write(self.format_json(payload))
            template_icon = self.join_path("src", "templates", "template_icon.png")
            shutil.copy2(template_icon, os.path.join(tmpdirname, "template_icon.png"))
            if os.path.exists("script.yml"):
                with open("script.yml") as f:
                    conf = yaml.safe_load(f)
                    version = conf.get("script", []).get("version")
            else:
                version = datetime.now().strftime("%Y%m%d")

            archive_name = f"unv-tmplt-{self.format_ext_name(project_name.lower())}-{version}"
            new_archive_file = make_archive(archive_name, "zip", root_dir=tmpdirname)
            logging.info(f"Archive file created. File name is {archive_name}.zip")
            build_folder = self.join_path("build")
            if not os.path.exists(build_folder):
                os.makedirs(build_folder)
            move(new_archive_file, os.path.join(build_folder, archive_name + ".zip"))
            logging.debug(f"Archive file {archive_name}.zip moved to {build_folder}")
        return os.path.join(build_folder, archive_name + ".zip")

    def show_version(self, current_versions, update):
        cprint(f"Current Version {current_versions}", color="green")
        if update is None:
            print(f"Possible next versions:")
            print(f"   RELEASE: ", vb.get_new_version("release", current_versions[0]))
            print(f"   MAJOR: ", vb.get_new_version("major", current_versions[0]))
            print(f"   MINOR: ", vb.get_new_version("minor", current_versions[0]))
            print(f"   BETA: ", vb.get_new_version("beta", current_versions[0]))
            print(f"   RC: ", vb.get_new_version("rc", current_versions[0]))

    def update_version(self, method, current_version, forced_version=None):
        if forced_version is None:
            new_version = vb.get_new_version(method, self.curr_version[0])
        else:
            new_version = forced_version
        cprint(f"NEW Version will be {new_version}", color="green")
        answer = yes_or_no(f"Do you want to update the versions from {current_version} to {new_version}? ", default=True)
        if answer == True:
            vb.update_version(current_version, new_version, version_files=self._version_files)

    def titleize(self, name):
        if name[:3] in ["ue-", "ut-"]:
            name = name[3:]
        if name.lower() != name:
            # if name has uppercase than use it as-is
            return name
        name = name.replace("_", " ")
        name = name.replace("-", " ")
        name = name.replace("/", "")
        return name.title()

    def format_ext_name(self, name):
        if name.lower() != name:
            return name
        name = name.replace("_", "-")
        name = name.replace(" ", "-")
        name = name.replace("/", "")
        name = name.replace("---", "-")
        name = name.replace("--", "-")
        return name.lower()
    
    def format_project_folder_name(self, project_name, template, prefix=None):
        if len(project_name) == 0:
            return project_name
        
        ext_name = self.format_ext_name(project_name.lower())

        if ext_name[:3] in ["ue-", "ut-"]:
            ext_name = ext_name[3:]
        
        if prefix is not None:
            if not ext_name.startswith(prefix):
                ext_name = prefix + "-" + ext_name

        if template:
            ext_name = "ut-" + ext_name
        else:
            ext_name = "ue-" + ext_name

        return ext_name

    def join_path(self, *paths):
        if self.in_project_folder:
            return os.path.join(os.getcwd(), *paths)
        else:
            return os.path.join(self.project_folder_name, *paths)

    def uip_init(self, project_name, default_template):
        # run uip init command
        command = f'''uip init -t {default_template} {project_name}'''
        logging.info(f"Initializing the extension with command {command}")
        command = subprocess.run(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if command.returncode != 0:
            logging.error("UIP Init command failed.")
            logging.error(f"ERROR: Command is {command}")
            logging.error(f"ERROR: Return code is {command.returncode}")
            sys.exit(command.returncode)
    
    def run_uip(self, action):
        need_pass = False
        uac_url = self._global_conf_uip["url"]
        uac_user = self._global_conf_uip["userid"]
        if action in ["push_all", "push"]:
            additional_params = "-a" if action == "push_all" else ""
            command = f'''uip push {additional_params} -i {uac_url} -u {uac_user}'''
            need_pass = True
        elif action == "pull":
            need_pass = True
            command = f'''uip pull -i {uac_url} -u {uac_user}'''
        elif action == "build":
            need_pass = False
            command = f'''uip build -a'''
        elif action == "clean":
            need_pass = False
            command = f'''uip clean'''

        if need_pass:
            uac_pass = self.ask_password(uac_url, uac_user)
            os.environ["UIP_PASSWORD"] = uac_pass
        
        logging.info(f"Initializing the extension with command {command}")
        cprint(command, color="yellow")
        result = subprocess.run(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            logging.error("UIP command failed.")
            logging.error(f"ERROR: Command is {command}")
            logging.error(f"ERROR: Return code is {command.returncode}")
            sys.exit(command.returncode)
        else:
            cprint(f"======= UIP Output =======", color="yellow")
            for line in result.stdout.splitlines():
                if line.lower().startswith("success"):
                    cprint(line, color="green")
                elif line.lower().find("error") > 0:
                    cprint(line, color="red")
                else:
                    print(line)
            cprint(f"==============", color="yellow")
    
    def run_git(self, command):
        command = "git " + command
        cprint(command, color="yellow")
        result = subprocess.run(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            logging.error("GIT command failed.")
            logging.error(f"ERROR: Command is {command}")
            logging.error(f"ERROR: Return code is {command.returncode}")
            sys.exit(command.returncode)
        else:
            if len(result.stdout) > 0:
                cprint(f"======= GIT Output =======", color="yellow")
                for line in result.stdout.splitlines():
                    if line.lower().startswith("success"):
                        cprint(line, color="green")
                    elif line.lower().find("error") > 0:
                        cprint(line, color="red")
                    else:
                        print(line)
                cprint(f"==============", color="yellow")
            
    def rename_build_package(self, version):
        package_folder = self.join_path("dist", "package_build")
        for filename in os.listdir(package_folder):
            if filename.endswith("universal_template.zip"):
                base_filename = "unv-tmplt-" + os.path.basename(filename).replace("_universal_template.zip", f"-{version}.zip").replace("_", " ")
                new_filename = os.path.join(os.path.dirname(filename),  base_filename)
                new_filepath = self.join_path("dist", "package_build", new_filename)
                if os.path.exists(new_filepath):
                    shutil.move(self.join_path("dist", "package_build", filename), new_filepath)
                else:
                    os.rename(self.join_path("dist", "package_build", filename), new_filepath)
                cprint(f"File Renamed: {filename} => {new_filename}", "yellow")

    def update_extension_yaml(self, project_name, new_project=True):
        logging.info("Updating extension.yml file")
        extension_config = self.join_path("src", "extension.yml")
        if os.path.exists(extension_config):
            if new_project:
                with open(extension_config, "w") as f:
                    _extension_config = self._global_conf_extension
                    _extension_config["extension"]["name"] = project_name
                    yaml.dump(_extension_config, f, sort_keys=False)
            else:
                with open(extension_config) as f:
                    _config = yaml.safe_load(f)

                with open(extension_config, "w") as f:
                    _config["extension"]["name"] = project_name
                    yaml.dump(_config, f, sort_keys=False)
            logging.debug("extension.yml file is updated")
        else:
            logging.error(f"ERROR: extension.yml file is missing! Path= {extension_config}")
            sys.exit(1)

    def update_uip_config(self, project_name, new_project=True):
        logging.info("Updating uip.yml file")
        config = self.join_path(".uip", "config", "uip.yml")
        if os.path.exists(config):
            if new_project:
                with open(config, "w") as f:
                    _config = self._global_conf_uip
                    _config["template-name"] = self.template_name
                    yaml.dump(_config, f, sort_keys=False)
            else:
                with open(config) as f:
                    _config = yaml.safe_load(f)

                with open(config, "w") as f:
                    _config["template-name"] = self.template_name
                    yaml.dump(_config, f, sort_keys=False)
            logging.debug("uip.yml file is updated")
        else:
            logging.error(f"ERROR: uip.yml file is missing! Path= {config}")
            sys.exit(1)
    
    def update_script_config(self, project_name):
        logging.info("Updating script.yml file")
        config = self.join_path("script.yml")
        
        if os.path.exists(config):
            with open(config) as f:
                _config = yaml.safe_load(f)

            with open(config, "w") as f:
                _config["script"]["name"] = project_name
                yaml.dump(_config, f, sort_keys=False)
                logging.debug("script.yml file is updated")
        else:
            logging.error(f"ERROR: script.yml file is missing! Path= {config}")
            sys.exit(1)

    def read_template_json(self, template_path):
        logging.info("Reading template.json file")
        
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                template_content = f.read()
                return json.loads(template_content)
        else:
            logging.error(f"ERROR: template.json file is missing! Path= {template_path}")
            sys.exit(1)

    def update_template_json(self, project_name, update_uuid=False, update_new_uuid=False, new_project=False):
        logging.info("Updating template.json file")
        template = self.join_path("src", "templates", "template.json")
        if os.path.exists(template):
            with open(template, "r") as f:
                template_content = f.read()
                if update_uuid:
                    logging.info("Updating SysIds in template.json")
                    template_content = self.update_all_sysid_values(template_content)
                if update_new_uuid:
                    logging.info("Updating new_uuid with a valid SysIds in template.json")
                    template_content = self.update_new_uuid_values(template_content)
            
            with open(template, "w") as f:
                _json = json.loads(template_content)
                if new_project:
                    if "extension" in _json and _json["extension"] is not None:
                        _json["extension"] = self.extension_name
                    _json["name"] = self.template_name
                    if "variablePrefix" in _json:
                        if self.args.template:
                            _json["variablePrefix"] = "var"
                        else:
                            _json["variablePrefix"] = self.extension_name.replace("-", "_")
                            if len(_json["variablePrefix"]) > 20:
                                _json["variablePrefix"] = "ext"
                f.write(self.format_json(_json))
            logging.debug("template.json file is updated")
        else:
            logging.error(f"ERROR: template.json file is missing! Path= {template}")
            sys.exit(1)
    
    def merge_template_scripts(self, project_name):
        logging.info("Merging scripts to template.json file")
        template = self.join_path("src", "templates", "template.json")
        if os.path.exists(template):
            with open(template, "r") as f:
                template_content = f.read()

            _json = json.loads(template_content)
            if _json["useCommonScript"]:
                script_path = self.join_path("src", "templates", "script.py")
                if not os.path.exists(script_path):
                    script_path = self.join_path("src", "templates", "script")
                script_content = self.read_file_content(script_path)
                _json["script"] = r"""{}""".format(script_content)
                _json["scriptUnix"] = None
                _json["scriptWindows"] = None
            else:
                _json["script"] = None
                if _json["agentType"] in ["Linux/Unix", "Any"]:
                    script_unix_path = self.join_path("src", "templates", "scriptUnix.py")
                    if not os.path.exists(script_unix_path):
                        script_unix_path = self.join_path("src", "templates", "scriptUnix")
                    script_unix_content = self.read_file_content(script_unix_path)
                    _json["scriptUnix"] = script_unix_content #.replace('\n', '\\n')

                if _json["agentType"] in ["Windows", "Any"]:
                    script_windows_path = self.join_path("src", "templates", "scriptWindows.py")
                    if not os.path.exists(script_windows_path):
                        script_windows_path = self.join_path("src", "templates", "scriptWindows")
                    script_windows_content = self.read_file_content(script_windows_path)
                    _json["scriptWindows"] = script_windows_content #.replace('\n', '\\n')
            
            if "iconFilename" not in _json:
                icon_file = self.join_path("src", "templates", "template_icon.png")
                if os.path.exists(icon_file):
                    logging.info("Icon fields are added to the template.json payload.")
                    _json["iconDateCreated"] = "2022-06-23 15:37:45"
                    _json["iconFilename"] = "template_icon.png"
                    _json["iconFilesize"] = os.path.getsize(icon_file)

            # Remove new fields to it can be imported to 7.1
            if "events" in _json:
                del _json["events"]
            if "sendVariables" in _json:
                del _json["sendVariables"]

            return _json
        else:
            logging.error(f"ERROR: template.json file is missing! Path= {template}")
            sys.exit(1)

    def split_template_scripts(self, payload_json):
        if payload_json["useCommonScript"]:
            script_path = self.join_path("src", "templates", "script.py")
            self.write_to_file(script_path, payload_json["script"])
        else:
            if payload_json["agentType"] in ["Linux/Unix", "Any"]:
                script_unix_path = self.join_path("src", "templates", "scriptUnix.py")
                self.write_to_file(script_unix_path, payload_json["scriptUnix"])
            if payload_json["agentType"] in ["Windows", "Any"]:
                script_windows_path = self.join_path("src", "templates", "scriptWindows.py")
                self.write_to_file(script_windows_path, payload_json["scriptWindows"])

        payload_json["script"] = None
        payload_json["scriptUnix"] = None
        payload_json["scriptWindows"] = None

        # Remove new fields to it can be imported to 7.1
        del payload_json["events"]
        del payload_json["sendVariables"]

        template = self.join_path("src", "templates", "template.json")
        with open(template, "w") as f:
            f.write(self.format_json(payload_json))
            logging.debug("template.json file is updated")
    
    def format_json(self, json_obj):
        json_string = json.dumps(json_obj, indent=4, sort_keys=True)
        json_string = re.sub(r"\n\s*\{", " {", json_string)
        json_string = re.sub(r"\n\s*\]", " ]", json_string)
        json_string = re.sub(r"\[\],", "[ ],", json_string)
        json_string = re.sub(r"\":(\s*[^\n]+)", "\" :\\1", json_string)
        return json_string

    def read_file_content(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
        else:
            logging.error(f"ERROR: file is missing! Path= {file_path}")
            sys.exit(1)

        return content

    def write_to_file(self, file_path, content):
        try:
            short_file_path = file_path.replace(os.getcwd(), "")
            if content is None:
                logging.warn(f"Script Content for {short_file_path} is empty.")
                return

            if os.path.exists(file_path):
                if not yes_or_no(f"Do you want to overwrite the script file? ({short_file_path}): ", default=False):
                    logging.info(f"Script file NOT updated.")
                    return None
            
            logging.info(f"Script file updated: {short_file_path}")
            with open(file_path, "w") as f:
                f.write(content)
        except Exception as ex:
            logging.error(f"ERROR: While writing to file! Path= {file_path}")
            logging.error(f"ERROR: {ex}")
            sys.exit(1)

    def update_all_sysid_values(self, template_content):
        regex = re.compile(r"""\"sysId\"\s*:\s*\"([^\"]+)\"""")
        matches = regex.finditer(template_content)
        olds = set()
        for match in matches:
            old = match.group(1)
            if old in olds:
                continue

            new = self.get_new_uuid()
            logging.info(f"Updating SysID: {old} => {new}")
            template_content = template_content.replace(old, new)
            olds.add(old)
        
        _json = json.loads(template_content)
        if "sysId" in _json:
            old = _json["sysId"]
            if not regex.match(old):
                new = self.get_new_uuid()
                logging.info(f"Updating SysID: {old} => {new}")
                _json["sysId"] = new
                template_content = self.format_json(_json)
        
        return template_content

    def update_new_uuid_values(self, template_content):
        old = '"new_uuid"'
        for i in range(template_content.count(old)):
            new = "\"{}\"".format(self.get_new_uuid())
            logging.info(f"Updating SysID: {old} => {new}")
            template_content = template_content.replace(old, new, 1)
        
        return template_content
    
    def get_new_uuid(self):
        return str(uuid.uuid4()).replace("-","")
    
    def ask_password(self, server, user_name, prompt=None, color='cyan', style='normal'):
        cprint(f"Server = `{server}`, User = `{user_name}`", color, style=style)
        if prompt is None:
            prompt = f'''Enter password for {user_name}: '''
            if self.use_keyring:
                if (keyring.get_password(server, user_name) is not None):
                    prompt = f'''Enter password for {user_name} or [Enter] to use the existing password : '''
        else:
            if self.use_keyring:
                if (keyring.get_password(server, user_name) is not None):
                    print("There is a saved password. To used the saved password just press [Enter]")
        if color is not None:
            prompt = color_text(prompt, color, style=style)
        password = getpass(prompt=prompt)
        if len(password) == 0:
            if self.use_keyring:
                logging.debug("Using password from Keyring")
                # get password 
                password = keyring.get_password(server, user_name)
            else:
                logging.error("Password is missing.")
                return None
        else:
            if self.use_keyring:
                logging.debug("Updating the password in Keyring")
                # set password 
                keyring.set_password(server, user_name, password)
        
        return password

class QuipGlobalConfig:
    def __init__(self, config_file=None) -> None:
        self.conf = {}
        self.new_config = False
        if config_file is None:
            config_file = self.find_config_path()
        
        if config_file is not None:
            with open(config_file) as f:
                self.conf = yaml.safe_load(f)
            if self.new_config:
                self.conf["new"] = True

    def find_config_path(self, config_path=None):
        current_folder = os.path.curdir
        config_file = config_file_home = os.path.join(current_folder, ".uip_config.yml")
        if os.path.exists(config_file):
            logging.warning(f"Project specific config file found.")
        else:
            home_folder = os.path.expanduser("~")
            config_file = config_file_home = os.path.join(home_folder, ".uip_config.yml")
        
        if os.path.exists(config_file):
            logging.info(f"Using config from file : {config_file}")
            return config_file
        else:
            logging.warn(f"Not using any config file. {config_file_home} or {config_file}")
            config_file = self.setup_config(config_file_home)
            self.new_config = True
            return config_file
    
    def setup_config(self, config_file):
        logging.info("You don't have any config file. I think this is the first time you are running this tool.")
        if yes_or_no(f"Do you want to download sample quip config? (Destination: {config_file}): ", default=True):
            response = requests.get("https://stb-se-dev.s3.amazonaws.com/quip/.uip_config.yml.sample")
            if response.ok:
                conf = yaml.safe_load(response.text)
                owner_name = input(f"Enter your name: ")
                conf["extension.yml"]["owner"]["name"] = owner_name

            with open(config_file, "w") as f:
                yaml.dump(conf, f, sort_keys=False)
            
            logging.info(f"Config file created. Check {config_file}")
            cprint("You need to pull the baseline projects. Use the following command.", color="cyan")
            cprint("git clone https://gitlab.stonebranch.com/cs-uac/ue-baseline.git", color="cyan")
            cprint("git clone https://gitlab.stonebranch.com/cs-uac/ut-baseline.git", color="cyan")
            
            self.check_config(conf)

            return config_file
        return None
    
    def check_config(self, conf):
        print(yaml.dump(conf, sort_keys=False))
        # check defaults
        if "defaults" not in conf:
            cprint("Defaults section is missing", color="red")
        else:
            if "template" not in conf["defaults"]:
                cprint("Defaults>template tag is missing", color="red")
            elif len(conf["defaults"]["template"]) == 0:
                cprint("Defaults>template value is empty.", color="red")
            
            if "bootstrap" not in conf["defaults"]:
                cprint("Defaults>bootstrap tag is missing", color="red")
            else:
                if "source" not in conf["defaults"]["bootstrap"]:
                    cprint("Defaults>bootstrap>source tag is missing", color="red")
                else:
                    if not os.path.exists(conf["defaults"]["bootstrap"]["source"]):
                        cprint("Defaults>bootstrap>source path is missing.", color="red")
                        cprint("Be sure you use full path of the ue-baseline project. You can clone the project by using the following command.", color="red")
                        cprint("git clone https://gitlab.stonebranch.com/integration-prototypes/ue-baseline.git\n", color="green")

                if "template_source" not in conf["defaults"]["bootstrap"]:
                    cprint("Defaults>bootstrap>template_source tag is missing", color="red")
                else:
                    if not os.path.exists(conf["defaults"]["bootstrap"]["template_source"]):
                        cprint("Defaults>bootstrap>template_source path is missing.", color="red")
                        cprint("Be sure you use full path of the ut-baseline project. You can clone the project by using the following command.", color="red")
                        cprint("git clone https://gitlab.stonebranch.com/integration-prototypes/ut-baseline.git\n", color="green")


class MyDumper(yaml.SafeDumper):
    # HACK: insert blank lines between top-level objects
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 2:
            super().write_line_break()

def run():
    _quip = Quip(log_level=logging.INFO)
    _quip.main()

if __name__ == '__main__':
    _quip = Quip(log_level=logging.INFO)
    _quip.main()
