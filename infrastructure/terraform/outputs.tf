output "lambda_name" {
  value = aws_lambda_function.football_ingestion.function_name
}

output "bucket" {
  value = aws_s3_bucket.sports_bucket.bucket
}
