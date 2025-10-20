import json
from data import render, j_data
import interfaces
import tfcode


j_data = {
    # "data": [
    #     {
    #         "tfe_output": {
    #             "sources": {
    #                 "__block__": True,
    #                 "provider": "aws/custom",
    #                 "organization": "my-org",
    #                 "workspace": "my-workspace",
    #             },
    #         },
    #     }
    # ],
    "locals": [
        {
            "__block__": True,
            "i_data": "${{ for i_type in distinct(flatten([for value in values(local.parents) : keys(value.interfaces)])) : i_type => { for i in flatten([for p_name, p_values in local.parents : ["
            'for i_id, i_values in lookup(p_values.interfaces, i_type, {}) : { id = "${p_name}-${i_id}", values = i_values }'
            "]]) : i.id => i.values } } }",
        }
    ],
    "output": [
        # {"i_data": {"__block__": True, "value": "${local.i_data}"}},
        {
            "i_obj_kms_module": {
                "__block__": True,
                "value": str(
                    interfaces.assign("i_obj_kms", "${module.test1.interface(kms)}")
                ),
            }
        },
        {
            "i_obj_kms_parent": {
                "__block__": True,
                "value": str(
                    interfaces.assign(
                        "i_obj_kms", "${parent(base).interface(kms,test1)}"
                    )
                ),
            }
        },
        {
            "i_list_kms": {
                "__block__": True,
                "value": str(
                    interfaces.assign(
                        "i_list_kms",
                        "${parent(base).interfaces(kms)}",
                    )
                ),
            }
        },
        {
            "i_list_kms_filtered": {
                "__block__": True,
                "value": str(
                    interfaces.assign(
                        "i_list_kms",
                        [
                            "${parent(base).interfaces(kms,test1)}",
                            "${parent(test).interfaces(kms,test1)}",
                        ],
                    )
                ),
            }
        },
    ],
}

# Remove empty resources and write file
# print(json.dumps(j_data, indent=2))
tfcode.write("test.tf", {i: j_data[i] for i in j_data if j_data[i] != []})
