# Create the ECR Repository to hold the Docker Images
resource "aws_ecr_repository" "lambda_repo" {
  name                 = "budget-manager-lambdas"
  image_tag_mutability = "MUTABLE" # Allows to overwrite the 'latest' tag when we update code
  force_delete         = true      # Allows Terraform to destroy the repo even if it contains images

  image_scanning_configuration {
    scan_on_push = true # AWS will automatically scan the Python packages for security vulnerabilities!
  }
}

# Output the URL so I can use it to push the Docker image
output "ecr_repository_url" {
  value = aws_ecr_repository.lambda_repo.repository_url
}