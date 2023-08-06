import json

"""
("tuple", [("float", None), ("record", OrderedDict(a=("float", None)))])
"""


def serialize_list(x, schema):
    f = dispatch[schema[0]]
    return "[{}]".format(",".join([f(y, schema[1]) for y in x]))


def serialize_tuple(x, schema):
    elements = []
    for (t, e) in zip(schema, x):
        f = dispatch[t[0]]
        elements.append(f(e, t[1]))
    return "[{}]".format(",".join(elements))


def serialize_record(x, schema):
    entries = []
    for (k, t) in schema.items():
        f = dispatch[t[0]]
        entries.append('"{}":{}'.format(k, f(x[k], t[1])))
    return "{{{}}}".format(",".join(entries))


def serialize_float(x, schema):
    return str(x)


def serialize_int(x, schema):
    return str(x)


def serialize_str(x, schema):
    return json.dumps(x)


def serialize_bool(x, schema):
    return json.dumps(x)

def serialize_none(x, schema):
    return json.dumps(None)

dispatch = { 
    "list" : serialize_list,
    "tuple" : serialize_tuple,
    "record" : serialize_record,
    "dict" : serialize_record,
    "float" : serialize_float,
    "int" : serialize_int,
    "str" : serialize_str,
    "bool" : serialize_bool,
    "None" : serialize_none,
  }


def mlc_serialize(x, schema):
    if type(schema[0]) == str:
        return dispatch[schema[0]](x, schema[1])
    else:
        # Is the label is not a string, then it is a constructor,
        # so the data should an object
        return serialize_record(x.__dict__, schema[1])


def deserialize_list(xs, schema):
    deserialize = dispatch_deserialize[schema[0]]
    return [deserialize(x, schema[1]) for x in xs]


def deserialize_tuple(xs, schema):
    return tuple([dispatch_deserialize[s[0]](x, s[1])  for (x,s) in zip(xs, schema)])


def deserialize_record(d0, schema):
    d = dict()
    for (k, v) in schema.items():
        deserializer = dispatch_deserialize[v[0]]
        d[k] = deserializer(d0[k], v[1])
    return d


dispatch_deserialize = {
    "list"   : deserialize_list,
    "tuple"  : deserialize_tuple,
    "record" : deserialize_record,
    "dict"   : deserialize_record,
    "float"  : lambda x, _: x,
    "int"    : lambda x, _: x,
    "str"    : lambda x, _: x,
    "bool"   : lambda x, _: x,
    "None"   : None
}


def mlc_deserialize(json_str, schema):
    x = json.loads(json_str)
    if type(schema[0]) == str:
        return dispatch_deserialize[schema[0]](x, schema[1])
    else:
        return schema[0](**deserialize_record(x, schema[1]))
