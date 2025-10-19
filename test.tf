locals {
  i_data = { for i_type in distinct(flatten([ for value in values(local.parents) : keys(value.interfaces)])) : i_type => { for i in flatten([ for p_name,p_values in local.parents : [ for i_id,i_values in lookup(p_values.interfaces, i_type,{}) : {id = "${p_name}-${i_id}",values = i_values}]]) : i.id => i.values}}
}

output "i_data" {
  value = local.i_data
}
