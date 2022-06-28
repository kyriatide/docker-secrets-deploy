# Test deploy with persisting a template

# Pre-condition: there is a config file in config/example.conf
# Post-condition: there will be no template file after execution

import sys, os, pathlib
import descriptor as dscr, run, handler as tmpl

# set environment variables
scriptpath = pathlib.Path(__file__).parent.absolute()
os.environ[dscr.EnvironLoader.SOURCE_ENV_VAR] = '\
    [{"config": "' + str(scriptpath) + '/config/example.conf", \
      "assign": {"pwd": "ENV_PASSWORD"}, "persist": true}] \
'
os.environ['ENV_PASSWORD'] = 'bLupdLr4R2HY'

# load deployment descriptor
desc = dscr.EnvironLoader.load()[0]

run.deploy()

# print generated template
template_id = tmpl.FileTemplateHdl(tmpl.IniFileConfigHdl(desc.config_id())).template_id()
sys.argv += ['cat', template_id]
run.cmd(sys.argv[1:])

# delete generated template
os.remove(template_id)
