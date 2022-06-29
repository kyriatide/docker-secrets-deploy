
# Test Suites

End-to-end testing refers to comprising the following steps
* loader loads deployment descriptors;
* configurations are templatized;
* read secret/config values from Secrets Providers;
* templates are instantiated.

## `deploy`

End-to-end test cases related to deployment of secrets and variable values.

Structured by features as tests are end-to-end.

Uses default `EnvironLoader`, `EnvironProvider`,  `IniFileConfigHdl`, and `FileTemplateHdl`. 


## `loader`

Test cases for testing non-default loader types, and erroneous default loader cases.
Ends with retrieved `DeploymentDescriptor`s.

## `dscrpt`

Test cases for testing erroneous deployment descriptors along the various configuration types. Correctly formed deployment descriptors are tested along the `deploy` test suite.

## `config`

Test cases for testing non-default configuration handlers.

## `provider`

Test cases for testing Secrets Providers by provider type.

## `template`

Test cases for testing non-default template handlers.
