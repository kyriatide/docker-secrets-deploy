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

import importlib
import json, os
import handler as tmpl


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
        :param config: Conifguration Id.
        :param assign: Variable assignments that shall be made in the referenced configuration.
        """
        # configuration-id is mandatory
        assert config
        assert (templatize and assign is not None and len(assign) > 0) or \
               (not templatize and (assign is None or len(assign) == 0))

        self._config_id = config
        self._templatize = templatize
        self._assignments = assign
        self._persist = persist

    def config_id(self):
        return self._config_id

    def assignments(self):
        return self._assignments

    def persist(self):
        return self._persist

    def templatize(self):
        return self._templatize

    def args(self) -> dict:
        """
        :return: Returns deployment descriptor attributes as dict, with keys named following coding conventions/names,
            not serialization conventions/names.
        """
        return {'config_id': self.config_id(), 'templatize': self.templatize(),
                'assignments': self.assignments(), 'persist': self.persist()}

    @classmethod
    def parse(cls, config_type: str=None, **kwargs) -> 'DeploymentDescriptor':
        """
        Parses a single deployment descriptor item represented by kwargs into a deployment descriptor instance of the
        according class.
        It uses the deployment descriptor to identify the respective configuration type. This is done either by
        using the explicitly specified attribute config_type, or by deriving the type from the syntax of the config_id.
        """
        if config_type is not None:
            # config_type is explicitly specified
            dscr_cls = config_type + DeploymentDescriptor.__name__
        else:
            # derive configuration type from configuration id
            # todo: can further use filename extensions as indicators for correct config types
            config_id = DeploymentDescriptor(**kwargs).config_id()
            if tmpl.IniFileConfigHdl(config_id).validate():
                dscr_cls = IniFileConfigDeploymentDescriptor.__name__
            else:
                raise ValueError('Configuration identifier \'{}\' is not supported.'.format(config_id))

        return getattr(importlib.import_module('descriptor'), dscr_cls)(**kwargs)


class IniFileConfigDeploymentDescriptor(DeploymentDescriptor):
    """
    Describes the deployment of secrets/values into an ini configuration file.
    """
    def __init__(self, assignment_op: chr = '=', allow_multi_occurance: bool = False, **kwargs):
        """
        Validates parameters specific to the configuration type, alongside instantiation via the superclass' constructor.
        :param assignment_op:
        :param kwargs: All other deployment descriptor attributes.
        """
        assert assignment_op in ['=', ':']
        self._assignment_op = assignment_op

        self._allow_multi_occurance = allow_multi_occurance

        super(IniFileConfigDeploymentDescriptor, self).__init__(**kwargs)

    def assignment_op(self):
        return self._assignment_op

    def allow_multi_occurance(self):
        return self._allow_multi_occurance

    def args(self):
        return {
            **super(IniFileConfigDeploymentDescriptor, self).args(),
            **{'assignment_op': self.assignment_op(), 'allow_multi_occurance': self.allow_multi_occurance()}
        }


class Loader:
    @classmethod
    def load(cls) -> list:
        """
        Loads a deployment descriptor from source.
        :return: List of loaded deployment descriptor items.
        """
        raise NotImplementedError

    @classmethod
    def parse(cls, dscrs: list):
        """
        Parses a list of dicts into a list of deployment descriptor objects of according type.
        :param dscrs: List of dicts.
        :return: List of deployment descriptors.
        """
        return [DeploymentDescriptor.parse(**dscr) for dscr in dscrs]


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

        return EnvironLoader.parse(raw_dscr if isinstance(raw_dscr, list) else [raw_dscr])
