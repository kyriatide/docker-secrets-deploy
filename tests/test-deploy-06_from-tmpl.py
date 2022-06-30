# Test deploy with existing template but lacking config

# Precondition: config file exists
# Postcondition: config file exists unchanged, template file does not exist

import os, pathlib, shutil
import descriptor as dscr, run, handler

# set environment variables
scriptpath = pathlib.Path(__file__).parent.absolute()
os.environ[dscr.EnvironLoader.SOURCE_ENV_VAR] = '\
    [{"config": "' + str(scriptpath) + '/config/example.conf", \
      "persist": true, "templatize": false}] \
'
os.environ['ENV_PASSWORD'] = 'bLupdLr4R2HY'

# load deployment descriptor
desc = dscr.EnvironLoader.load()[0]
assert isinstance(desc, dscr.IniFileConfigDeploymentDescriptor)

config_hdl = handler.IniFileConfigHdl(desc.config_id())
template_hdl = handler.FileTemplateHdl(config_hdl)

# Prepare: create template and backup config
assert os.path.exists(config_hdl.config_id())
template = config_hdl.templatize(
    dscr.IniFileConfigDeploymentDescriptor.parse(
        **{'config': desc.config_id(), 'assign': {'pwd': 'ENV_PASSWORD'}, 'assignment_op': desc.assignment_op()}
    )
)
template_hdl.write(template)
#
shutil.move(desc.config_id(), desc.config_id() + '.backup')

# Test: create config from template
assert os.path.exists(template_hdl.template_id()) and not os.path.exists(config_hdl.config_id())
run.deploy()
assert os.path.exists(config_hdl.config_id())

args = ['cat', template_hdl.template_id()]
run.cmd(args)
#
args = ['cat', config_hdl.config_id()]
run.cmd(args)

#
os.remove(template_hdl.template_id())
shutil.move(desc.config_id() + '.backup', desc.config_id())