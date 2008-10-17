from django.template import Library, Node, Variable
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse

from pdb import set_trace

register = Library()

class CallNode(Node):
    def __init__(self, func_name, args, kwargs, asvar):
        self.func_name = func_name
        self.args = args 
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        func = self.func_name.resolve(context)
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
    bits = token.contents.split(' ')
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    func_name = Variable(bits[1])

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
    return CallNode(func_name, args, kwargs, asvar)
call = register.tag(call)


class RenderNode(Node):
    def __init__(self, object_name):
        self.object_name = object_name

    def render(self, context):
        object = self.object_name.resolve(context)
        bytag_view_name = Variable('bytag_page_name').resolve(context)

        def bytag_url(tag_name):
            return reverse(bytag_view_name, kwargs=dict(slug=tag_name))

        return object.render(bytag_url=bytag_url)

def render(parser, token):
    bits = token.contents.split(' ')
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument"
                                  " (object's name)" % bits[0])
    object_name = Variable(bits[1])
    return RenderNode(object_name)
render = register.tag(render)
