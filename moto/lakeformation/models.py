"""LakeFormationBackend class with methods for supported APIs."""

from moto.core import BaseBackend, BackendDict, BaseModel
from moto.logs.exceptions import (
    ResourceAlreadyExistsException
)
from moto.core import CloudFormationModel


class Tag(CloudFormationModel):
    def __init__(self, catalog_id, tag_key, tag_values):
        self.tag_key = tag_key
        self.tag_values = list()
        self.catalog_id = catalog_id
        self.tag = {"catalog_id": catalog_id, "tag_key": self.tag_key, "tag_values": self.tag_values}
        # {"catalog_id": {
        #     "tag_key": []
        # }}  

    def to_describe_dict(self):
        print(dir(self))

        return {
            "CatalogId": self.catalog_id,
            "TagKey": self.tag_key,
            "TagValues": self.tag_values,
        }


class LakeFormationBackend(BaseBackend):
    """Implementation of LakeFormation APIs."""

    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)
        self.tags = dict()

    # add methods from here

    def create_lf_tag(self, catalog_id, tag_key, tag_values):
        if self.tags.get(catalog_id):
            if tag_key in list(self.tags.get(catalog_id)):
                raise ResourceAlreadyExistsException()

        self.tags[catalog_id] = {"catalog_id": catalog_id, "tag_key": tag_key, "tag_values": tag_values}

        return self.tags[catalog_id]


    def list_lf_tags(self, catalog_id, resource_share_type, max_results, next_token):
        tags = self.tags.get(catalog_id)
        print(tags)
        return tags, {}
        # return lf_tags, next_token


lakeformation_backends = BackendDict(LakeFormationBackend, "lakeformation")
