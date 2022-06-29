# Deploying Secrets into Containers

In almost every docker image you have configuration files containing variables that need to be set to the correct values 
when the image is run as container. Sometimes the correct values can be set at the time when the image is
being built (at 'build time', e.g., with `docker build`), and sometimes the correct values can (or should) be set when the 
container is being run (at 'runtime', e.g., with `docker run`).
The latter applies for variables that e.g. differ depending on the runtime environment, like the development or production environment,
but also for secrets, which you wouldn't want to build into the image but deploy or inject into the container at runtime.

The proposed approach provides for setting variables in configuration files to environment variables passed to the 
container at runtime in a lightweight, robust and simple manner. It builds on an extensible framework that allows to add
support for new configuration types and secrets providers amongst others.

Compared to manually maintaining templates and inserting secrets, the approach has the benefits of
declarative specification, providing for always current configurations, and persistent configurations managed in git.

The approach can be used to deploy secrets as well as arbitrary configuration values.

# Usage

## Declarative Specification

For example, when having a configuration file `/config/example.conf` in a docker image with the following content:

```
user = admin
pwd  = 
```

then running the container, e.g., by

```
docker run \
    -e ENV_PASSWORD=bLupdLr4R2HY \
    -e DCKR_SCRTS_DEPLOY='{"config": "/config/example.conf", "assign": {"pwd": "ENV_PASSWORD"}}' \
    image
```

results in the following changed configuration file `/config/example.conf` taking effect in the container:

```
user = admin
pwd  = bLupdLr4R2HY
```

Basically, this change is defined via the environment variable `DCKR_SCRTS_DEPLOY`. It contains the deployment descriptor in JSON format which defines
the following: first, it identifies the configuration file via parameter `config`, and second it instructs to replace the value of the variable `pwd` by 
the current value of the environment variable `ENV_PASSWORD` via parameter `assign`. Please note that JSON needs double quotes.
You can pass environment variables to the container in a number of ways. For example 
along `docker run` as above, in the respective `docker-compose.yaml` file, or with secrets managers of your choice such as doppler.

Additionaly you need to execute the python file `run.py` when starting the container, which will modify the configuration file. 
This can again be done in a number of ways, e.g., via the `Dockerfile` at build time

```
RUN git clone https://gitlab.com/kyriatide/docker-secrets-deploy.git
ENTRYPOINT ["python3", "/docker-secrets-deploy/run.py"]
CMD ["your-command", "and-options"]
```

or at runtime via `docker run --entrypoint python3 /docker-secrets-deploy/run.py image your-command and-options`.

See the folder `/example` for a complete example.

## Always Current Configurations

Values are deployed into configurations by a two-step process. 
First, a transient template is generated from the configuration specified in the deployment descriptor,
which is called *templatization*.
And second, a new configuration is created by deploying secrets and 
values into the template, which is called *instantiation*.

Thereby, if a new version of a software package was installed when rebuidling a docker image (newer compared to earlier images) 
that updated its configuration file with, e.g., additional variables, the configuration created 
would always be current, i.e., also comprise the newly added variables, because templatization and instantiation 
use the current version of the configuration.

This is different from manually creating a template from an initial package version's configuration at the time of
developing the docker image (at development time), and using this template as the basis for the package's configuration 
at the container's runtime. A configuration created based on that template will always be one of that initial version.

Whether this feature is beneficial for you in your situation may depend.
For always current images where you favor security and configuration management 
simplicity over stability this might be particularly handy.

## Persistent Configurations Managed in Git

Sometimes configurations need to be persistent across containers, and may evolve along image and software upgrades.
This is usually solved by persisting the configuration on docker volumes, e.g., on local disk via 
`docker run -v ./config/example.conf:/config/example.conf:rw image`.

You usually do not want to add these configuration files to your git repository as they contain secrets. 
On the other hand you do not want to use a static config file with empty secrets/values as in the example above, 
because you want the configuration to evolve along image and software upgrades (and not to 
overwrite it with every deployment into the same static config file).

To solve this situation you can persist the *template file* during the secrets deployment process. The
template file in the example would be named `example.conf.tmpl`, and can be added to git, while you would exclude
the actual configuration file via `.gitignore`. 
In the example the template file would have the following content.

```
username = admin
password = {{.ENV_PASSWORD}}
```

Persisting the template file is specified by the parameter `persist` in the deployment descriptor (which is `false` by
default), e.g., as follows:

```
docker run -e ENV_PASSWORD=pass123 \
           -e DCKR_SCRTS_DEPLOY='{"config": "/config/example.conf", "assign": {"pwd": "ENV_PASSWORD"}, \
                                  "persist": true}' image
```

Now every time the container is run, the template file is refreshed based on the found actual configuration file, and
actual environment values are deployed into the configuration file. Thereby the configuration can evolve along
image and software upgrades, while the template file that follows these changes can be managed in git as it doesn't
contain any secrets. 

## The Conventional Way: Working with Templates

You can also work with static manually maintained template files instead of templatization from configuration files,
if you prefer. The template file syntax is already shown in the example above.

Please take into account that you need name your template file like the configuration file, 
with the suffix `.tmpl` as, e.g., in `example.conf.tmpl`. 

Regarding the deployment descriptor,
* note that parameter `config` must always reference the configuration file (and not the template file!), e.g., `example.conf`.
* you need to set `templatize` to `false`, and `assign` is not required, since no values will be assigned to variables, 
but template keyword will be replaced with values.

The rest stays the same, however, you lose the benefits of always current configurations and persistent configurations
as described above. 

# Reference

## Deployment Descriptor Attributes

A deployment descriptor can comprise the following attributes for any configuration type:

* `config` (mandatory, type `string`): Identifies the configuration, and used as base to identify the template (if stored or persisted).
* `templatize` (default: `true`):
Generate a template from the current configuration if available, and then use the 
template to create a new configuration by deploying secrets/values into the template. If `False` the templatization
step is skipped and a template which must be available is used right away.
* `assign` (optional, type `dictionary`): Defines which variables are to be assigned which values. It configures the templatization step,
so if there is no templatization, this attribute must be empty.
* `persist` (default: `false`): Whether to persist the generated template, or to use it only during deployment.

For ini configuration files:
* `assignment_op` (default: `=`): Defines the operator used in the config file to assign values to variables.
* `assignment_shell_style` (default: `false`): Forces assignment of values to variables to follow POSIX shell style syntax, i.e., without whitespace in between the variable name, the assignment operator, and the values, as e.g. in `VARIABLE="value"`. Otherwise, the whitespace contained in the original configuration file is preserved. 
* `allow_multi_occurrence` (default: `false`): Check every variable occured only once in the configuration. Alleged multiple occurrences usually indicate an error, e.g., caused by a variable name that is not unique.

# Extensibility

The created underlying framework is open for extensions, subject to future releases. The module's documentation 
describes the framework concepts and extension points for developers.
