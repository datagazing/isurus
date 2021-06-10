import datetime
import importlib
import itertools
import logging
import os
import re
import sys
import typing

import attr
import mako.template
import mako.lookup
import mako.exceptions

import optini

def datestamp(format='%Y-%m-%d_%H-%M-%S'):
    return(datetime.datetime.now().strftime(format))

@attr.s(auto_attribs=True)
class Isurus:
    '''
    Class that simplifies rendering arbitrary mako templates

    - Supports automatically loading various python modules
    - NOT designed to be memory-efficient (many strings in memory)

    Examples
    --------

    .. code-block:: python

      import isurus
      input = 'asdf <% myvar = 1 %> ${myvar} fdsa ${str(pandas.DataFrame)}'
      template = isurus.Isurus(input)
      template.add_import('pandas')
      print(template)

    Attributes
    ----------

    input : str
        template input as either file name or string
    markdown : bool (default: False)
        disable '##' mako comments by wrapping with Mako <%text> tags
        '##' comments conflict with markdown headers
        set markdown=False to pass '##' through verbatim
    save : bool (default: False)
        saving a copy of pre-rendered template in current dir
    '''
    input: str
    markdown: bool = False
    save: bool = False
    savefile: str = f"isurus_{datestamp()}.mako"
    _pre: typing.List[int] = attr.Factory(list)
    _post: typing.List[int] = attr.Factory(list)
    _imports: typing.Set[str] = attr.Factory(set)

    def __attrs_post_init__(self):
        if os.path.exists(self.input):
            self.input = open(self.input, 'r').read()
        # else assume input is the mako template as a string

    def template(self):
        'construct full template as string'
        pre = self.pre()
        post = self.post()
        # break input into list of lines for consistency with pre and post
        lines = map(
            lambda x: x.rstrip("\n"),
            self.input.split("\n"),
        )
        if self.markdown:
            # disable mako '##' comments
            # ^## conflicts with markdown header syntax
            lines = map(
                lambda x: re.sub(r'^##', '<%text>##</%text>', x),
                lines,
            )
        lines = list(lines)
        # join everything back together as a single string
        return("\n".join(list(itertools.chain(pre, lines, post))) + "\n")

    def render(self):
        # to support loading sub-templates
        lookup_dirs = []
        # always look in the current directory
        lookup_dirs.append(".")
        lookup = mako.lookup.TemplateLookup(directories=lookup_dirs)
        # mako can only load templates from string or filename
        # so truly lazy template read is difficult
        # could construct another temporary file on disk
        # reading the template into memory seems like best compromise
        tmpl = self.template()
        if self.save:
            logging.info(f"saving complete intermediate template...")
            open(self.savefile, 'w').write(tmpl)
            logging.info(f"created intermediate template: {self.savefile}")
        try:
            return(mako.template.Template(text=tmpl, lookup=lookup).render())
        except Exception as e:
            self.error("mako failed to render template")
            self.error(f"{e}")
            traceback = mako.exceptions.RichTraceback()
            for (filename, lineno, function, line) in traceback.traceback:
                logging.debug(f"file {filename}, line {lineno}, in {function}")
                logging.debug(f"line: {line}")
            sys.exit(1)

    def renderfile(self, filename):
        'write rendered template to file'
        with open(filename, "wt") as f:
            f.write(self.render())
        logging.info(f"wrote {filename}")

    def verify_import(self, import_statement):
        'examine import statement, flag potential problems'
        module = None
        element = None

        import_statement = import_statement.strip()

        # treat single tokens as module names, prepend 'import '
        pattern = r'^(\w+)$'
        match = re.search(pattern, import_statement)
        if match:
            module = match.group(1)
            import_statement = f"import {module}"
        # this should also catch 'import x as y'
        pattern = r'^import\s+(\w+)'
        match = re.search(pattern, import_statement)
        if match:
            module = match.group(1)
        # this should also catch 'from x import y as z'
        pattern = r'^from\s+(\w+)\s+import\s+(\w+)'
        match = re.search(pattern, import_statement)
        if match:
            module = m.group(1)
            element = m.group(2)
        # checking if element exists without importing is a hassle
        # ignore such additional check for now

        if module is None:
            self.error(f"unable to parse: {import_statement}")
        else:
            if importlib.util.find_spec(module) is None:
                self.error(f"unable to find module {module}")
                sys.exit(1)
        return(import_statement)

    def add_import(self, import_statement):
        'import module into template namespace'
        import_statement = self.verify_import(import_statement)
        self._imports.add(import_statement)

    def pre(self):
        'return template header'
        preamble = []
        preamble.append(r'<%!')
        preamble.extend(sorted(self._imports))
        preamble.extend(self._pre)
        preamble.append(r'%>')
        return(preamble)

    def post(self):
        'return template footer'
        post = []
        # no need for enclusing tags if post is empty
        if len(self._post) == 0:
            return([])
        post.append(r'<%')
        post.extend(self._post)
        post.append(r'%>')
        return(post)

    def add_pre(self, pythoncode):
        'add arbitrary python code to template header'
        self._pre.append(pythoncode)

    def add_post(self, pythoncode):
        'add arbitrary python code to template footer'
        self._post.append(pythoncode)

    def __str__(self):
        return self.render()

def config(appname):
    description='Humane Mako template preprocessor interface/filter'

    spec = {
        'input': {
            'help': 'input file (Mako template)',
            'type': str,
            'default': sys.argv[-1],
        },
        'output': {
            'help': 'output file',
            'type': str,
        },
        'Replace': {
            'help': 'replace output file if it already exists',
        },
        'Markdown': {
            'help': 'assume markdown input (disable "##" Mako comments)',
        },
    }
    confobj = optini.Config(
        logging=True,
        appname=appname,
        description=description,
        spec=spec,
    )
    return confobj

def derive_output(input):
    match = re.search(r'(.*)\.mako$', input, re.IGNORECASE)
    if match:
        output = match.group(1)
    else:
        output = f"isurus_out_{datestamp()}.txt"
    logging.debug(f"output = {output}")
    return output
    
def main():
    confobj = config(appname='isurus')
    logging.debug(f"input = {optini.opt.input}")
    template = Isurus(optini.opt.input, markdown=optini.opt.Markdown)
    if optini.opt.output is None:
        optini.opt.output = derive_output(optini.opt.input)
    if os.path.exists(optini.opt.output) and not optini.opt.Replace:
        logging.error(f"output file exists: {optini.opt.output}")
        logging.error(f"replace option (-R/--Replace) not specified")
        sys.exit(1)
    template.renderfile(optini.opt.output)

if __name__ == '__main__':
    main()
