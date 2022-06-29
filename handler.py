"""
A *Configuration Handler* can read, templatize, and write configurations of a specific *configuration type*.
Add support for new configuration types by deriving from class `handler.ConfigHdl`.
Currently supported configuration types are: text configuration files, sometimes referred to as 'ini configuration files'.

A *Template Handler* can read, instantiate, and write templates of a specific configuration type.
Add support for templates of new configuration types by deriving from class `handler.TemplateHdl`.
"""
import io, os, re

import provider as prvd, descriptor as dscr

TMPL_FILENAME_SUFFIX = '.tmpl'

TMPL_KEYWORD_PREFIX = '{{.'
TMPL_KEYWORD_SUFFIX = '}}'


class ConfigHdl:
    """
    Stateless configuration objects, i.e., the actual configuration will be stored and maintained on disk,
    but never held as part of objects of this class. That's why we refer to it as Handler by suffix 'Hdl'.
    """
    def __init__(self, config_id):
        self._config_id = config_id

    def validate(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def write(self, config):
        raise NotImplementedError

    def templatize(self, desc: dscr.DeploymentDescriptor):
        raise NotImplementedError

    def config_id(self) -> str:
        return self._config_id


class FileConfigHdl(ConfigHdl):

    def read(self) -> str:
        if os.path.exists(self.config_id()):
            file = open(self.config_id(), 'r')
            config = file.read()
            file.close()
            return config

    def write(self, config: str):
        file = open(self.config_id(), 'w')
        file.write(config)
        file.close()


class IniFileConfigHdl(FileConfigHdl):

    def __init__(self, config_id: str):
        super(IniFileConfigHdl, self).__init__(config_id)

    def templatize(self, desc: dscr.IniFileConfigDeploymentDescriptor) -> str:
        """
        Creates a template from a specific configuration by replacing actual occurrences of
        configuration variables values by templating keywords, i.e., corresponding environment variable names,
        which are enclosed in double curly braces starting with a dot before the keyword (like templating in Go).
        :param desc:
        :return:
        """
        template = ''

        vars_found = []
        for line in io.StringIO(self.read()).readlines():
            for key in desc.assignments().keys():
                match_expr = '^\s*' + key + '\s*' + desc.assignment_op() + '[ \t]*' \
                    if not desc.assignment_shell_style() else '^\s*' + key + desc.assignment_op()
                match = re.search(match_expr, line)
                if match:
                    line = match.group(0) + \
                           TMPL_KEYWORD_PREFIX + desc.assignments()[key] + TMPL_KEYWORD_SUFFIX + '\n'
                    vars_found += [key]
                    break
            template += line
        print('Found variable(s) during templatization \'{}\'.'.format(', '.join(vars_found)))

        # check all assignments keys are found as variables in configuration
        vars_not_found = set(desc.assignments().keys()).difference(set(vars_found))
        if vars_not_found:
            whitespace = ' ' if not desc.assignment_shell_style() else ''
            if template[-1] != '\n':
                template += '\n'
            for key in vars_not_found:
                template += '{}{}{}{}{}{}{}\n'.format(key, whitespace, desc.assignment_op(), whitespace,
                                                    TMPL_KEYWORD_PREFIX, desc.assignments()[key], TMPL_KEYWORD_SUFFIX)
            print('Added variable(s) not found during templatization \'{}\'.'.format(', '.join(vars_not_found)))

        # check every variable occured only once in the configuration if applicable
        multi_occurrences = [v for v in vars_found if vars_found.count(v) > 1]
        if not desc.allow_multi_occurrence() and len(multi_occurrences) > 0:
            raise ValueError('Variable(s) occur multiple times in configuration: {}.'.format(', '.join(multi_occurrences)))

        return template


class TemplateHdl:

    def __init__(self, config_hdl: ConfigHdl):
        self._config_hdl = config_hdl
        self._template_id = None

    def read(self):
        raise NotImplementedError

    def write(self, template):
        raise NotImplementedError

    @classmethod
    def instantiate(cls, template, provider: prvd.Provider):
        raise NotImplementedError

    def config_hdl(self):
        return self._config_hdl

    def template_id(self) -> str:
        return self._template_id


class FileTemplateHdl(TemplateHdl):

    def __init__(self, config_hdl: IniFileConfigHdl):
        super(FileTemplateHdl, self).__init__(config_hdl)
        self._template_id = config_hdl.config_id() + TMPL_FILENAME_SUFFIX

    def read(self) -> str:
        if os.path.exists(self.template_id()):
            file = open(self.template_id(), 'r')
            template = file.read()
            file.close()
            return template

    def write(self, template: str):
        file = open(self.template_id(), 'w')
        file.write(template)
        file.close()

    @classmethod
    def instantiate(cls, template: str, provider: prvd.Provider) -> str:
        """
        Notions:
        * template string, e.g., `{{.VARIABLE_NAME}}`
        * template keyword, e.g., `VARIABLE_NAME`

        :param template:
        :param provider: Secrets provider.
        :return:
        """
        config = ''
        tmpl_kw_set = []

        for line in io.StringIO(template).readlines():
            # search for template string
            match = re.search(TMPL_KEYWORD_PREFIX + '.+' + TMPL_KEYWORD_SUFFIX, line)
            if match:
                tmpl_str = match.group(0)
                tmpl_kw = tmpl_str[len(TMPL_KEYWORD_PREFIX):-len(TMPL_KEYWORD_SUFFIX)]

                try:
                    line = line[:line.find(tmpl_str)] + \
                           provider.get(tmpl_kw) + \
                           line[line.find(tmpl_str) + len(tmpl_str):]
                    tmpl_kw_set += [tmpl_kw]
                except KeyError:
                    raise ValueError('Referenced template keyword \'{}\' not available from secrets provider {}.' \
                                     .format(tmpl_kw, provider.__class__.__name__))
            config += line

        print('Instantiated template keyword(s) \'{}\'.'.format(', '.join(tmpl_kw_set)))

        return config
