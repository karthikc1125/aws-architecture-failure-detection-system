resource "aws_kinesis_stream" "InputStream" {
  name        = "input_stream"
  shard_count = 2
}

resource "aws_lambda_function" "ProcessorA" {
  function_name = "ProcessorA"
  handler = "proc.a"
}

resource "aws_lambda_event_source_mapping" "TriggerA" {
  event_source_arn = aws_kinesis_stream.InputStream.arn
  function_name    = aws_lambda_function.ProcessorA.arn
}

resource "aws_kinesis_stream" "IntermediateStream" {
  name        = "intermediate_stream"
}

# ProcessorA writes to IntermediateStream
resource "aws_iam_policy" "RoleA" {
   name = "RoleA"
   policy = jsonencode({
      Statement = [{
          Action = ["kinesis:PutRecord"]
          Resource = aws_kinesis_stream.IntermediateStream.arn
      }]
   })
}

resource "aws_lambda_function" "ProcessorB" {
  function_name = "ProcessorB"
  handler = "proc.b"
}

resource "aws_lambda_event_source_mapping" "TriggerB" {
  event_source_arn = aws_kinesis_stream.IntermediateStream.arn
  function_name    = aws_lambda_function.ProcessorB.arn
}

# Recursion! ProcessorB writes back to InputStream (Bad event loop)
resource "aws_iam_policy" "RoleB" {
   name = "RoleB"
   policy = jsonencode({
      Statement = [{
          Action = ["kinesis:PutRecord"]
          Resource = aws_kinesis_stream.InputStream.arn
      }]
   })
}
