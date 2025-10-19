j_data = {
    "variable": [],
    "locals": [{"__block__": True}],
    "module": [
        {
            "test1": {
                "__block__": True,
                "source": "./",
                "inputs": {},
                "outputs": {"i_kms": {"data": "value1"}},
            }
        },
        {
            "test2": {
                "__block__": True,
                "source": "./",
                "inputs": {},
                "outputs": {"i_kms": {"data": "value2"}},
            }
        },
        {
            "test3": {
                "__block__": True,
                "source": "./",
                "inputs": {},
                "outputs": {"i_kms": {"data": "value3"}},
            }
        },
    ],
    "data": [],
    "resource": [],
    "output": [],
}

render = {
    "tfcode": j_data,
    "parents": {"test": {"id": "123-test"}, "base": {"id": "123-base"}},
    "providers": {"base": {"id": "000-base"}},
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
