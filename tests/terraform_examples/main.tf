resource "aws_lambda_function" "OrdersFunction" {
  function_name = "OrdersFunction"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  
  environment {
    variables = {
      QUEUE_URL = aws_sqs_queue.OrdersQueue.id
      TABLE_NAME = aws_dynamodb_table.InventoryTable.name
      DB_ENDPOINT = aws_db_instance.MainDB.address
    }
  }
}

resource "aws_sqs_queue" "OrdersQueue" {
  name = "orders-queue"
}

resource "aws_lambda_event_source_mapping" "OrdersTrigger" {
  event_source_arn = aws_sqs_queue.OrdersQueue.arn
  function_name    = aws_lambda_function.ProcessorFunction.arn
}

resource "aws_lambda_function" "ProcessorFunction" {
  function_name = "ProcessorFunction"
  handler       = "process.handler"
  runtime       = "python3.8"
  
  environment {
    variables = {
        # Circular dependency back to OrdersFunction via direct invocation (implicit)
        CALLBACK_FUNCTION = aws_lambda_function.OrdersFunction.arn
        DB_ENDPOINT = aws_db_instance.MainDB.address
    }
  }
}

resource "aws_dynamodb_table" "InventoryTable" {
  name           = "Inventory"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "ItemId"

  attribute {
    name = "ItemId"
    type = "S"
  }
}

resource "aws_db_instance" "MainDB" {
  allocated_storage    = 10
  engine               = "mysql"
  instance_class       = "db.t3.micro"
  name                 = "mydb"
  username             = "admin"
  password             = "password"
}

# Processor also writes to MainDB
resource "aws_iam_policy" "ProcessorPolicy" {
  name        = "ProcessorPolicy"
  description = "Access to RDS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "rds:*"
        ]
        Effect   = "Allow"
        Resource = aws_db_instance.MainDB.arn
      },
    ]
  })
}
