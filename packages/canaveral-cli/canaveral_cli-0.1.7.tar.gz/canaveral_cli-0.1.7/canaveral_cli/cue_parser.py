"""This module provides the Cue Parser"""
# canaveral_cli/cue_parser.py

import re
# from langchain.chat_models import ChatOpenAI
# from langchain.prompts.chat import (
#     ChatPromptTemplate,
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
# )


# def parse_cue_llm(file: str) -> dict:
#     OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

#     chat = ChatOpenAI(client=OPENAI_API_KEY, temperature=0)

#     system_message_prompt = SystemMessagePromptTemplate.from_template(
#         """You will receive a CUE file for a configuration of a Kubernetes object. 
#         Parse the CUE file and return the name, description, type and parameters in the format of a json file.
#         If the file has "ui-hidden": "true" in the labels, return an empty json file.""")
#     human_message_prompt = HumanMessagePromptTemplate.from_template("{file}")

#     chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

#     start = time.time()
#     response = chat(chat_prompt.format_prompt(file=file).to_messages())
#     print(f"Time to get response: {time.time() - start:.2f} seconds")
#     print(response.content)
#     return json.loads(response.content)

#     return {'type': 'component', 
#             'name': 'cronjob', 
#             'description': 'Describes cron jobs that run code or a script to completion.', 
#             'paramet': {'labels': 'string', 'annotations': 'int'}
#             }


def rem_quotation_marks(string: str) -> str:
    if string.startswith('"') and string.endswith('"'):
        return string[1:-1]
    return string

def parse_cue_hc(file: str) -> dict:
    # Go line by line and parse the file
    oam_file = {}
    current_parameter = {}
    state = 'name'
    for _, line in enumerate(file.splitlines()):
        # catch import and ignore inside of parens
        if line.startswith('import'):
            state = 'import'
        if state == 'import' and line.startswith(')'):
            state = 'name'
        if state == 'import':
            continue
        
        # catch name of type:
        if state == 'name' and line.find(': {') != -1:
            oam_file["name"] = line.split(':')[0]
            # if name has "", remove them
            oam_file["name"] = rem_quotation_marks(oam_file["name"])
            state = 'type-description-2'
            continue

        # description and type are at the same level, either one can appear first
        if (state == "type-description-2" or state == "type-description") and (line.find('description') != -1 or line.find('type') != -1):
            if line.find('description:') != -1:
                oam_file["description"] = line.split('description:')[1].strip()
                oam_file["description"] = rem_quotation_marks(oam_file["description"])
            if line.find('type:') != -1:
                oam_file["type"] = line.split('type:')[1].strip()
                oam_file["type"] = rem_quotation_marks(oam_file["type"])
            state = 'type-description' if state == 'type-description-2' else 'find-parameters'
            continue
        
        
        # catch parameters start
        if state == 'find-parameters' and line.startswith('\tparameter: '):
            oam_file["parameters"] = []
            if line.startswith('\tparameter: {'):
                state = 'parameter-list'
                continue
            else:
                # Specific case -> parameter: [string]: string | null
                current_parameter["name"] = None
                current_parameter["type"] = line.split('parameter: ')[1].strip()
                oam_file["parameters"].append(current_parameter)
                break
            
        # Ignore current parameter until new one
        if state == 'ignore-parameter' and (line.find('\n\n') != -1 or line.startswith('\t\t// +usage')):
            # Corner case in trait/expose.cue for line.startswith('\t\t// +usage')
            state = 'parameter-list'
            continue
        # Ignore current parameter, but if it is the last one, break
        if (state == 'ignore-parameter' or state == 'parameter-list') and line.startswith('\t}'):
            break
            # ignore parameter until blank line
        # skip blank lines between parameters
        if state == 'parameter-list' and line == '':
            continue

        # Parameters with comments. 
        # If in list and find comment, enter comment list
        # If already in comment list, keep here if find //
        if (state == 'parameter-list' or state == 'parameter-comment') and line.startswith('\t\t//'):
            if state == 'parameter-list':
                current_parameter = {}
            try:
                comment_type = line.split('=')[0].split('+')[1].strip()
                # print(f'comment_type: {comment_type}')
            except:
                # Corner case in policy/read-only.cue. Normal comment bellow informative comment
                if line.find('=') == -1:
                    continue
            else:
                match comment_type:
                    case 'usage':
                        if line.find('Deprecated') != -1:
                            state = 'ignore-parameter'
                            continue
                        else:
                            current_parameter["usage"] = line.split('=')[1].strip()
                    case 'short':
                        current_parameter["short"] = line.split('=')[1].strip()
                    case 'ignore':
                        state = 'ignore-parameter'
                        continue
                    case _:
                        raise Exception(f'Unknown comment type: {comment_type} in {oam_file["name"]}')
                state = 'parameter-comment'
                continue
            
        # if in comment and didn't find //, in parameter name
        # OR
        # if in parameter list and didn't find //, in parameter name
        if (state == 'parameter-comment') or (state == 'parameter-list' and re.search("^\t{2}[^\t\n:]+:[^\n]+", line)):
            name = line.split(':', 1)[0].strip()
            type_par = line.split(':', 1)[1].strip()
            #TODO Extract default value

            # If name has a ?, remove it and add current parameter["labels"] = false
            current_parameter['mandatory'] = True if name.find('?') == -1 else False
            name = name.replace('?', '') if name.find('?') != -1 else name

            current_parameter["name"] = name
            current_parameter["type"] = type_par
            oam_file["parameters"].append(current_parameter)
            # print(f'current_parameter appended: {current_parameter}')
            state = 'parameter-list'
            continue

        # Parameters can not have comments on top e.g.apply-deployment.cue
        

    return oam_file