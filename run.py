#!/bin/python3
#
import pathlib, sys, subprocess, importlib
import handler, descriptor as dscr, provider


def deploy(loader_cls: dscr.Loader = dscr.EnvironLoader,
           provider_cls: provider.Provider = provider.EnvironProvider,
           config_cls: handler.ConfigHdl = handler.IniFileConfigHdl,
           template_cls: handler.TemplateHdl = handler.FileTemplateHdl,
           dry_run: bool = False):
    """
    Deploys actual secrets and configuration values into a configuration.

    Deployment is a two-step process:
    First, retrieve a template by either
    a) generating a template from the configuration using the deployment descriptor by *templatization*; or
    b) using an existing template; and
    If desired (if persist is True) persist the template.
    Second, Create a new configuration by *instantiation* of the template using the secrets provider

    The created configuration is persisted by default.

    :param loader_cls: Loader class for loading deployment descriptors.
    :param provider_cls: Provider class for loading secrets and variable values.
    :param config_cls: Configuration class.
    :param template_cls: Template class.
    :param dry_run: Defines whether the configuration created should be persisted to disk. This does not impact
        behavior of deployment descriptor directives that affect persistence of some sort, like persist.
        Parameter dry_run has not been made part of the deployment descriptor, as it is primarily intended to
        be used programmatically to e.g. ease testing, and is not intended for specification by a user via
        a deployment descriptor.
    :returns: Conifguration into which secrets and values have been deployed.
    """
    # Load deployment descriptors using the given loader
    descs = loader_cls.load()

    for desc in descs:
        # retrieve deployment descriptor
        assert isinstance(desc, dscr.DeploymentDescriptor)
        print('Deploying secrets and variables into {} ...'.format(pathlib.Path(desc.config_id()).parts[-1]))

        config_hdl = config_cls(desc.config_id())
        template_hdl = template_cls(config_hdl)

        # 1. retrieve a template
        if desc.templatize():
            # a) derive template from configuration
            if not config_hdl.read():
                raise ValueError('Configuration not found but required for templatization (as set by attribute \'templatize\').')
            template = config_hdl.templatize(desc)
        else:
            # b) use template right away
            if not template_hdl.read():
                raise ValueError('Template not found but required for instantiation (as set by attribute \'tremplatize\').')
            template = template_hdl.read()

        # c) persist the template
        if desc.persist():
            template_hdl.write(template)

        # 2. instantiate the template using the secrets provider
        config = template_hdl.instantiate(template, provider_cls())

        if not dry_run:
            # write new configuration
            config_hdl.write(config)

        return config


def cmd(args) -> int:
    """
    Executes the command defined in the Dockerfile via CMD or provided to the docker container via arguments to docker run,
    redirects stderr to stdout, and outputs to stdout. Exits when the command exits.

    :param args: Command to be run, starting with position 0.
    :returns: Return code of the executed process.
    """
    if len(args) > 0:
        print("Running {} ... ".format(args))
        sys.stdout.flush()

        # https://docs.python.org/3/library/subprocess.html#subprocess.Popen
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0) as _popen:
            while _popen.poll() is None:
                line = _popen.stdout.readline()
                # if not line:
                #     break
                print(line.rstrip().decode(errors='backslashreplace'))
                sys.stdout.flush()

        return _popen.returncode


if __name__ == "__main__":
    deploy()
    cmd(sys.argv[1:])
