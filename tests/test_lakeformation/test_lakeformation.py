"""Unit tests for lakeformation-supported APIs."""
import boto3

# import sure  # noqa # pylint: disable=unused-import
from moto import mock_lakeformation

# See our Development Tips on writing tests for hints on how to write good tests:
# http://docs.getmoto.org/en/latest/docs/contributing/development_tips/tests.html


@mock_lakeformation
def test_create_lf_tag():
    lf_client = boto3.client("lakeformation", region_name="us-east-1")
    catalog_id = "default_catalog_id"
    tag_key = "tag_key_bla"
    tag_values = ["tag_value_1", "tag_value_2"]

    response = lf_client.create_lf_tag(TagKey=tag_key, TagValues=tag_values)
    # print(f"{response=}")

    response = lf_client.list_lf_tags()
    print(response)
    # assert response == "Added tags"

#     raise Exception("NotYetImplemented")


# @mock_lakeformation
# def test_list_lf_tags():
#     client = boto3.client("lakeformation", region_name="us-east-2")
#     resp = client.list_lf_tags()

#     raise Exception("NotYetImplemented")
