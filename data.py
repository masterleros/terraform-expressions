j_data = {
    "variable": [],
    "locals": [{"__block__": True}],
    "module": [
        {
            "test1": {
                "__block__": True,
                "source": "./",
                "inputs": {},
                "outputs": {"i_obj_kms": {"data": "value1"}},
            }
        },
        {
            "test2": {
                "__block__": True,
                "source": "./",
                "inputs": {},
                "outputs": {"i_obj_kms": {"data": "value2"}},
            }
        },
        {
            "test3": {
                "__block__": True,
                "source": "./",
                "inputs": {},
                "outputs": {"i_obj_kms": {"data": "value3"}},
            }
        },
    ],
    "data": [],
    "resource": [],
    "output": [],
}

render = {
    "tfcode": j_data,
    "module": {
        "test1": {
            "__block__": True,
            "source": "./",
            "inputs": {},
            "outputs": {"i_obj_kms": {"data": "value1"}},
        },
        "test2": {
            "__block__": True,
            "source": "./",
            "inputs": {},
            "outputs": {"i_obj_kms": {"data": "value2"}},
        },
    },
    "parents": {
        "test": {"id": "123-test", "outputs": {"interfaces": {"kms": {"value": 1}}}},
        "base": {"id": "123-base", "outputs": {"interfaces": {"kms": {"value": 2}}}},
    },
    "providers": {
        "base": {"id": "000-base", "outputs": {"interfaces": {"kms": {"value": 4}}}}
    },
}

expressions = [
    "${parent(base).interface(kms,test1)}",
    "${provider(base).interfaces(kms,mykms)}",
    "${provider(base).interfaces(kms)}",
    "${module.test2.an_output}",
    "${module.test1.interface(kms)}",
    "${var.test}",
    "${collector(kms)}",
]
