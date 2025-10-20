import tfcode
import json
from data import j_data

j_data["locals"][0].update(
    {
        "i_data": "${{ for i_type in distinct(flatten([for value in values(local.parents) : keys(value.interfaces)])) : i_type => { for i in flatten([for p_name, p_values in local.parents : ["
        'for i_id, i_values in lookup(p_values.interfaces, i_type, {}) : { id = "${p_name}-${i_id}", values = i_values }'
        "]]) : i.id => i.values } } }"
    }
)

j_data["output"].append({"i_data": {"__block__": True, "value": "${local.i_data}"}})

j_data["output"].append(
    {
        "test": {
            "__block__": True,
            "value": "${flatten(["
            '[ for ik, iv in local.i_data.kms : iv if startswith(ik, "parent-base") ],'
            '[ for ik, iv in local.i_data.kms : iv if startswith(ik, "parent-test") ]'
            "])}",
        }
    },
)


# Remove empty resources and write file
# tfcode.write("test.tf", {i: j_data[i] for i in j_data if j_data[i] != []})

# Read file
j_data = tfcode.read("test.tf")
print(json.dumps(j_data, indent=2))
