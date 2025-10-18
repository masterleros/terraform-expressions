from expressions import Expression

render = {
    "tfcode": {
        "variable": {},
        "local": {},
        "module": {},
        "data": {},
        "resource": {},
        "output": {},
    },
    "parents": ["test"],
    "providers": [],
}

exp = Expression("${parent(base).interfaces(kms,mykms)}")
exp.process(render)
print(exp.render())
