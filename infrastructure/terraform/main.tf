terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = var.aws_region
}

# ---------- S3 Bucket ----------
resource "aws_s3_bucket" "sports_bucket" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.sports_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ---------- IAM Role for Lambda ----------
resource "aws_iam_role" "lambda_role" {
  name = "lambda_sports_ingest_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy_attachment" "lambda_s3_policy_attach" {
  name       = "lambda_s3_policy_attach"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_policy_attachment" "lambda_logging_policy_attach" {
  name       = "lambda_logging_policy_attach"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ---------- Lambda Function ----------
resource "aws_lambda_function" "football_ingestion" {
  function_name = "football_ingestion_lambda"

  runtime = "python3.12"
  handler = "extract_api.handler"
  role    = aws_iam_role.lambda_role.arn
  timeout = 30

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  environment {
    variables = {
      API_TOKEN   = var.api_token
      BUCKET_NAME = var.bucket_name
    }
  }
}

# ---------- CloudWatch Event Rule (daily trigger) ----------
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name        = "lambda_daily_trigger"
  description = "Triggers Lambda daily at midnight UTC"
  schedule_expression = "cron(0 0 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "football_ingestion"
  arn       = aws_lambda_function.football_ingestion.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.football_ingestion.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}
