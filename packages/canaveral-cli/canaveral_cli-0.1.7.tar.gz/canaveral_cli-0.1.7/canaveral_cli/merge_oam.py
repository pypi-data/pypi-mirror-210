"""This module provides the merge_oam function"""
# canaveral_cli/merge_oam.py

def merge_oam(dev: dict, ops: dict):
    merged_yaml = {}
    # Keep header and components from dev
    merged_yaml["apiVersion"] = dev["apiVersion"]
    merged_yaml["kind"] = dev["kind"]
    merged_yaml["metadata"] = dev["metadata"]
    merged_yaml["spec"] = dev["spec"]

    # Add spec.policies and spec.workflow from ops to dev
    if "policies" in ops["spec"]:
        merged_yaml["spec"]["policies"] = ops["spec"]["policies"]
    if "workflow" in ops["spec"]:
        merged_yaml["spec"]["workflow"] = ops["spec"]["workflow"]

    # Add traits from ops to components with same name from dev, keep dev traits
    for dev_comp in merged_yaml["spec"]["components"]:
        for ops_comp in ops["spec"]["components"]:
            if dev_comp["name"] == ops_comp["name"]:
                if "traits" in dev_comp:
                    dev_comp["traits"] += ops_comp["traits"]
                else:
                    dev_comp["traits"] = ops_comp["traits"]

    return merged_yaml

