# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiofauna', 'aiofauna.cli']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'Markdown>=3.4.3,<4.0.0',
 'Pygments>=2.15.1,<3.0.0',
 'aiohttp-devtools>=1.0.post0,<2.0',
 'aiohttp-sse>=2.1.0,<3.0.0',
 'aiohttp>=3.8.4,<4.0.0',
 'aiohttp_cors>=0.7.0,<0.8.0',
 'iso8601>=1.1.0,<2.0.0',
 'pydantic[dotenv]>=1.10.7,<2.0.0']

entry_points = \
{'console_scripts': ['aiofauna = aiofauna.cli:main']}

setup_kwargs = {
    'name': 'aiofauna',
    'version': '0.1.19',
    'description': '',
    'long_description': "---\ntitle: AioFauna\n---\n# AioFauna\n\n🚀 Introducing aiofauna: A full-stack framework built on top of Aiohttp, Pydantic and FaunaDB.\n\n🔥 Inspired by FastAPI focuses on Developer Experience, Productivity and Versatility.\n\n🌟 Features:\n\n✅ Supports Python 3.7+, comes with an opinionated ODM (Object Document Mapper) out of the box for FaunaDB that abstracts out complex FQL expressions into pythonic, fully typed asynchronous methods for all CRUD operations.\n\n✅ Powerful and Scalable: Being built on top of Aiohttp an asyncio based http server/client and FaunaDB an scalable serverless database for modern applications allows for powerful and seamless integrations.\n\n✅ Performant: As a framework built on top of Aiohttp it leverages the power of asyncio and the fastest python `HTTPClient` aiohttp plus the ubiquiness of FaunaDB to achieve high performance.\n\n✅ Automatic Swagger UI generation: Automatic generation of interactive Swagger UI documentation for instant testing of your `Api`.\n\n✅ SSE (Server Sent Events): Built-in support for SSE (Server Sent Events) for real-time streaming of data from FaunaDB to your application.\n\n✅ Websockets: Built-in support for Websockets for real-time bidirectional communication between your application and the resources served by AioFauna `Api`.\n\n✅ Robust data validation: Utilizes the rich features of Pydantic for data validation and serialization.\n\n✅ Auto-provisioning: Automatic management of indexes, unique indexes, and collections with `FaunaModel` ODM.\n\n✅ Full JSON communication: Focus on your data, don't worry about the communication protocol. Your `Api` will receive and return JSON.\n\n✅ Markdown and Html support with live reload: experiment an smooth frontend devserver experience without leaving your backend code with familiar syntax, `render_template` and `markdown_it` functions enable you to render static markdown files and html jinja templates with live reload.\n\n✅ Inspired by fastapi, you will work with almost the same syntax and features like path operations, path parameters, query parameters, request body, status codes, `/docs` automatic interactive API documentation, and decorated view functions and automatic serialization and deserialization of your data.\n\n💡 With aiofauna, you can build fast, scalable, and reliable modern applications, avoiding decision fatigue and focusing on what really matters, your data and your business logic.\n\n📚 Check out the aiofauna library, and start building your next-gen applications today! 🚀\n\n#Python #FaunaDB #Async #Pydantic #aiofauna\n\n⚙️ If you are using a synchronous framework check out [Faudantic](https://github.com/obahamonde/faudantic) for a similar experience with FaunaDB and Pydantic.\n\n📚 [Documentation](https://obahamonde-aiofauna-docs.smartpro.solutions) (Built with aiofauna)\n\n📦 [PyPi](https://pypi.org/project/aiofauna/)\n\n📦 [Demo](https://aiofauna-fwuw7gz7oq-uc.a.run.app/) (Whatsapp clone built with aiofauna)\n\n📦 [Swagger UI](https://aiofauna-fwuw7gz7oq-uc.a.run.app/docs) (Whatsapp clone built with aiofauna)\n\n📦 [GitHub](https://github.com/obahamonde/aiofauna)\n",
    'author': 'Oscar Bahamonde',
    'author_email': 'oscar.bahamonde.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/obahamonde/aiofauna',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
