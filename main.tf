locals {
  parents = {
    "123456-test" = {
      interfaces = {
        kms = {
          test1 = { "value" = 1 }
          test2 = { "value" = 2 }
        }
      }
    }
    "000000-base" = {
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

  interfaces = {
    for i_type in distinct(flatten([for value in values(local.parents) : keys(value.interfaces)])) : i_type => merge([
      for p_name, p_values in local.parents : {
        for i_id, i_values in lookup(p_values.interfaces, i_type, {}) : "${p_name}.${i_id}" => i_values
      }
    ]...)
  }
}

output "interfaces" {
  value = local.interfaces
}

output "i_list" {
  value = merge([
    { for ik, iv in local.interfaces.kms : ik => iv if startswith(ik, "000000-base") },
    { for ik, iv in local.interfaces.kms : ik => iv if startswith(ik, "123456-test") },
  ]...)
}

output "i_obj" {
  value = merge([{ for ik, iv in local.interfaces.base : ik => iv if startswith(ik, "000000-base.base1") }]...)
}
