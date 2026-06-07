from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import NATGateway, InternetGateway
from diagrams.aws.compute import EC2
from diagrams.aws.storage import S3
from diagrams.aws.network import ELB
from diagrams.aws.database import RDS


# with Diagram("AWS NAT Gateway Architecture", show=False, direction="LR"):
#     igw = InternetGateway("Internet Gateway")

#     with Cluster("VPC"):
#         with Cluster("Public Subnet"):
#             nat = NATGateway("NAT Gateway")

#         with Cluster("Private Subnet"):
#             ec2 = EC2("EC2 Instance")

#     s3 = S3("S3 Bucket")

#     igw >> nat
#     ec2 >> nat >> igw >> s3


with Diagram("Grouped Workers", show=False, direction="TB"):
    ELB("lb") >> [EC2("worker1"),
                  EC2("worker2"),
                  EC2("worker3"),
                  EC2("worker4"),
                  EC2("worker5")] >> RDS("events")


