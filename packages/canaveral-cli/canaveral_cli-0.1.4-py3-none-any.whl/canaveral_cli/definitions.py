"""This module provides funtions to update internal definitions"""
# canaveral_cli/definitions.py

import json
import os
from github import Github
from canaveral_cli import PACKAGEDIR

from canaveral_cli.cue_parser import parse_cue_hc


def clean_cue_file(cue) -> str:
    #* File can have too many tokens
    #* cut off #HealthProbe (and add closing bracket removed by cutting off #HealthProbe)
    hp_idx = cue.find("#HealthProbe: {")
    if hp_idx != -1:
        cue = cue[:hp_idx] + "}"
    #* remove parameters marked with // +usage=Deprecated
    
    depre_idx = cue.find("// +usage=Deprecated")
    while depre_idx != -1:
        # find nearest empty line before and after, delete all in between
        start_idx = cue.rfind("\n\n", 0, depre_idx)
        end_idx = cue.find("\n\n", depre_idx)
        cue = cue[:start_idx] + cue[end_idx:]
        depre_idx = cue.find("// +usage=Deprecated")

    return cue


def get_updated_type_data():
    GITHUB_API_KEY = os.getenv('GITHUB_API_KEY')
    g = Github(GITHUB_API_KEY)
    repo = g.get_repo("kubevela/kubevela")

    for element in ["component", "trait", "policy", "workflowstep"]:
        definitions = repo.get_contents(f'vela-templates/definitions/internal/{element}')
        if type(definitions) == list:
            for definition in definitions:
                # if definition.name != "task.cue":
                #     continue
                cue_file = definition.decoded_content.decode("utf-8")
                
                # If file has "ui-hidden": "true" in the labels, skip it
                if cue_file.find('"ui-hidden": "true"') != -1:
                    print(f"Skipping {element} definition: {definition.name}")
                    # If local file exists, delete it
                    if os.path.exists(PACKAGEDIR/f"data/oam_types/{element}/{definition.name[:-4]}.json"):
                        os.remove(PACKAGEDIR/f"data/oam_types/{element}/{definition.name[:-4]}.json")
                    continue
                
                # cue_file = clean_cue_file(cue_file)
                print(f'Parsing {element} definition: {definition.name}')
                parsed_dict = parse_cue_hc(cue_file)
                type_name = parsed_dict["name"]
                with open(PACKAGEDIR/f"data/oam_types/{element}/{type_name}.json", "w") as f:
                    f.write(json.dumps(parsed_dict))
                    f.close()
        else:
            raise Exception("No component definitions found in the Kubevela repository")
        