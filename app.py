"""
Sfera AWS Infrastructure Diagram
Generated from: SCRIPTS/AWS-migration/tofu/

Install deps:  pip install diagrams
Run:           python sfera_aws_diagram.py
Output:        sfera_aws_infra.png
"""

import os
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS, EC2, ECR
from diagrams.aws.database import RDS
from diagrams.aws.network import InternetGateway, NATGateway
from diagrams.aws.storage import EBS
from diagrams.aws.security import IAM


graph_attr = {
    "fontsize": "13",
    "bgcolor": "white",
    "pad": "0.75",
    "splines": "spline",
    "nodesep": "0.8",
    "ranksep": "1.2",
}

with Diagram(
    "Sfera AWS Infrastructure\nlabelgrup-cluster-k8s  |  eu-central-1",
    show=False,
    filename="sfera_aws_infra",
    direction="TB",
    graph_attr=graph_attr,
):
    # ── Outside VPC ────────────────────────────────────────────────────────────
    ecr = ECR("ECR: labelgrup-k8s\n~154 GB\nAES256 · scan-on-push")
    iam = IAM("IAM Roles\n· eks-cluster-role\n· eks-nodes-role\n· ebs-csi-role\n+ OIDC provider")

    with Cluster("VPC: labelgrup-cluster-k8s-vpc  10.46.0.0/16"):

        igw = InternetGateway("Internet Gateway")

        # ── Public subnets ─────────────────────────────────────────────────────
        with Cluster("Public Subnets  10.46.4–6.0/24  (AZ a / b / c)"):
            bastion = EC2("bastion-sfera\nm5.xlarge · Ubuntu 22.04\nEIP · SG: port 22 office-only")
            nat     = NATGateway("NAT Gateway\n+ EIP")
            bvol    = EBS("backups\n500 GB gp3\n/dev/sdf")

        # ── Private subnets ────────────────────────────────────────────────────
        with Cluster("Private Subnets  10.46.1–3.0/24  (AZ a / b / c)"):

            with Cluster("EKS Cluster: labelgrup-cluster-k8s  (K8s v1.31)"):
                eks = EKS(
                    "Control Plane\nAddons: vpc-cni · coredns\n"
                    "kube-proxy · aws-ebs-csi-driver\n"
                    "services CIDR: 10.3.0.0/16"
                )

                with Cluster("nodepool-1  (3 × m5.xlarge · 100 GB · monthly)"):
                    n1 = EC2("node-85a324\n10.46.1.199")
                    n2 = EC2("node-a490db\n10.46.1.21")
                    n3 = EC2("node-afdeab\n10.46.1.30")

                with Cluster("horizon  (1 × m5.xlarge · 100 GB · on-demand)"):
                    hz = EC2("horizon-node\n10.46.0.103")

            rds = RDS(
                "mysql-sfera-pre\n"
                "MySQL 8.0 · db.m5.large\n"
                "400 GB gp3 · encrypted\n"
                "SG: port 3306 (nodes + office)\n"
                "backup 7 days · deletion-protected"
            )

    # ── Edges ──────────────────────────────────────────────────────────────────
    igw >> [bastion, nat]

    bastion - Edge(style="dashed", label="attached") - bvol

    nat >> Edge(label="outbound") >> [n1, n2, n3, hz]

    eks >> [n1, n2, n3, hz]

    [n1, n2, n3, hz] >> Edge(label="3306") >> rds

    [n1, n2, n3, hz] >> Edge(label="pull images") >> ecr

    hz >> Edge(label="pull images") >> ecr

    iam >> Edge(label="IRSA / roles") >> eks

    bastion >> Edge(style="dashed", label="SSH tunnel\n(kubectl access)") >> eks
