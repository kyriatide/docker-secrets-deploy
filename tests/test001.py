import sys, os, pathlib
import descriptor as dscr, run, handler as tmpl

# set environment variables
import provider

scriptpath = pathlib.Path(__file__).parent.absolute()
os.environ[dscr.EnvironLoader.SOURCE_ENV_VAR] = '\
    [{"config": "' + str(scriptpath) + '/config/example.conf", "assign": {"pwd": "ENV_PASSWORD"}}] \
'
os.environ['ENV_PASSWORD'] = 'bLupdLr4R2HY'

# load deployment descriptor
desc = dscr.EnvironLoader.load()[0]

# print config with secrets deployed
print(tmpl.FileTemplateHdl.instantiate(
    tmpl.IniFileConfigHdl(desc.config_id()).templatize(desc), provider.EnvironProvider())
)
# print template
print(tmpl.IniFileConfigHdl(desc.config_id()).templatize(desc))

# print config using cmd
args = ['cat', str(scriptpath) + '/config/example.conf']
run.cmd(args)