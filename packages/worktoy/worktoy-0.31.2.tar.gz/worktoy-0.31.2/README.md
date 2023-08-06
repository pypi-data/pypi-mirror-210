# WorkToy v0.31.2

Collection of General Utilities

```
pip install worktoy
```

## Parsing Arguments

In the present version, parse arguments with `extractArg`:

    def func(*args, **kwargs) -> Any:
        """Let us find a str indicating name in these arguments!"""
        nameKeys = stringList('name, identifier, title, target')
        name, args, kwargs = extractArg(str, nameKeys, *args, **kwargs)
        #  And lets find an integer to represent the amount:
        amountKeys = stringList('amount, count, quantity')
        amount, args, kwargs = extractArg(int, nameKeys, *args, **kwargs

In the above example, we used two powerful convenience functions from
WorkToy to parse an arbitrary collection of positional and keyword
arguments to a `str` and an `int`. The `stringList` splits our text on
commas followed by a space, providing:

    nameKeys
    >>> ['name', 'identifier', 'title', 'target']
    amountKeys
    >>> ['amount, count, quantity']

In the next part, `extractArg` finds the first keyword argument from the
list of keys that belongs to the type given and returns it. If it finds
no such argument, it returns the first positional argument encountered
having the indicated type. This allows a great deal of flexibility in how
a function is invoked.

## The None-aware 'maybe'

In a programming language which shall rename nameless as well as typeless,
the following syntax is available:

    const func = (arg = null) => {
        let val1 = arg || 1.0;
        let val2 = arg ?? 1.0;
        return [val1, val2]; }

In the above code, the default argument is set to null (in this context
null is treated the same as None in Python). The `??` operator is the
null-coalescence operator, which is nearly the same as the `or` operator.  
Consider the return value obtained from calling `func()`:

    func()
    >>> (2)  [1, 1]

This makes sense, but what happens when we call the function on a falsy
value other than null, such as 0:

    func(0)
    >>> (3)  [1, 0]

The first value in the return value comes from using the pipes (the
logical or operator), is not aware of the difference between null and
other falsy values. The null-coalescence operator is able to tell the
difference. The WorkToy module brings this to python along with several
derived utility functions:

### `maybe`

In the below python code, we implement the same function using the maybe
function from WorkToy:

    def func(arg: Any = None) -> Any:
        """Function using the maybe from the WorkToy module"""
        val1 = arg or 1.0
        val2 = maybe(arg, 1.0)
        return [val1, val2]

The implementation of maybe simply follows a common pattern:

    def maybe(*args) -> Any:
        """Implementation of maybe returns the first argument given that 
        is different from None. If no such argument is found None is 
        returned."""
        for arg in args:
            if arg is not None: 
                return arg
        return None

Unlike the `??` operator, the `maybe` operator handles an arbitrary
number of arguments.

### `maybeType`

The first of the derived functions finds the first argument of a
particular type:

    def maybeType(type_: type, *args) -> type_:
        """Returns the first argument of given type"""

### `maybeTypes`

Adding an 's' returns every argument of given type. Further, it supports
keyword arguments `pad: int` and `padChar: Any`. If `pad` is given it
defines the length of the returned list padded with `padChar` or `None`
by default. Setting `pad` will either pad or crop as necessary.
