output "bucket_name"        { value = ibm_cos_bucket.bucket.bucket_name }
output "readers_group_id"   { value = ibm_iam_access_group.readers.id }
output "writers_group_id"   { value = ibm_iam_access_group.writers.id }
