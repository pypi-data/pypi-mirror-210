# perun.proxygui

Pages used by microservices in [satosacontrib.perun](https://gitlab.ics.muni.cz/perun-proxy-aai/python/satosacontrib-perun).

## Installation

The recommended way to install is via pip:

```
pip3 install perun.proxygui
```

Alternatively, you can clone the repository and run:

```
pip3 install .
```

## Configuration

Copy `perun.proxygui.yaml` from config_templates to `/etc/` (it needs to reside at `/etc/perun.proxygui.yaml`) and adjust to your needs.

The `global_cfg_filepath` option needs to point to the location of the global microservice config from the [satosacontrib.perun](https://gitlab.ics.muni.cz/perun-proxy-aai/python/satosacontrib-perun) module. You also need to set the attribute map config.

At the very least, you need to copy the config templates:

```
cp config_templates/perun.proxygui.yaml /etc/perun.proxygui.yaml
cp ../satosacontrib-perun/satosacontrib/perun/config_templates/attribute_typing.yaml /etc/
cp ../satosacontrib-perun/satosacontrib/perun/config_templates/microservices_global.yaml /etc/
```

Then change the following line in `/etc/perun.proxygui.yaml`:

```
global_cfg_filepath: /etc/microservices_global.yaml
```

And the following line in `/etc/microservices_global.yaml`:

```
attrs_cfg_path: /etc/attribute_typing.yaml
```

## Run

### uWSGI

To run this Flask app with uWSGI, use the callable `perun.proxygui.app:get_app`, e.g.

```
mount = /proxygui=perun.proxygui.app:get_app
```

### local development

```
python3 perun/proxygui/app.py
```

Now the app is available at `http://localhost:5000/` (e.g. `http://localhost:5000/banned-users/`).

## Translations

### Babel

First you need to generate `.pot` file: `pybabel extract -F babel.cfg -o messages.pot .`

Next step is to generate `.po` file: `pybabel init -i messages.pot -d perun/proxygui/gui/translations -D messages -l <language_code>`

- replace <language code> with given language code (eg: fr)

Then you need to, manually or using a tool like [Poedit](https://poedit.net/), write your translations in the generated `.po` file and compile it: `pybabel compile -d perun/proxygui/gui/translations -D messages`

- note that if the `.pot` file is already created and you want to add new language ignore the first step

## API

### Consent

This API handles consents - checks if any consent was given by the user and asks him to give a new one if not. API is connected to GUI where user can choose which attributes are to be consented. This API is strongly based on [CMservice](https://github.com/its-dirg/CMservice). Some of the differences:

- GUI
- usage of MongoDB
- user_id and requester_name are sent from micro_service and are part of the consent stored in the database
- we can define attributes which are ignored (in the config)
