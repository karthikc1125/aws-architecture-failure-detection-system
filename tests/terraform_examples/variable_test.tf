variable "queue_url" {
  default = "aws_sqs_queue.OrdersQueue.id"
}

resource "aws_lambda_function" "OrdersFunction" {
  function_name = "OrdersFunction"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  
  environment {
      variables = {
          # Use a variable instead of direct reference
          QUEUE_URL = var.queue_url
      }
  }
}

resource "aws_sqs_queue" "OrdersQueue" {
  name = "orders-queue"
}

# Add a loop via processor
resource "aws_lambda_function" "ProcessorFunction" {
  function_name = "ProcessorFunction"
  
  environment {
      variables = {
          # Trigger logic simulated via env vars here for simplicity of graph detection
          TARGET = aws_lambda_function.OrdersFunction.arn
      }
  }
}
