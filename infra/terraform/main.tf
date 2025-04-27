provider "aws" {
  region = var.aws_region
}

# =========================
# VPC & Networking
# =========================
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"

  name = "summiva-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    Project     = "Summiva"
    Environment = var.environment
  }
}

# =========================
# EKS Cluster
# =========================
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.4"

  cluster_name    = "summiva-eks"
  cluster_version = "1.28"
  subnet_ids      = module.vpc.private_subnets
  vpc_id          = module.vpc.vpc_id

  enable_cluster_creator_admin_permissions = true

  eks_managed_node_groups = {
    default = {
      desired_size   = 2
      max_size       = 3
      min_size       = 1
      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"
    }
  }

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }

  tags = {
    Project     = "Summiva"
    Environment = var.environment
  }
}

# =========================
# RDS PostgreSQL
# =========================
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.1.0"

  identifier = "summiva-db"
  engine     = "postgres"
  engine_version = "16"

  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  max_allocated_storage   = 50
  db_name                 = "summiva_db"
  username                = var.db_user
  password                = var.db_password
  subnet_ids              = module.vpc.private_subnets
  vpc_security_group_ids  = [module.vpc.default_security_group_id]
  skip_final_snapshot     = true

  tags = {
    Name = "Summiva-Postgres"
  }
}

# =========================
# Redis (ElastiCache)
# =========================
resource "aws_elasticache_subnet_group" "summiva" {
  name       = "summiva-cache-subnet-group"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_cluster" "summiva" {
  cluster_id           = "summiva-redis"
  engine               = "redis"
  node_type            = "cache.t2.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"

  subnet_group_name  = aws_elasticache_subnet_group.summiva.name
  security_group_ids = [module.vpc.default_security_group_id]
}
