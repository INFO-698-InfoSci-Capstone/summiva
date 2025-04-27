output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "db_endpoint" {
  value = module.db.db_instance_endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.summiva.cache_nodes[0].address
}
