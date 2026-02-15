resource "aws_api_gateway_rest_api" "MyApi" {
  name = "MyApi"
}

resource "aws_lambda_function" "AuthLambda" {
  function_name = "AuthLambda"
  handler = "auth.handler"
  runtime = "nodejs14.x"
}

resource "aws_lambda_function" "UserService" {
  function_name = "UserService"
  handler = "user.handler"
  runtime = "nodejs14.x"
  
  environment {
    variables = {
       AUTH_URL = aws_lambda_function.AuthLambda.arn
    }
  }
}

resource "aws_lambda_function" "ProductService" {
  function_name = "ProductService"
  handler = "product.handler"
  runtime = "nodejs14.x"
  
  environment {
    variables = {
       AUTH_URL = aws_lambda_function.AuthLambda.arn
    }
  }
}

resource "aws_lambda_function" "OrderService" {
  function_name = "OrderService"
  handler = "order.handler"
  runtime = "nodejs14.x"
  
  environment {
    variables = {
       AUTH_URL = aws_lambda_function.AuthLambda.arn
    }
  }
}

resource "aws_lambda_function" "NotificationService" {
  function_name = "NotificationService"
  handler = "notify.handler"
  runtime = "nodejs14.x"
  
  environment {
    variables = {
       AUTH_URL = aws_lambda_function.AuthLambda.arn
    }
  }
}
