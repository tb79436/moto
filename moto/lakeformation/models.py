"""LakeFormationBackend class with methods for supported APIs."""

from moto.core import BaseBackend, BackendDict, BaseModel
from moto.logs.exceptions import (
    ResourceAlreadyExistsException
)
from moto.core import BaseModel


class LFTag(BaseModel):
    def __init__(self, catalog_id, tag_key, tag_values):
        self.tag_key = tag_key
        self.tag_values = tag_values
        self.catalog_id = catalog_id
        self.tag = {
            catalog_id: [
                {
                    "tag_key": self.tag_key,
                    "tag_values": self.tag_values
                }
            ]
        }


class DataCatalog(BaseModel):
    def __init__(self, catalog_id):
        self.catalog_id = catalog_id
        self.lf_tags = list()


class LakeFormationBackend(BaseBackend):
    """Implementation of LakeFormation APIs."""

    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)
        self.data_catalogs = {"AwsDataCatalog": {"LFTags": []}}

    def create_lf_tag(self, catalog_id, tag_key, tag_values):
        if catalog_id in self.data_catalogs:
            if tag_key in list(self.data_catalogs.keys()):
                raise ResourceAlreadyExistsException()
        self.data_catalogs[catalog_id]["LFTags"].append(LFTag(catalog_id, tag_key, tag_values))
        return self.data_catalogs[catalog_id]


    def list_lf_tags(self, catalog_id, resource_share_type, max_results, next_token):
        try:
            models_tags = self.data_catalogs[catalog_id]["LFTags"]
            returned_tags = [{'CatalogId': catalog_id, 'TagKey': tag.tag_key, 'TagValues': tag.tag_values} for tag in models_tags]
            next_token = "more"
            return returned_tags, next_token
        except AttributeError:
            return None


lakeformation_backends = BackendDict(LakeFormationBackend, "lakeformation")
