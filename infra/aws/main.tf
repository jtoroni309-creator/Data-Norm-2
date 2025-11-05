# Aura Audit AI - AWS Infrastructure
terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "atlas" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "atlas-vpc" }
}

# RDS PostgreSQL with encryption
resource "aws_db_instance" "atlas" {
  identifier        = "atlas-db"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  storage_encrypted = true
  multi_az          = true

  tags = { Name = "atlas-db" }
}

# S3 with Object Lock (WORM)
resource "aws_s3_bucket" "worm" {
  bucket              = "atlas-worm"
  object_lock_enabled = true

  tags = { Name = "atlas-worm" }
}

resource "aws_s3_bucket_object_lock_configuration" "worm" {
  bucket = aws_s3_bucket.worm.id

  rule {
    default_retention {
      mode = "COMPLIANCE"
      days = 2555  # 7 years
    }
  }
}

# KMS encryption key
resource "aws_kms_key" "atlas" {
  description             = "Atlas encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

output "rds_endpoint" {
  value = aws_db_instance.atlas.endpoint
}

output "worm_bucket" {
  value = aws_s3_bucket.worm.id
}
