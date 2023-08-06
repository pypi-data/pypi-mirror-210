import functools
import bs4
import json

gen_soup = lambda s='', p='html.parser': bs4.BeautifulSoup(s, p)

def dict_deep_update(orig_dict, new_dict):
    import collections.abc
    for key, val in new_dict.items():
        if isinstance(val, collections.abc.Mapping):
            tmp = dict_deep_update(orig_dict.get(key, { }), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = (orig_dict.get(key, []) + val)
        else:
            orig_dict[key] = new_dict[key]
    return orig_dict

### core

class NonWidgetBlock:
    def __init__(self, content):
        self.content = content
        self.parent = None
        self.soup = None

    def _set_parent(self, p):
        self.parent = p
    
    def build(self):
        return self.content

class Widget:
    root_tag = 'widget-tag'
    props = {}
    deps = {}
    style = {}
    root_align = 'left'
    content_align = 'left'
    ignored_props = []
    _build_steps = {}
    _not_set_flag = '__NOT_SET__'
    _build_count = 0

    def __init__(self, *children, **attrs):
        self._blocks = []
        self.parent = None

        for dep_name, d in self.deps.items():
            if 'name' not in d:
                d['name'] = dep_name
        
        for k, v in attrs.items():
            current = getattr(self, k, self._not_set_flag)
            exists = current != self._not_set_flag
            if not exists:
                self.__dict__[k] = v
            else:
                if isinstance(current, dict):
                    merged = dict_deep_update(current.copy(), v)
                    self.__dict__[k] = merged
                else:
                    self.__dict__[k] = v
        
        props, children = self._parse_chilldren(children)
        self.props = {**self.props, **props}
        self.children = children
        self._extend_children(*children)

    @classmethod
    def build_step(cls, priority=0):
        def deco_fn(fn):
            cname = cls.__name__
            mro = cls.__mro__
            fname = fn.__name__

            if cls not in cls._build_steps:
                cls._build_steps[cls] = {}
            
            safe_fname = f'{cname}_{fname}'
            cls._build_steps[cls][safe_fname] = dict(priority=priority, fn=fn)

            @functools.wraps(fn)
            def deco_args(*a, **kw):
                return fn(*a, **kw)
            return deco_args
        return deco_fn

    def add(self, *children):
        self._extend_children(*children)
    
    def insert(self, ix, child):
        return self._insert_child(child, ix)

    def gen_soup(self, s=''):
        return gen_soup(s).find()

    def _parse_chilldren(self, children):
        if len(children) == 0:
            props = {}
            children = []
        else:
            if isinstance(children[0], dict):
                props = children[0]
                children = children[1:]
            else:
                props = {}
        return props, children

    def _insert_child(self, c, ix=None):
        if ix is None:
            ix = len(self._blocks)
        self._blocks.insert(ix, c)

    def _extend_children(self, *children):
        for i in children:
            if hasattr(i, '_set_parent'):
                i._set_parent(self)
            else:
                i = NonWidgetBlock(i)
                i._set_parent(self)
            self._insert_child(i)

    def _set_parent(self, p):
        self.parent = p

    def _get_methods(self):
        ret = {}
        for k in dir(self):
            v = getattr(self, k)
            if not callable(v):
                continue
            ret[k] = v
        return ret

    def _get_flagged_fns(self, flag, as_generator=False, with_priority=False):
        ret = {}
        methods = self._get_methods()
        for fname, fn in methods.items():
            priority = getattr(fn, flag, None)
            if priority is not None:
                if with_priority:
                    ret[fname] = (fn, priority)
                else:
                    ret[fname] = fn
        return ret.items() if as_generator else ret

    def set_soup_dep(self, name, soup, priority=0):
        self.deps[name] = dict(name=name, soup=soup, priority=priority)

    def get_deps(self):
        return sorted(self.deps.values(), key=lambda x: x['priority'])

    def ignore_prop(self, name):
        self.ignored_props.add(name)

    def __safe_style_s(self):
        s = ''
        for k, v in self.style.items():
            s += f'{k}: {v};'
        return s

    def as_webpage(self):
        widget_deps = self.get_deps()
        widget_soup = self.build()
        tmpl = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="ie=edge">
        </head>
        <body>
        </body>
        </html>
        '''

        soup = gen_soup(tmpl)
        head = soup.find('head')
        for dep_data in widget_deps:
            dep_soup = dep_data['soup']
            head.append(dep_soup)

        body = soup.find('body')
        body.append(widget_soup)

        return soup.prettify()

    def build(self):
        cls = self.__class__
        cname = cls.__name__
        self._build_count += 1
        assert self._build_count == 1, f'Widget is singleton. You just tried to reuse a {cname} instance'
        cls = self.__class__
        cname = cls.__name__
        self.soup = self.gen_soup(f'''
            <{self.root_tag}>
        ''')

        #cmt = gen_soup(f'<!-- Widget {cname} start -->')
        #self.soup.insert(0, cmt)

        mro = cls.__mro__
        build_step_fns = {}
        for i in mro:
            if i in self._build_steps:
                build_step_fns.update(self._build_steps[i])

        build_step_fns = sorted(build_step_fns.items(), key = lambda x: x[1]['priority'], reverse=1)
        for fname, d in build_step_fns:
            fn = d['fn']
            priority = d['priority']
            ret = fn(self)
            t = type(ret)
            if issubclass(t, Widget):
                self.soup = ret.build()
            elif isinstance(ret, bs4.element.Tag):
                self.soup = ret
            elif isinstance(ret, str):
                self.soup = gen_soup(ret)

        for i in self._blocks:
            if hasattr(i, 'build'):
                b = i.build()
            else:
                b = str(i.content)
            self.soup.append(b)

        to_update = {
            k: v for k, v in self.props.items() 
                if k not in self.ignored_props
        }
        self.soup.attrs.update(to_update)

        if self.root_align == 'left':
            self.style.update({
                'margin-right': 'auto',
            })
        elif self.root_align == 'center':
            self.style.update({
                'margin-left': 'auto',
                'margin-right': 'auto',
            })
        elif self.root_align == 'right':
            self.style.update({
                'margin-left': 'auto',
            })
        else:
            raise Exception(f'"{self.root_align}" is not a valid "root_align" value')

        if self.content_align == 'left':
            self.style.update({
                'text-align': 'left',
            })
        elif self.content_align == 'center':
            self.style.update({
                'text-align': 'center',
            })
        elif self.content_align == 'right':
            self.style.update({
                'text-align': 'right',
            })
        else:
            raise Exception(f'"{self.content_align}" is not a valid "content_align" value')
        
        if self.style:
            safe_style = self.__safe_style_s()
            if 'style' in self.soup.attrs:
                self.soup.attrs['style'] += safe_style
            else:
                self.soup.attrs['style'] = safe_style
        
        #cmt = gen_soup(f'<!-- Widget {cname} end -->')
        #self.soup.append(cmt)
        
        return self.soup

class Tag(Widget):
    def __init__(self, name, *children, **attrs):
        self.root_tag = name
        super().__init__(*children, **attrs)

class Soup(Widget):
    def __init__(self, s):
        self.content = s
        self.parent = None
    
    def _set_parent(self, p):
        self.parent = p

    def build(self):
        return gen_soup(self.content).find()