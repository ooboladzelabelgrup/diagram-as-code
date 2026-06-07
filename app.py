from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import NATGateway, InternetGateway
from diagrams.aws.compute import EC2
from diagrams.aws.storage import S3

with Diagram("AWS NAT Gateway Architecture", show=False, direction="LR"):
    igw = InternetGateway("Internet Gateway")

    with Cluster("VPC"):
        with Cluster("Public Subnet"):
            nat = NATGateway("NAT Gateway")

        with Cluster("Private Subnet"):
            ec2 = EC2("EC2 Instance")

    s3 = S3("S3 Bucket")

    igw >> nat
    ec2 >> nat >> igw >> s3
