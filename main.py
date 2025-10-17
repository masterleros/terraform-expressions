import json
import re
from expressions import Expression

tfcode = {"variable":{},"local":{},"module":{},"data":{},"resource":{},"output":{},"parent":{},"provider":{}}

# print(Expression.process("variable = parent(base).interfaces(kms,mykms)", render=render_additions))
# print(Expression.process("variable = provider(eks).interfaces(kms,mykms)", render=render_additions))
# print(Expression.process("variable = provider(eks).outputs.test.id", render=render_additions))
# print(Expression.process("variable = var.interfaces(kms,mykms)", render=render_additions))
# print(Expression.process("variable = var.test", render=render_additions))

# for e in extracted:
#     print(ExpressionObject(e).context)

# exp = Expression("variable = var.test")
# exp.process(render=render_additions)
# print(exp.render())

Expression("variable = var.test").process(tfcode)
Expression("variable = module.leo").process(tfcode)
Expression("variable = parent(base).interfaces(kms,mykms)").process(tfcode)

print(json.dumps(tfcode, indent=2))