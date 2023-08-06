# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fastapi_authlib',
 'fastapi_authlib.alembic',
 'fastapi_authlib.alembic.versions',
 'fastapi_authlib.config',
 'fastapi_authlib.messages',
 'fastapi_authlib.repository',
 'fastapi_authlib.rest_api',
 'fastapi_authlib.rest_api.handler',
 'fastapi_authlib.rest_api.routers',
 'fastapi_authlib.schemas',
 'fastapi_authlib.services',
 'fastapi_authlib.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiomysql>=0.1.1,<0.2.0',
 'alembic>=1.10.3,<2.0.0',
 'authlib>=1.2.0,<2.0.0',
 'dynaconf>=3.1.12,<4.0.0',
 'fastapi-sa>=0.1.0,<0.2.0',
 'fastapi>=0.95.0,<0.96.0',
 'httpx>=0.24.0,<0.25.0',
 'inflection>=0.5.1,<0.6.0',
 'itsdangerous>=2.1.2,<3.0.0',
 'sqlalchemy==1.4.46',
 'uvicorn>=0.21.1,<0.22.0']

setup_kwargs = {
    'name': 'fastapi-authlib',
    'version': '0.0.1',
    'description': 'A fastapi authlib authentication library',
    'long_description': '# fastapi-oidc-support\n\nfastapi-oidc-support provides easy integration between FastAPI and openid connection in your application.\nProvides the initialization and dependencies of oidc, aiming to unify authentication management and\nreduce the difficulty of use.\n\n## Installing\n\ninstall and update using pip:\n\n```shell\npip install fastapi-authlib\n```\n\n## Examples\n\n### Create settings for examples, `settings.py`\n\n```python\nconfig = {\n    \'database\': \'sqlite+aiosqlite:////tmp/oidc_demo.db\',\n    \'oauth_client_id\': \'client_id\',\n    \'oauth_client_secret\': \'client_secret\',\n    \'oauth_conf_url\': \'conf_url\',\n    \'session_secret\': \'secret_key\',\n    \'router_prefix\': \'\',\n}\n```\n\nsettings.py is a simple configuration file of the use case, which mainly provides the database link,\nthe necessary parameters used by oidc, the session authentication key and the routing prefix.\n\nPlease use your authentication server configuration to populate the parameter value prefixed with oauth.\nOther parameters can be modified according to the actual situation.\n\n### Create api route, `api_router.py`\n\n```python\nfrom fastapi import APIRouter\nfrom starlette.requests import Request\n\nrouter = APIRouter()\n\n\n@router.get(\'/index\')\nasync def index(\n        *,\n        request: Request,\n):\n    """\n    User\n    """\n    user_info = request.state.user\n    return {\'name\': user_info.get(\'user_name\')}\n```\n\nFor authenticated api, you can use `request.state.user` to get the current user.\n\n### Create oidc demo entry, `main.py`\n\n```python\n"""main"""\nimport uvicorn\nfrom fastapi import Depends, FastAPI\nfrom fastapi_sa.database import db\nfrom fastapi_sa.middleware import DBSessionMiddleware\n\nfrom fastapi_authlib.oidc import OIDCClient\nfrom fastapi_authlib.utils.check_user_depend import check_auth_session\nfrom api_router import index\nfrom .settings import config\n\n\nclass OIDCDemo:\n    """OIDCDemo"""\n\n    def __init__(self, settings: dict):\n        self.settings = settings\n        self.router_prefix = self.settings.get(\'router_prefix\')\n\n    def run(self):\n        """Run"""\n        # Early environment initialization\n        app = FastAPI(title=\'FastAPIOIDCSupportDemo\', version=\'0.1.0\')\n        db.init(self.settings.get(\'database\'))\n\n        # Oidc environment initialization\n        client = OIDCClient(\n            app=app,\n            **config\n        )\n        # If you only init app, you should use init_app() instead\n        client.init_oidc()\n\n        # Customize the environment initialization\n        # add dependencies to the interface that needs to be authenticated\n        app.include_router(index.router, tags=[\'index\'], prefix=config.get(\'router_prefix\'),\n                           dependencies=[Depends(check_auth_session)])\n        app.add_middleware(DBSessionMiddleware)\n        return app\n\n\nif __name__ == \'__main__\':\n    client_app = OIDCDemo(config).run()\n    uvicorn.run(client_app, host="0.0.0.0", port=8001)\n\n```\n\n### Use Step\n\n- Create app and init db\n- Init the environment of oidc, If you don\'t want to do data migration, you should use init_app method.\n  Usually database migration and oidc initialization are performed together\n- Register routing and other middleware, the DBSessionMiddleware is required\n- Start a fastapi server with uvicorn or other\n\n## Based on\n\n- [FastAPI](https://github.com/tiangolo/fastapi)\n- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy)\n- [Fastapi-sa](https://github.com/whg517/fastapi-sa)\n- [Authlib](https://github.com/lepture/authlib)\n\n## Develop\n\nYou may need to read the [develop document](./docs/development.md) to use SRC Layout in your IDE.\n',
    'author': 'qiang.xie',
    'author_email': 'qiang.xie@zncdata.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
