variable "AWS_ACCESS_KEY" {
  type = string
}
variable "AWS_SECRET_KEY" {
  type = string
}
variable "AWS_REGION" {
    type = string
    default = "eu-west-2"
}


variable "DB_USERNAME" {
    type = string
}
variable "DB_PASSWORD"{
    type = string
}
variable "DB_NAME" {
    type = string
}
variable "DB_IP"{
    type = string
}
variable "DB_PORT"{
    type = string
}