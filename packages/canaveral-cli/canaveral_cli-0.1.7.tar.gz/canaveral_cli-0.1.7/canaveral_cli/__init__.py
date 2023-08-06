"""Top-level package for Canaveral"""
# canaveral_cli/__init__.py

import os
from dotenv import load_dotenv
from pathlib import Path
import logging

load_dotenv()

__app_name__ = "canaveral"
__version__ = "0.1.0"
PACKAGEDIR = Path(__file__).parent.absolute()

# check if form_data directory exists in home directory
if not os.path.isdir(Path.home() / "form_data"):
    os.mkdir(Path.home() / "form_data")

logging.basicConfig(filename=Path.home() / 'form_data/canaveral.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

# COMPONENT_TYPES = ["webservice", "task", "cron-task", "daemon", "k8s-objects"]
# TRAIT_TYPES = ["affinity", "annotations", "command", "container-image", "cpuscaler", "env", "expose", "gateway", "hostalias", "hpa", "init-container", "json-merge-patch", "json-patch",
#                "k8s-update-strategy", "labels", "lifecycle", "nocalhost", "resource", "scaler", "service-account", "service-binding", "sidecar", "startup-probe", "storage", "topologyspreadconstraints"]
# POLICY_TYPES = ["apply-once", "garbage-collect", "health", "override",
#                 "read-only", "replication", "shared-resource", "take-over", "topology"]
# WORKFLOWSTEP_TYPES = ["addon-operation", "apply-app", "apply-component", "apply-deployment", "apply-object", "apply-terraform-config", "apply-terraform-provider", "build-push-image", "clean-jobs", "collect-service-endpoints", "create-config", "delete-config", "depends-on-app", "deploy",
#                       "deploy-cloud-resource", "export-data", "export2config", "export2secret", "generate-jdbc-connection", "list-config", "notification", "print-message-in-status", "read-app", "read-config", "read-object", "request", "share-cloud-resource", "step-group", "suspend", "vela-cli", "webhook"]
COMPONENT_TYPES = []
TRAIT_TYPES = []
POLICY_TYPES = []
WORKFLOWSTEP_TYPES = []
