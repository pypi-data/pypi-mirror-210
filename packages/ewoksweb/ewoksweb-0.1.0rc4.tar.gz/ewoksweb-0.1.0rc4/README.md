# ewoksweb

_ewoksweb_ is a frontend to create, visualize and execute
[ewoks](https://ewoks.readthedocs.io/) workflows in the web.

## Demo

https://workflow.gitlab-pages.esrf.fr/ewoks/ewoksweb/

## From source

Required system packages

```bash
apt-get install npm
npm install -g pnpm
```

Start the frontend

```bash
pnpm start
```

Build the package for deployment on pypi

```bash
npx -y browserslist@latest --update-db  # optional
pnpm install
pnpm build
python setup.py sdist
```

## From pypi

Install REST server only (`ewoksserver` is another package)

```bash
pip install ewoksserver
```

Install REST server with frontend (`ewoksserver` has `ewoksweb` as optional
dependency)

```bash
pip install ewoksserver[frontend]
```

or alternatively

```bash
pip install ewoksserver
pip install ewoksweb
```

Start the server that serves the frontend

```bash
ewoks-server
```

or for an installation with the system python

```bash
python3 -m ewoksserver.server
```

## Documentation

https://ewoksweb.readthedocs.io/
