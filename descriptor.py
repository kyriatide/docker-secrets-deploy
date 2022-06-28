"""
A *deployment descriptor* describes the deployment of secrets/values into a configuration for a specific
configuration type, i.e., how and which variables in a confiuration are to be set in course of a deployment.
A deployment descriptor is used by a configuration handler to templatize, i.e., to create a template from a configuration.
Add support for new configuration types by deriving from class `descriptor.DeploymentDescriptor`.
These subclasses store and validate attributes specific to the configuration type.

A *loader* loads deployment descriptors from a source.
Add support for loading deployment descriptors from new sources by deriving from class `descriptor.Loader`.
Currently supported are loading: from environment variable (`EnvironLoader`).

"""

import importlib, json, os, re, typing


class DeploymentDescriptor:
    """
    Describes the deployment of secrets/values into a configuration.
    A deployment takes place in  one of two forms:
    a) instantiate a template to write a new configuration. In this case the template identifier is derived from
        parameter config, and parameter assign is None as no assigmnents occur.
    b) first, create a template from a config, and second, instantiate the template. In this case parameter
        assign must hold a dict describing which config variables to set to which values.
    :param config: Identifies the configuration to deploy to.
    :param assign: Describes which config variables to set to which values.
    :param persist: Whether to persist (store) the template (templatized from the configuration).
    """
    def __init__(self, config: str=None, templatize: bool=True, assign: dict=None, persist: bool=False, **kwargs):
        """
        Note that the parameters of this method follow the JSON serialization attribute names of deployment
        descriptors, which does not always align with the naming conventions used throghout the code.
        :param config: Configuration id.
        :param assign: Variable assignments that shall be made in the referenced configuration.
        """
        # configuration-id is mandatory
        assert config and isinstance(config, str) and len(config) > 0
        self._config_id = config

        assert isinstance(templatize, bool)
        assert assign is None or isinstance(assign, dict)
        assert (templatize and assign is not None and len(assign) > 0) or \
               (not templatize and (assign is None or len(assign) == 0))
        self._templatize = templatize
        self._assignments = assign
        
        assert isinstance(persist, bool)
        self._persist = persist

    def config_id(self):
        return self._config_id

    def assignments(self):
        return self._assignments

    def persist(self):
        return self._persist

    def templatize(self):
        return self._templatize

    @classmethod
    def parse(cls, config_type: str=None, **kwargs) -> 'DeploymentDescriptor':
        """
        Parses a single deployment descriptor represented by kwargs into a deployment descriptor object of the
        correct class.
        It uses the deployment descriptor to identify the respective configuration type. This is done either by
        using the explicitly specified attribute config_type, or by identifying the type by the syntax of the config_id.
        """
        if config_type is not None:
            # config_type is explicitly specified
            dscr_cls = config_type + DeploymentDescriptor.__name__
        else:
            # identify configuration type by configuration id
            config_id = DeploymentDescriptor(**kwargs).config_id()
            # todo: identification rules to become more elaborate, e.g., use further indicators such as filename extensions
            #  for correct identification of config type
            # currently very basic, least specific rule: if it's a file, assume its an ini config files
            if FileConfigDeploymentDescriptor.is_valid_config_id(config_id):
                dscr_cls = IniFileConfigDeploymentDescriptor.__name__
            else:
                raise ValueError('Configuration identifier \'{}\' is not supported.'.format(config_id))

        return getattr(importlib.import_module('descriptor'), dscr_cls)(**kwargs)


class FileConfigDeploymentDescriptor(DeploymentDescriptor):

    def __init__(self, config: str=None, **kwargs):
        super(FileConfigDeploymentDescriptor, self).__init__(**{**{'config': config}, **kwargs})

        assert FileConfigDeploymentDescriptor.is_valid_config_id(config)

    @classmethod
    def is_valid_config_id(cls, config_id: str):
        """
        Only file URIs without host name and with absolute file paths are supported.
        """""
        VALID_FILEPATH_CHAR = '[A-z0-9-_+ \.]'
        RE_ABSOLUTE_PATH = '^([A-Z]:)?\{1}({0}+\{1})*({0}+(\.{0}*)?)$'.format(VALID_FILEPATH_CHAR, os.path.sep)
        FILE_URI_PREFIX = 'file://'

        return ((config_id.find(FILE_URI_PREFIX) == 0) and
                re.match(RE_ABSOLUTE_PATH, config_id[len(FILE_URI_PREFIX):])) or \
               re.match(RE_ABSOLUTE_PATH, config_id)


class IniFileConfigDeploymentDescriptor(FileConfigDeploymentDescriptor):
    """
    Describes the deployment of secrets/values into an ini configuration file.
    """
    def __init__(self, assignment_op: str = '=', allow_multi_occurance: bool = False, **kwargs):
        """
        Validates parameters specific to the configuration type, alongside instantiation via the superclass' constructor.
        :param assignment_op:
        :param kwargs: All other deployment descriptor attributes.
        """
        super(IniFileConfigDeploymentDescriptor, self).__init__(**kwargs)

        assert isinstance(assignment_op, str) and assignment_op in ['=', ':']
        self._assignment_op = assignment_op

        assert isinstance(allow_multi_occurance, bool)
        self._allow_multi_occurance = allow_multi_occurance

    def assignment_op(self):
        return self._assignment_op

    def allow_multi_occurance(self):
        return self._allow_multi_occurance


class Loader:
    @classmethod
    def load(cls) -> list:
        """
        Loads a deployment descriptor from source.
        :return: List of loaded deployment descriptor items.
        """
        raise NotImplementedError

    @classmethod
    def parse(cls, raw_dscr: typing.Union[list, dict]):
        """
        Parses a raw deployment descriptor or a list of raw deployment descriptors into objects of correct class.
        :param raw_dscr: Dict or list of dicts representing raw deployment descriptors.
        :return: List of deployment descriptor objects.
        """
        return [DeploymentDescriptor.parse(**dscr) for dscr in (raw_dscr if isinstance(raw_dscr, list) else [raw_dscr])]


class EnvironLoader(Loader):
    SOURCE_ENV_VAR = 'DCKR_SCRTS_DEPLOY'

    @classmethod
    def load(cls) -> list:
        """
        Loads a deployment descriptor from an environment variable named after SOURCE_ENV_VAR.
        :return: List of loaded deployment descriptor items.
        """
        try:
            raw_dscr = json.loads(os.environ[EnvironLoader.SOURCE_ENV_VAR])
        except KeyError:
            raise ValueError('Failed to load descriptor from environment variable \'{}\' which does not exist.'.format(EnvironLoader.SOURCE_ENV_VAR))

        return EnvironLoader.parse(raw_dscr)
