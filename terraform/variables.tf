variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "cluster_name" {
  type    = string
  default = "expense-tracker-eks"
}

variable "node_instance_type" {
  type    = string
  default = "t3.small"
}

variable "node_count" {
  type    = number
  default = 2
}
