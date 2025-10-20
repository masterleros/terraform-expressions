locals {
  i_data = { for i_type in distinct(flatten([ for value in values(local.parents) : keys(value.interfaces)])) : i_type => { for i in flatten([ for p_name,p_values in local.parents : [ for i_id,i_values in lookup(p_values.interfaces, i_type,{}) : {id = "${p_name}-${i_id}",values = i_values}]]) : i.id => i.values}}
}

output "i_obj_kms_module" {
  value = module.test1.i_obj_kms
}

output "i_obj_kms_parent" {
  value = local.i_data.kms["parent-base-test1"]
}

output "i_list_kms" {
  value = [ for ik,iv in local.i_data.kms : iv if startswith(ik, "parent-base")]
}

output "i_list_kms_filtered" {
  value = flatten([[local.i_data.kms["parent-base-test1"]],[local.i_data.kms["parent-test-test1"]]])
}
