locals {
  environment = "production"
  db_name = "${local.environment}-database"
}

module "vpc" {
  source = "./modules/vpc"
}

resource "aws_lambda_function" "api" {
  function_name = "api-function"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  timeout       = lookup(var.timeouts, "api", 30)
}

resource "aws_db_instance" "main" {
  allocated_storage = 20
  engine           = "mysql"
  instance_class   = "db.t3.micro"
  name             = local.db_name
  multi_az         = true
  storage_encrypted = true
}

resource "aws_lambda_function" "processor" {
  function_name = "processor"
  environment {
    variables = {
      DB_ENDPOINT = aws_db_instance.main.address
    }
  }
}
