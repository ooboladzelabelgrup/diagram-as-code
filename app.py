from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS, EC2, ECR
from diagrams.aws.database import RDS
from diagrams.aws.network import InternetGateway, NATGateway
from diagrams.aws.security import IAM
from diagrams.aws.management import SystemsManager
from diagrams.generic.network import Router

with Diagram("AWS MVP - sfera-mvp | eu-central-1", show=False, filename="aws_mvp_actual", direction="TB"):

    internet = Router("Internet")

    with Cluster("AWS Managed Services"):
        eks_ctrl = EKS("EKS Control Plane\nsfera-mvp | K8s 1.31")
        ecr = ECR("ECR\nsfera-mvp")
        ssm = SystemsManager("SSM\nSession Manager")

    with Cluster("VPC sfera-mvp | 10.20.0.0/16"):

        igw = InternetGateway("Internet Gateway")

        with Cluster("eu-central-1a"):
            with Cluster("Public 10.20.10.0/24"):
                nat = NATGateway("NAT Gateway")

            with Cluster("Private 10.20.1.0/24"):
                node = EC2("ip-10-20-1-104\nm5.xlarge | 4vCPU/16GB\nv1.31.14-eks")
                rds = RDS("sfera-mvp-mysql-pre\nMySQL 8.0 | db.t3.medium\n100 GB gp3 | available")

        with Cluster("eu-central-1b (standby)"):
            with Cluster("Private 10.20.2.0/24"):
                rds_subnet = RDS("RDS subnet group\n(no active instance)")

    with Cluster("IAM"):
        iam_cluster = IAM("eks-cluster-role")
        iam_node = IAM("eks-node-role")
        iam_ebs = IAM("sfera-mvp-ebs-csi-role\n(IRSA)")

    internet >> igw >> nat >> node
    eks_ctrl >> node
    node >> Edge(label=":3306") >> rds
    node >> Edge(label="via NAT") >> ecr
    ssm >> node
    iam_cluster >> eks_ctrl
    iam_node >> node
    iam_ebs >> Edge(label="IRSA") >> node
