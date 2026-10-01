terraform {
  required_providers {
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = ">= 1.60.0"
    }
  }
}

provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key
  region           = var.region
}

# ---- COS instance + bucket ----
resource "ibm_resource_instance" "cos" {
  name              = "${var.prefix}-cos"
  service           = "cloud-object-storage"
  plan              = "standard"
  location          = "global"
  resource_group_id = var.resource_group_id
}

resource "ibm_cos_bucket" "bucket" {
  bucket_name          = var.bucket_name
  resource_instance_id = ibm_resource_instance.cos.id
  region_location      = var.region
  storage_class        = "standard"
}

# ---- Access groups ----
resource "ibm_iam_access_group" "readers" {
  name        = "${var.prefix}-cos-readers"
  description = "Read-only access to ${var.bucket_name}"
}

resource "ibm_iam_access_group" "writers" {
  name        = "${var.prefix}-cos-writers"
  description = "Read/write access to ${var.bucket_name}"
}

# ---- Bucket-scoped policies (least privilege) ----
resource "ibm_iam_access_group_policy" "readers_policy" {
  access_group_id = ibm_iam_access_group.readers.id
  roles           = ["Reader"]

  resources {
    service              = "cloud-object-storage"
    resource_instance_id = element(split(":", ibm_resource_instance.cos.id), 7)
    resource_type        = "bucket"
    resource             = ibm_cos_bucket.bucket.bucket_name
  }
}

resource "ibm_iam_access_group_policy" "writers_policy" {
  access_group_id = ibm_iam_access_group.writers.id
  roles           = ["Writer"]

  resources {
    service              = "cloud-object-storage"
    resource_instance_id = element(split(":", ibm_resource_instance.cos.id), 7)
    resource_type        = "bucket"
    resource             = ibm_cos_bucket.bucket.bucket_name
  }
}

# ---- Optional: add existing users ----
resource "ibm_iam_access_group_members" "readers_members" {
  count           = length(var.reader_emails) > 0 ? 1 : 0
  access_group_id = ibm_iam_access_group.readers.id
  ibm_ids         = var.reader_emails
}

resource "ibm_iam_access_group_members" "writers_members" {
  count           = length(var.writer_emails) > 0 ? 1 : 0
  access_group_id = ibm_iam_access_group.writers.id
  ibm_ids         = var.writer_emails
}
