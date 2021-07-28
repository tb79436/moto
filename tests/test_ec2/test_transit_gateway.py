import boto3
import sure  # noqa
from moto import mock_ec2
from moto.core import ACCOUNT_ID


@mock_ec2
def test_describe_transit_gateways():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    response = ec2.describe_transit_gateways()
    response.should.have.key("TransitGateways").equal([])


@mock_ec2
def test_create_transit_gateway():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    response = ec2.create_transit_gateway(
        Description="my first gateway", Options={"DnsSupport": "disable"}
    )
    gateway = response["TransitGateway"]
    gateway.should.have.key("TransitGatewayId").match("tgw-[a-z0-9]+")
    gateway.should.have.key("State").equal("available")
    gateway.should.have.key("OwnerId").equal(ACCOUNT_ID)
    gateway.should.have.key("Description").equal("my first gateway")
    gateway.should.have.key("Tags").equal([])
    options = gateway["Options"]
    options.should.have.key("AmazonSideAsn").equal(64512)
    options.should.have.key("TransitGatewayCidrBlocks").equal([])
    options.should.have.key("AutoAcceptSharedAttachments").equal("disable")
    options.should.have.key("DefaultRouteTableAssociation").equal("enable")
    options.should.have.key("DefaultRouteTablePropagation").equal("enable")
    options.should.have.key("PropagationDefaultRouteTableId").match("tgw-rtb-[a-z0-9]+")
    options.should.have.key("VpnEcmpSupport").equal("enable")
    options.should.have.key("DnsSupport").equal("disable")
    #
    # Verify we can retrieve it
    response = ec2.describe_transit_gateways()
    gateways = response["TransitGateways"]
    gateways.should.have.length_of(1)
    gateways[0].should.have.key("CreationTime")
    gateways[0].should.have.key("TransitGatewayArn").equal(
        "arn:aws:ec2:us-east-1:{}:transit-gateway/{}".format(
            ACCOUNT_ID, gateway["TransitGatewayId"]
        )
    )
    gateways[0]["Options"].should.have.key("AssociationDefaultRouteTableId").equal(
        gateways[0]["Options"]["PropagationDefaultRouteTableId"]
    )
    del gateways[0]["CreationTime"]
    del gateways[0]["TransitGatewayArn"]
    del gateways[0]["Options"]["AssociationDefaultRouteTableId"]
    gateway.should.equal(gateways[0])


@mock_ec2
def test_create_transit_gateway_with_tags():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    response = ec2.create_transit_gateway(
        Description="my first gateway",
        TagSpecifications=[
            {
                "ResourceType": "transit-gateway",
                "Tags": [
                    {"Key": "tag1", "Value": "val1"},
                    {"Key": "tag2", "Value": "val2"},
                ],
            }
        ],
    )
    gateway = response["TransitGateway"]
    gateway.should.have.key("TransitGatewayId").match("tgw-[a-z0-9]+")
    tags = gateway.get("Tags", [])
    tags.should.have.length_of(2)
    tags.should.contain({"Key": "tag1", "Value": "val1"})
    tags.should.contain({"Key": "tag2", "Value": "val2"})


@mock_ec2
def test_delete_transit_gateway():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    g = ec2.create_transit_gateway(Description="my first gateway")["TransitGateway"]
    ec2.describe_transit_gateways()["TransitGateways"].should.have.length_of(1)

    ec2.delete_transit_gateway(TransitGatewayId=g["TransitGatewayId"])
    ec2.describe_transit_gateways()["TransitGateways"].should.have.length_of(0)


@mock_ec2
def test_modify_transit_gateway():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    g = ec2.create_transit_gateway(Description="my first gatway")["TransitGateway"]
    ec2.describe_transit_gateways()["TransitGateways"].should.have.length_of(1)
    ec2.describe_transit_gateways()["TransitGateways"][0]["Description"].should.equal(
        "my first gatway"
    )

    ec2.modify_transit_gateway(
        TransitGatewayId=g["TransitGatewayId"], Description="my first gateway"
    )
    ec2.describe_transit_gateways()["TransitGateways"].should.have.length_of(1)
    ec2.describe_transit_gateways()["TransitGateways"][0]["Description"].should.equal(
        "my first gateway"
    )


@mock_ec2
def test_describe_transit_gateway_vpc_attachments():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    response = ec2.describe_transit_gateway_vpc_attachments()
    response.should.have.key("TransitGatewayVpcAttachments").equal([])


@mock_ec2
def test_describe_transit_gateway_attachments():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    response = ec2.describe_transit_gateway_attachments()
    response.should.have.key("TransitGatewayAttachments").equal([])


@mock_ec2
def test_create_transit_gateway_vpc_attachment():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    response = ec2.create_transit_gateway_vpc_attachment(
        TransitGatewayId="gateway_id", VpcId="some-vpc-id", SubnetIds=["sub1"]
    )
    attachment = response["TransitGatewayVpcAttachment"]
    attachment.should.have.key("TransitGatewayAttachmentId").match("tgw-attach-*")
    attachment.should.have.key("TransitGatewayId").equal("gateway_id")
    attachment.should.have.key("VpcId").equal("some-vpc-id")
    attachment.should.have.key("VpcOwnerId").equal(ACCOUNT_ID)
    attachment.should.have.key("State").equal("available")
    attachment.should.have.key("SubnetIds").equal(["sub1"])
    attachment.should.have.key("Options").equal(
        {
            "DnsSupport": "enable",
            "Ipv6Support": "disable",
            "ApplianceModeSupport": "disable",
        }
    )
    attachment.should.have.key("Tags").equal([])
    #
    # Verify we can retrieve it as a VPC attachment
    attachments = ec2.describe_transit_gateway_vpc_attachments()[
        "TransitGatewayVpcAttachments"
    ]
    attachments.should.have.length_of(1)
    attachments[0].should.have.key("CreationTime")
    del attachments[0]["CreationTime"]
    attachment.should.equal(attachments[0])
    #
    # Verify we can retrieve it as a general attachment
    attachments = ec2.describe_transit_gateway_attachments()[
        "TransitGatewayAttachments"
    ]
    attachments.should.have.length_of(1)
    attachments[0].should.have.key("CreationTime")
    attachments[0].should.have.key("TransitGatewayOwnerId").equal(ACCOUNT_ID)
    attachments[0].should.have.key("ResourceOwnerId").equal(ACCOUNT_ID)
    attachments[0].should.have.key("ResourceType").equal("vpc")
    attachments[0].should.have.key("ResourceId").equal("some-vpc-id")
    attachments[0].should.have.key("State").equal("available")
    attachments[0].should.have.key("Tags").equal([])
    attachments[0].should.have.key("TransitGatewayAttachmentId").equal(
        attachment["TransitGatewayAttachmentId"]
    )
    attachments[0].should.have.key("TransitGatewayId").equal("gateway_id")


@mock_ec2
def test_describe_transit_gateway_route_tables():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    response = ec2.describe_transit_gateway_route_tables()
    response.should.have.key("TransitGatewayRouteTables").equal([])


@mock_ec2
def test_create_transit_gateway_route_table():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    tables = ec2.describe_transit_gateway_route_tables()["TransitGatewayRouteTables"]
    tables.should.equal([])

    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    table = ec2.create_transit_gateway_route_table(TransitGatewayId=gateway_id)[
        "TransitGatewayRouteTable"
    ]
    table.should.have.key("TransitGatewayRouteTableId").match("tgw-rtb-[0-9a-z]+")
    table.should.have.key("TransitGatewayId").equals(gateway_id)
    table.should.have.key("State").equals("available")
    table.should.have.key("DefaultAssociationRouteTable").equals(False)
    table.should.have.key("DefaultPropagationRouteTable").equals(False)
    table.should.have.key("CreationTime")
    table.should.have.key("Tags").equals([])

    tables = ec2.describe_transit_gateway_route_tables()["TransitGatewayRouteTables"]
    tables.should.have.length_of(1)
    tables[0].should.equal(table)


@mock_ec2
def test_create_transit_gateway_route_table_with_tags():
    ec2 = boto3.client("ec2", region_name="us-west-1")

    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    response = ec2.create_transit_gateway_route_table(
        TransitGatewayId=gateway_id,
        TagSpecifications=[
            {
                "ResourceType": "transit-gateway-route-table",
                "Tags": [
                    {"Key": "tag1", "Value": "val1"},
                    {"Key": "tag2", "Value": "val2"},
                ],
            }
        ],
    )
    table = response["TransitGatewayRouteTable"]
    table["Tags"].should.have.length_of(2)
    table["Tags"].should.contain({"Key": "tag1", "Value": "val1"})
    table["Tags"].should.contain({"Key": "tag2", "Value": "val2"})


@mock_ec2
def test_delete_transit_gateway_route_table():
    ec2 = boto3.client("ec2", region_name="us-west-1")

    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    table = ec2.create_transit_gateway_route_table(TransitGatewayId=gateway_id)[
        "TransitGatewayRouteTable"
    ]

    tables = ec2.describe_transit_gateway_route_tables()["TransitGatewayRouteTables"]
    tables.should.have.length_of(1)

    ec2.delete_transit_gateway_route_table(
        TransitGatewayRouteTableId=table["TransitGatewayRouteTableId"]
    )

    tables = ec2.describe_transit_gateway_route_tables()["TransitGatewayRouteTables"]
    tables.should.have.length_of(0)


@mock_ec2
def test_search_transit_gateway_routes_empty():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    table_id = ec2.create_transit_gateway_route_table(TransitGatewayId=gateway_id)[
        "TransitGatewayRouteTable"
    ]["TransitGatewayRouteTableId"]

    response = ec2.search_transit_gateway_routes(
        TransitGatewayRouteTableId=table_id,
        Filters=[{"Name": "state", "Values": ["active"]}],
    )
    response.should.have.key("Routes").equal([])
    response.should.have.key("AdditionalRoutesAvailable").equal(False)


@mock_ec2
def test_create_transit_gateway_route():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    table_id = ec2.create_transit_gateway_route_table(TransitGatewayId=gateway_id)[
        "TransitGatewayRouteTable"
    ]["TransitGatewayRouteTableId"]

    route = ec2.create_transit_gateway_route(
        DestinationCidrBlock="0.0.0.0", TransitGatewayRouteTableId=table_id
    )["Route"]

    route.should.have.key("DestinationCidrBlock").equal("0.0.0.0")
    route.should.have.key("Type").equal("TODO")
    route.should.have.key("State").equal("active")


@mock_ec2
def test_create_transit_gateway_route_as_blackhole():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    table_id = ec2.create_transit_gateway_route_table(TransitGatewayId=gateway_id)[
        "TransitGatewayRouteTable"
    ]["TransitGatewayRouteTableId"]

    route = ec2.create_transit_gateway_route(
        DestinationCidrBlock="192.168.0.1",
        TransitGatewayRouteTableId=table_id,
        Blackhole=True,
    )["Route"]

    route.should.have.key("DestinationCidrBlock").equal("192.168.0.1")
    route.should.have.key("Type").equal("TODO")
    route.should.have.key("State").equal("blackhole")


@mock_ec2
def test_search_transit_gateway_routes_by_state():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    table_id = ec2.create_transit_gateway_route_table(TransitGatewayId=gateway_id)[
        "TransitGatewayRouteTable"
    ]["TransitGatewayRouteTableId"]

    ec2.create_transit_gateway_route(
        DestinationCidrBlock="192.168.0.0", TransitGatewayRouteTableId=table_id
    )

    ec2.create_transit_gateway_route(
        DestinationCidrBlock="192.168.0.1",
        TransitGatewayRouteTableId=table_id,
        Blackhole=True,
    )

    routes = ec2.search_transit_gateway_routes(
        TransitGatewayRouteTableId=table_id,
        Filters=[{"Name": "state", "Values": ["active"]}],
    )["Routes"]

    routes.should.equal(
        [{"DestinationCidrBlock": "192.168.0.0", "Type": "TODO", "State": "active"}]
    )

    routes = ec2.search_transit_gateway_routes(
        TransitGatewayRouteTableId=table_id,
        Filters=[{"Name": "state", "Values": ["blackhole"]}],
    )["Routes"]

    routes.should.equal(
        [{"DestinationCidrBlock": "192.168.0.1", "Type": "TODO", "State": "blackhole"}]
    )

    routes = ec2.search_transit_gateway_routes(
        TransitGatewayRouteTableId=table_id,
        Filters=[{"Name": "state", "Values": ["unknown"]}],
    )["Routes"]

    routes.should.equal([])


@mock_ec2
def test_delete_transit_gateway_route():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    table_id = ec2.create_transit_gateway_route_table(TransitGatewayId=gateway_id)[
        "TransitGatewayRouteTable"
    ]["TransitGatewayRouteTableId"]

    ec2.create_transit_gateway_route(
        DestinationCidrBlock="192.168.0.0", TransitGatewayRouteTableId=table_id
    )
    ec2.create_transit_gateway_route(
        DestinationCidrBlock="192.168.0.1", TransitGatewayRouteTableId=table_id
    )

    response = ec2.delete_transit_gateway_route(
        DestinationCidrBlock="192.168.0.0", TransitGatewayRouteTableId=table_id
    )

    response["Route"].should.equal(
        {"DestinationCidrBlock": "192.168.0.0", "Type": "TODO", "State": "deleted"}
    )

    routes = ec2.search_transit_gateway_routes(
        TransitGatewayRouteTableId=table_id,
        Filters=[{"Name": "state", "Values": ["active"]}],
    )["Routes"]

    routes.should.equal(
        [{"DestinationCidrBlock": "192.168.0.1", "Type": "TODO", "State": "active"}]
    )


@mock_ec2
def test_create_transit_gateway_vpc_attachment():
    ec2 = boto3.client("ec2", region_name="us-west-1")
    gateway_id = ec2.create_transit_gateway(Description="g")["TransitGateway"][
        "TransitGatewayId"
    ]
    response = ec2.create_transit_gateway_vpc_attachment(
        TransitGatewayId=gateway_id, VpcId="vpc-id", SubnetIds=["sub1"]
    )
    response.should.have.key("TransitGatewayVpcAttachment")
    attachment = response["TransitGatewayVpcAttachment"]
    attachment.should.have.key("TransitGatewayAttachmentId").match(
        "tgw-attach-[0-9a-z]+"
    )
    attachment.should.have.key("TransitGatewayId").equal(gateway_id)
    attachment.should.have.key("VpcId").equal("vpc-id")
    attachment.should.have.key("VpcOwnerId").equal(ACCOUNT_ID)
    attachment.should.have.key("SubnetIds").equal(["sub1"])
    attachment.should.have.key("State").equal("available")
    attachment.should.have.key("Tags").equal([])
