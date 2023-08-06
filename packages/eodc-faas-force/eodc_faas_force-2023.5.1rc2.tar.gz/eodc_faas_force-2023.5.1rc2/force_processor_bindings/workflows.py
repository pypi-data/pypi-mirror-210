import logging
import re
from pathlib import Path
from time import sleep

import argo_workflows
from argo_workflows.api import workflow_service_api
from argo_workflows.model.io_argoproj_workflow_v1alpha1_arguments import (
    IoArgoprojWorkflowV1alpha1Arguments,
)
from argo_workflows.model.io_argoproj_workflow_v1alpha1_parameter import (
    IoArgoprojWorkflowV1alpha1Parameter,
)
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow import (
    IoArgoprojWorkflowV1alpha1Workflow,
)
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_create_request import (
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest,
)
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_spec import (
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
)
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_template_ref import (
    IoArgoprojWorkflowV1alpha1WorkflowTemplateRef,
)
from argo_workflows.model.object_meta import ObjectMeta
from force_processor_bindings.model import ForceParameters
from pystac import Collection, Item

logger = logging.getLogger(__name__)


LABEL_VALIDATION_REGEX = r"(([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?"


class ForceProcessor:
    def __init__(self, endpoint_url, namespace="development") -> None:
        self.configuration = argo_workflows.Configuration(host=endpoint_url)
        self.configuration.verify_ssl = False
        self.namespace = namespace

        self.api_client = argo_workflows.ApiClient(self.configuration)
        self.api_instance_workflows = workflow_service_api.WorkflowServiceApi(
            self.api_client
        )

    def submit_workflow(
        self, parameters: ForceParameters, user_id: str, job_id: str
    ) -> str:
        """Returns workflow name"""
        re.match(LABEL_VALIDATION_REGEX, user_id)
        re.match(LABEL_VALIDATION_REGEX, job_id)

        manifest = IoArgoprojWorkflowV1alpha1Workflow(
            metadata=ObjectMeta(generate_name="force-"),
            spec=IoArgoprojWorkflowV1alpha1WorkflowSpec(
                workflow_template_ref=IoArgoprojWorkflowV1alpha1WorkflowTemplateRef(
                    # see name in
                    # faas-force/deploy/templates/WorkflowTemplates/force.yaml
                    name="faas-force"
                ),
                arguments=IoArgoprojWorkflowV1alpha1Arguments(
                    parameters=[
                        IoArgoprojWorkflowV1alpha1Parameter(
                            name="force_parameters", value=parameters.json()
                        ),
                        IoArgoprojWorkflowV1alpha1Parameter(
                            name="user_id", value=user_id
                        ),
                        IoArgoprojWorkflowV1alpha1Parameter(
                            name="job_id", value=job_id
                        ),
                    ]
                ),
            ),
        )

        created_workflow = self.api_instance_workflows.create_workflow(
            namespace=self.namespace,
            body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=manifest),
            _check_return_type=False,
        )

        workflow_name = created_workflow.metadata.get("name")

        logger.info(f"Submitted FORCE workflow with ID {workflow_name}")
        return workflow_name

    def wait_for_completion(self, workflow_name: str) -> None:
        """Repeatedly query workflow status until it changes to a completed state"""

        def get_workflow_status(workflow_name: str) -> dict:
            status = self.api_instance_workflows.get_workflow(
                namespace=self.namespace,
                name=workflow_name,
                fields="status.phase,status.finishedAt,status.startedAt",
                _check_return_type=False,
            ).get("status", {})
            return status

        while (status := get_workflow_status(workflow_name)).get("finishedAt") is None:
            logger.info("Workflow still running, sleeping 30 seconds")
            sleep(30)
        logger.info(f"Workflow completed with status {status.get('phase')}.")

        if status.get("phase") in ("Failed", "Error"):
            raise ValueError(
                f"Workflow {workflow_name} ended with status {status.get('phase')}"
            )

    @staticmethod
    def get_output_stac_items(user_workspace: Path) -> list[Item]:
        output_path = user_workspace / "FORCE/output/STAC"

        collection_file = list(output_path.glob("*_collection.json"))[0]
        force_output_collection = Collection.from_file(str(collection_file))
        stac_items = [
            Item.from_file(link.get_absolute_href())
            for link in force_output_collection.get_item_links()
        ]

        return stac_items
