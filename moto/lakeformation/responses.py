"""Handles incoming lakeformation requests, invokes methods, returns responses."""
import json

from moto.core.responses import BaseResponse
from .models import lakeformation_backends


class LakeFormationResponse(BaseResponse):
    """Handler for LakeFormation requests and responses."""

    def __init__(self):
        super().__init__(service_name="lakeformation")

    @property
    def lakeformation_backend(self):
        """Return backend instance specific for this region."""
        return lakeformation_backends[self.current_account][self.region]


    def create_lf_tag(self):
        if self._get_param("CatalogId") is None:
            catalog_id = "AwsDataCatalog"
        tag_key = self._get_param("TagKey")
        tag_values = self._get_param("TagValues")
        self.lakeformation_backend.create_lf_tag(
            catalog_id=catalog_id,
            tag_key=tag_key,
            tag_values=tag_values,
        )
        # TODO: handle the 50 tag limit
        return


    def list_lf_tags(self):
        lf_tags, next_token = self.lakeformation_backend.list_lf_tags(
            catalog_id=self._get_param("CatalogId"),
            resource_share_type=self._get_param("ResourceShareType"),
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        if lf_tags is None:
            return json.dumps({
                "LFTags": lf_tags,
                "NextToken": next_token
            })
        return json.dumps({
            "LFTags": lf_tags,
            "NextToken": next_token
        })

        # TODO: handle lots of tags
