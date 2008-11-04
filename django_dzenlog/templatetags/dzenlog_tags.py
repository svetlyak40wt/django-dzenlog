from django.template import Library, Node, Variable
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse

from pdb import set_trace

register = Library()

class CallNode(Node):
    def __init__(self, args, kwargs, asvar, func_name=None, obj_name=None, method_name=None):
        self.func_name = func_name
        self.obj_name = obj_name
        self.method_name = method_name
        self.args = args 
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        if self.func_name is not None:
            func = self.func_name.resolve(context)
        else:
            obj = self.obj_name.resolve(context)
            #method = self.method_name.resolve(context)
            func = getattr(obj, self.method_name)

        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        result = func(*args, **kwargs)

        if self.asvar:
            context[self.asvar] = result
            return ''
        else:
            return result

def call(parser, token):
    '''
    Call function or object's method and, optionally,
    place result into the context variable.

    Examples:
        {% call obj.get_absolute_url as abs_url %}
        {% call obj.some_method 42, var='test' %}

    If you don't pass an output variable's name, then result
    will be on the tag's output.
    '''
    bits = token.contents.split(' ')
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (function's name)" % bits[0])

    if '.' in bits[1]:
        obj_name, method_name = bits[1].split('.')
        names = dict(obj_name = Variable(obj_name), method_name = method_name)
    else:
        names = dict(func_name = Variable(bits[1]))

    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return CallNode(args, kwargs, asvar, **names)
call = register.tag(call)

