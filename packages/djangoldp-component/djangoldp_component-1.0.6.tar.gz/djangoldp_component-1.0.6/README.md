# DjangoLDP Component package

## Step by step quickstart

1. Installation

- `git clone git@git.startinblox.com:applications/ontochain/component-registry.git /path/to/djangoldp-component`

2. Developpement environnement

In order to test and developp your package, you need to put the package src directory at the same level of a working django ldp app. By exemple, you can clone the sib app data server
`git clone git@git.startinblox.com:applications/ontochain/component-registry.git server /path/to/app`

- The classical way :
  `ln -s /path/to/djangoldp-component/djangoldp_component /path/to/app/djangoldp_component`

- The docker way : in the _volumes_ section, add a line in docker-compose.override.yml. Example

```yaml
volumes:
  - ./:/app
  - /path/to/djangoldp-component/djangoldp_component:/app/djangoldp_component
```

Add your package in settings.py of the app. Now, you can test if your package is imported propefully by doing a
`python manage.py shell` then
from djangoldp_component.models import Component

If, no error, it's working.
