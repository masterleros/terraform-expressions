locals {
  parents = {
    "parent-test" = {
      interfaces = {
        kms = {
          test1 = { "value" = 1 }
          test2 = { "value" = 2 }
        }
      }
    }
    "parent-base" = {
      interfaces = {
        kms = {
          test1 = { "value" = 3 }
          test2 = { "value" = 4 }
        }
        base = {
          base1 = { "value" = 5 }
        }
      }
    }
  }

  # i_data = {
  #   for i_type in distinct(flatten([for value in values(local.parents) : keys(value.interfaces)])) : i_type =>
  #   {
  #     for i in flatten([for p_name, p_values in local.parents : [
  #       for i_id, i_values in lookup(p_values.interfaces, i_type, {}) : { id = "${p_name}-${i_id}", values = i_values }
  #     ]]) : i.id => i.values
  #   }
  # }
}

# output "i_data" {
#   value = local.i_data
# }

# output "i_map" {
#   value = merge([
#     { for ik, iv in local.i_data.kms : ik => iv if startswith(ik, "parent-base") },
#     { for ik, iv in local.i_data.kms : ik => iv if startswith(ik, "parent-test.test2") },
#   ]...)
# }


# output "test" {
#   value = flatten([[for ik, iv in local.i_data.kms : iv if startswith(ik, "parent-base")], [for ik, iv in local.i_data.kms : iv if startswith(ik, "parent-test")]])
# }

# output "i_list" {
#   value = flatten([
#     [for ik, iv in local.i_data.kms : iv if startswith(ik, "parent-base")],
#     [for ik, iv in local.i_data.kms : iv if startswith(ik, "parent-test.test2")],
#   ])
# }

# output "i_obj" {
#   value = merge([{ for ik, iv in local.i_data.base : ik => iv if startswith(ik, "000000-base.base1") }]...)
# }

# output "collector" {
#   value = [for iv in local.i_data.kms : iv]
# }
