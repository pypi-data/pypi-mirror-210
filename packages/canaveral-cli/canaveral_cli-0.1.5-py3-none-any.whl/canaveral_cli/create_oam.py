"""This module provides the functions to create OAM files"""
# canaveral_cli/create_oam.py

import json
import os
import jinja2
import typer
from rich import print
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator

from canaveral_cli import COMPONENT_TYPES, PACKAGEDIR, TRAIT_TYPES, POLICY_TYPES, WORKFLOWSTEP_TYPES

used_component_names = []
used_workflowstep_names = []

def get_type_data():
    for pair in [("component", COMPONENT_TYPES), ("trait", TRAIT_TYPES), ("policy", POLICY_TYPES), ("workflowstep", WORKFLOWSTEP_TYPES)]:
        for type_file in os.scandir(PACKAGEDIR/f"data/oam_types/{pair[0]}"):
            with open(type_file.path, "r") as f:
                pair[1].append(json.load(f))
                f.close()

    # move component with name webservice to first in list COMPONENT_TYPES
    for idx, component in enumerate(COMPONENT_TYPES):
        if component["name"] == "webservice":
            COMPONENT_TYPES.insert(0, COMPONENT_TYPES.pop(idx))
            break


def create_oam_file(oam_file_data: dict):
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(PACKAGEDIR/"data/templates/"), trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template('vela_template.yaml.jinja')
    with open("vela.yaml", "w") as f:
        f.write(template.render(oam_file_data))
        f.close()
    print("\nThe created file is most likely [bold red]incomplete[/bold red].",
         "Please check it and fill the missing fields by consulting the [link=https://kubevela.io/docs/end-user/components/references]docs[/]", sep=os.linesep)
    typer.confirm(text="Confirm [Enter]", default=True, show_default=False)
    print("✅ vela.yaml created successfully! ")


def create_choice_list_component(components: list[dict]):
    choice_list = []
    for idx, component in enumerate(components):
        choice_list.append(Choice(name=component["name"], value=idx))
    return choice_list


def validator_name(name: str) -> bool:
    return True if len(name) > 0 and len(name) <= 63 and name[0].isalnum() and name[-1].isalnum() and all(
        [char.isalnum() or char in ["-", "_", "."] for char in name]) else False


def validator_component_name(name: str) -> bool:
    # The name segment is required and must be 63 characters or less,
    # beginning and ending with an alphanumeric character ([a-z0-9A-Z])
    # with dashes (-), underscores (_), dots (.), and alphanumerics between.
    # It cannot be empty or contain spaces.
    # It cannot be repeated between component names
    return True if len(name) > 0 and len(name) <= 63 and name[0].isalnum() and name[-1].isalnum() and all(
        [char.isalnum() or char in ["-", "_", "."] for char in name]) and name not in used_component_names else False


def validator_workflowstep_name(name: str) -> bool:
    # The name segment is required and must be 63 characters or less,
    # beginning and ending with an alphanumeric character ([a-z0-9A-Z])
    # with dashes (-), underscores (_), dots (.), and alphanumerics between.
    # It cannot be empty or contain spaces.
    # It cannot be repeated between workflowstep names
    return True if len(name) <= 63 and name[0].isalnum() and name[-1].isalnum() and all(
        [char.isalnum() or char in ["-", "_", "."] for char in name]) and name not in used_workflowstep_names else False


def oam_form():
    get_type_data()
    oam_file_data = {}
    used_component_names.clear()
    print("This tool will help you create a Vela file for your application.",
          "The file is made up of four sections: [green]components[/], [blue]traits[/], [yellow]policies[/] and [purple]workflowsteps[/].",
          "Information will be gathered through a series of questions, and details will be given throughout the process.", sep=os.linesep)
    typer.confirm(text="Confirm [Enter]", default=True, show_default=False)

    oam_file_data["app_name"] = inquirer.text(
        message="What is the name of the application? (without spaces)",
        validate=validator_name,
    ).execute()

    print("\n[bold green]COMPONENTS[/]",
          "Components are the building blocks of your application. They are the smallest unit of your application that can be independently deployed and managed.",
          "To define a component, we need a name, a type and a Docker image. Let's start with the first one.", sep=os.linesep)

    # COMPONENTS
    oam_file_data["components"] = []
    components_number = 1

    component_name = inquirer.text(
        message="What is the name of the component?",
        validate=validator_component_name,
    ).execute()

    print("\n[b]Types[/] are a contruct of OAM, they are used to define the type of component you are using.",
          "If in doubt, use [u]webservice[/u]. For something more specific, check the available component types in the [link=https://kubevela.io/docs/end-user/components/references]docs[/link].",
          sep=os.linesep)

    component_type_name = inquirer.fuzzy(
        message=f'What is the type of component "{component_name}"?',
        choices=[c['name'] for c in COMPONENT_TYPES],
    ).execute()
    component_image = inquirer.text(
        message=f'What is the Docker image of component "{component_name}"?',
        validate=EmptyInputValidator(),
    ).execute()

    component_type = next(
        (component for component in COMPONENT_TYPES if component["name"] == component_type_name), None)

    component = {"name": component_name,
                 "type": component_type,
                 "image": component_image,
                 }
    oam_file_data["components"].append(component)
    used_component_names.append(component_name)

    another_component = inquirer.confirm(
        message="Do you want to add another component?",
    ).execute()
    while another_component:
        components_number += 1
        component_name = inquirer.text(
            message="What is the name of the component?",
            validate=validator_component_name,
        ).execute()
        component_type_name = inquirer.fuzzy(
            message=f'What is the type of component "{component_name}"?',
            choices=[c['name'] for c in COMPONENT_TYPES],
        ).execute()
        component_image = inquirer.text(
            message=f'What is the Docker image of component "{component_name}"?',
            validate=EmptyInputValidator(),
        ).execute()

        component_type = next(
            (component for component in COMPONENT_TYPES if component["name"] == component_type_name), None)

        component = {"name": component_name,
                     "type": component_type,
                     "image": component_image,
                     }
        oam_file_data["components"].append(component)
        used_component_names.append(component_name)
        another_component = inquirer.confirm(
            message="Do you want to add another component?",
        ).execute()

    print("\n[bold blue]TRAITS[/] - Optional", 
          "Traits are used to add [u]extra functionality to your components[/]. They are optional, but you can add as many as you want.", 
          "Information about available traits can be found in the [link=https://kubevela.io/docs/end-user/traits/references]docs[/link].", sep=os.linesep)

    # TRAITS
    mess = "Do you want to add traits to any of the components?" if components_number > 1 else (
        f"Do you want to add traits to the component {component_name}?")
    traits = inquirer.confirm(
        message=mess,
    ).execute()

    while traits:
        if components_number == 1:
            current_comp_idx: int = 0
        else:
            print(f'There are {components_number} components')
            current_comp_idx: int = int(inquirer.rawlist(
                message="Which component do you want to add traits to?",
                choices=create_choice_list_component(
                    oam_file_data["components"]),
                default=None,
            ).execute())

        oam_file_data["components"][current_comp_idx]["traits"] = [
        ] if "traits" not in oam_file_data["components"][current_comp_idx] else oam_file_data["components"][current_comp_idx]["traits"]

        trait_type_name = inquirer.fuzzy(
            message="What is the type of the trait?",
            choices=[t['name'] for t in TRAIT_TYPES],
        ).execute()

        trait_type = next(
            (trait for trait in TRAIT_TYPES if trait["name"] == trait_type_name), None)

        trait = {"type": trait_type}
        oam_file_data["components"][current_comp_idx]["traits"].append(trait)

        another_trait = inquirer.confirm(
            message=f"Do you want to add another trait to component {oam_file_data['components'][current_comp_idx]['name']}?",
        ).execute()
        while another_trait:
            trait_type_name = inquirer.fuzzy(
                message="What is the type of the trait?",
                choices=[t['name'] for t in TRAIT_TYPES],
            ).execute()

            trait_type = next(
                (trait for trait in TRAIT_TYPES if trait["name"] == trait_type_name), None)

            trait = {"type": trait_type}
            oam_file_data["components"][current_comp_idx]["traits"].append(
                trait)
            another_trait = inquirer.confirm(
                message="Do you want to add another trait to the component?",
            ).execute()

        if components_number > 1:
            traits = inquirer.confirm(
                message="Do you want to add more traits to any of the components?",
            ).execute()
        else:
            traits = False

    # POLICIES
    print("\n[bold yellow]POLICIES[/] - Optional", 
          "Policies are used to add [u]extra functionality to your application[/]. They are optional, but you can add as many as you want.",
          "Information about available policies can be found in the [link=https://kubevela.io/docs/end-user/policies/references]docs[/link].", sep=os.linesep)

    policies = inquirer.confirm(
        message="Do you want to add policies to the application?",
    ).execute()

    if policies:
        oam_file_data["policies"] = []

        policy_type_name = inquirer.fuzzy(
            message="What is the type of the policy?",
            choices=[p['name'] for p in POLICY_TYPES],
        ).execute()
        policy_name = inquirer.text(
            message="What is the name of the policy?",
            validate=validator_name,
        ).execute()
        policy_type = next(
            (policy for policy in POLICY_TYPES if policy["name"] == policy_type_name), None)
        policy = {"name": policy_name,
                  "type": policy_type,
                  }
        oam_file_data["policies"].append(policy)

        another_policy = inquirer.confirm(
            message="Do you want to add another policy?",
        ).execute()
        while another_policy:
            policy_type_name = inquirer.fuzzy(
                message="What is the type of the policy?",
                choices=[p['name'] for p in POLICY_TYPES],
            ).execute()
            policy_name = inquirer.text(
                message="What is the name of the policy?",
                validate=validator_name,
            ).execute()
            policy_type = next(
                (policy for policy in POLICY_TYPES if policy["name"] == policy_type_name), None)
            policy = {"name": policy_name,
                      "type": policy_type,
                      }
            oam_file_data["policies"].append(policy)
            another_policy = inquirer.confirm(
                message="Do you want to add another policy?",
            ).execute()

    # WORKFLOW
    print("\n[bold purple]WORKFLOW[/] - Optional",
          "A workflow is used to [u]describe the steps to deploy your application[/]. It is optional, but you can define as many steps as you want.",
          "Information about available workflow steps can be found in the [link=https://kubevela.io/docs/end-user/workflow/built-in-workflow-defs]docs[/link].", sep=os.linesep)

    workflow = inquirer.confirm(
        message="Do you want to add a workflow to the application?",
    ).execute()

    if workflow:
        oam_file_data["workflow"] = []
        used_workflowstep_names.clear()
        print("The workflow is composed of a list of steps")
        workflow_step_type_name = inquirer.fuzzy(
            message="What is the first step?",
            choices=[w['name'] for w in WORKFLOWSTEP_TYPES],
        ).execute()
        workflow_step_name = inquirer.text(
            message="What is the name of the first step?",
            validate=validator_workflowstep_name,
        ).execute()
        workflow_step_type = next(
            (workflowstep for workflowstep in WORKFLOWSTEP_TYPES if workflowstep["name"] == workflow_step_type_name), None)
        workflow_step = {"name": workflow_step_name,
                         "type": workflow_step_type,
                         }
        oam_file_data["workflow"].append(workflow_step)

        another_step = inquirer.confirm(
            message="Do you want to add another step?",
        ).execute()
        while another_step:
            workflow_step_type_name = inquirer.fuzzy(
                message="What is the next step?",
                choices=[w['name'] for w in WORKFLOWSTEP_TYPES],
            ).execute()
            workflow_step_name = inquirer.text(
                message="What is the name of the next step?",
                validate=validator_workflowstep_name,
            ).execute()
            workflow_step_type = next(
                (workflowstep for workflowstep in WORKFLOWSTEP_TYPES if workflowstep["name"] == workflow_step_type_name), None)
            workflow_step = {"name": workflow_step_name,
                             "type": workflow_step_type,
                             }
            oam_file_data["workflow"].append(workflow_step)
            another_step = inquirer.confirm(
                message="Do you want to add another step?",
            ).execute()

    return oam_file_data
