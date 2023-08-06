def get_ammounts_oam_file(oam_file: dict):
    """ Get the number of components, traits, policies, and workflowsteps in an OAM file """
    traits = 0
    for comp in oam_file["components"]:
        if "traits" in comp:
            traits += len(comp["traits"])
    
    policies = len(oam_file["policies"]) if "policies" in oam_file else 0
    workflow = len(oam_file["workflow"]) if "workflow" in oam_file else 0

    return len(oam_file["components"]), traits, policies, workflow