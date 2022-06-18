#!/bin/python3
#

import sys, subprocess
import handler, descriptor as dscr, provider


def deploy(loader_cls: dscr.Loader = dscr.EnvironLoader,
           provider_cls: provider.Provider = provider.EnvironProvider,
           config_cls: handler.ConfigHdl = handler.IniFileConfigHdl):
    """
    For deployment the following is being done:
    * (1) get a deployment descriptor (by configuration type) loaded by a loader (by loader type)
    * (2) get a template (by config type), identified by the deployment descriptor
    *   (a) if templatize, derive a template from the configuration (by config type) using the deployment descriptor; or
    *   (b) otherwise use the existing template; and
    *   (c) optional: persist the template.
    * (3) instantiate the template using the secrets provider (by secrets provider type) and persist the config.
    """
    # Load deployment descriptors using the given loader
    descs = loader_cls.load()

    for desc in descs:
        # (1) get a deployment descriptor
        assert isinstance(desc, dscr.DeploymentDescriptor)
        print('Deploying secrets and variables into {} ... '.format(desc.config_id()))

        config_hdl = handler.IniFileConfigHdl(desc.config_id())
        template_hdl = handler.FileTemplateHdl(config_hdl)

        # (2) get a template
        if desc.templatize():
            # (a) derive template from configuration
            if not config_hdl.read():
                raise ValueError('Configuration not found but required for templatization (as set by attribute \'templatize\').')
            template = config_hdl.templatize(desc)
        else:
            # (b) use template right away
            if not template_hdl.read():
                raise ValueError('Template not found but required for instantiation (as set by attribute \'tremplatize\').')
            template = template_hdl.read()

        # (c) persist the template
        if desc.persist():
            template_hdl.write(template)

        # (3) instantiate the template using the secrets provider
        config_hdl.write(handler.FileTemplateHdl.instantiate(template, provider_cls()))


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
        _popen = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)

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
