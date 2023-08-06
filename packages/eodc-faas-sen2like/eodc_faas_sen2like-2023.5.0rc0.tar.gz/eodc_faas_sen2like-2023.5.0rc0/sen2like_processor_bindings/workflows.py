import logging
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
from sen2like_processor_bindings.model import Sen2LikeParameters

logger = logging.getLogger(__name__)


class Sen2LikeProcessor:
    def __init__(self, endpoint_url, namespace="development") -> None:
        self.configuration = argo_workflows.Configuration(host=endpoint_url)
        self.configuration.verify_ssl = False
        self.namespace = namespace

        self.api_client = argo_workflows.ApiClient(self.configuration)
        self.api_instance_workflows = workflow_service_api.WorkflowServiceApi(
            self.api_client
        )

    def submit_workflow(
        self, parameters: Sen2LikeParameters, user_id: str, job_id: str
    ) -> str:
        """Returns workflow name"""
        manifest = IoArgoprojWorkflowV1alpha1Workflow(
            metadata=ObjectMeta(generate_name="sen2like-"),
            spec=IoArgoprojWorkflowV1alpha1WorkflowSpec(
                workflow_template_ref=IoArgoprojWorkflowV1alpha1WorkflowTemplateRef(
                    name="sen2like-dev"
                ),
                arguments=IoArgoprojWorkflowV1alpha1Arguments(
                    parameters=[
                        IoArgoprojWorkflowV1alpha1Parameter(
                            name="sen2like_parameters", value=parameters.json()
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

        logger.info(f"Submitted sen2like workflow {workflow_name}")
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

    def get_output_stac_item_paths(
        self, user_workspace: Path, target_product: str = "L2F"
    ) -> list[Path]:
        stac_item_paths = []
        output_path = user_workspace / "SEN2LIKE/output"

        for tile in output_path.iterdir():
            for item in tile.iterdir():
                if (
                    item.suffix == ".SAFE"
                    and target_product.upper() in item.name
                    and (item.name.startswith("S2") or item.name.startswith("LS"))
                ):  # result either L2F or L2H
                    item_path = item / (item.stem + ".json")
                    stac_item_paths.append(item_path)

        logger.info(f"Found {len(stac_item_paths)} STAC items in path: {output_path}")

        return stac_item_paths
