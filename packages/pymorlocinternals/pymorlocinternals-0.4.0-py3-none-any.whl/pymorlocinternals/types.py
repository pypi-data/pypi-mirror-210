def mlc_list(arg):
    """
  Helper function for building list types

  The "list" here is a homogenous vector, like the Haskell or lisp list, not
  the named, heterogenous lists of python. So `mlc_list(mlc_integer)` would be
  the python3 version of the Haskell type `[Int]`.

  @param args The type parameter for a list
  """
    return ("list", arg)


def mlc_tuple(*args):
    """
  Helper function for building tuple types

  @param *args The type parameter for the tuple
  """
    return ("tuple", [*args])


def mlc_record(**kwargs):
    """
  Helper function for building record types

  @param **kwargs The keyword arguments for the record
  """
    return ("record", dict(**kwargs))


def mlc_object(f, **kwargs):
    """
  Helper function for building object types

  @param **kwargs The keyword arguments for the record
  """
    return (f, dict(**kwargs))


mlc_int = ("int", None)

mlc_float = ("float", None)

mlc_str = ("str", None)

mlc_bool = ("bool", None)

mlc_null = ("null", None)
