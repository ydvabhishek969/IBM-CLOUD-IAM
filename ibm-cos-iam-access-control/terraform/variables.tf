variable "ibmcloud_api_key" {
  type      = string
  sensitive = true
}
variable "region" {
  type    = string
  default = "us-south"
}
variable "prefix" {
  type    = string
  default = "cosdemo"
}
variable "bucket_name" {
  type        = string
  description = "Globally unique bucket name"
}
variable "resource_group_id" {
  type        = string
  description = "Resource group ID (ibmcloud resource groups)"
}
variable "reader_emails" {
  type    = list(string)
  default = []
}
variable "writer_emails" {
  type    = list(string)
  default = []
}
