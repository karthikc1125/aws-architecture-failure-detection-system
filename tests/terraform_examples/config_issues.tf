resource "aws_lambda_function" "UnsafeLambda" {
  function_name = "UnsafeLambda"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  timeout       = 10  # Too low!
  memory_size   = 256 # Too low!
}

resource "aws_db_instance" "UnsafeDB" {
  allocated_storage    = 20
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  name                = "mydb"
  username            = "admin"
  password            = "password"
  # Missing: storage_encrypted = true
  # Missing: multi_az = true
  backup_retention_period = 1  # Too low!
}

resource "aws_s3_bucket" "UnsafeBucket" {
  bucket = "my-unsafe-bucket"
  # Missing: versioning
  # Missing: server_side_encryption_configuration
}

resource "aws_dynamodb_table" "UnsafeTable" {
  name           = "UnsafeTable"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  # Missing: point_in_time_recovery
}
