# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bovine_store',
 'bovine_store.actor',
 'bovine_store.fedi',
 'bovine_store.store',
 'bovine_store.utils']

package_data = \
{'': ['*'], 'bovine_store': ['templates/*']}

install_requires = \
['bovine>=0.2.1,<0.3.0',
 'quart>=0.18.3,<0.19.0',
 'tortoise-orm[asyncpg]>=0.19.3,<0.20.0']

setup_kwargs = {
    'name': 'bovine-store',
    'version': '0.2.2',
    'description': 'Store for ActivityPub activities, actors and objects',
    'long_description': '# bovine_store\n\n`bovine_store` is meant to be the module handling storing of\nlocal ActivityPub objects and caching of remote ActivityPub\nobjects.\n\n## Usage\n\nbovine_store assumes that a database connection is initialized using [tortoise-orm](https://tortoise.github.io/). See `examples/basic_app.py` for how to do this in the context of a quart app.\n\n## TODO\n\n- [ ] When properties of actor are updated, send an update Activity\n- [ ] Generally rework the actor properties mechanism. It is currently not possible to emulate say Mastodon featured collection with it.\n- [ ] bovine_store.models.BovineActorKeyPair needs renamings; and work, e.g. a future identity column should have a uniqueness constraint.\n- [ ] Generally the code quality is not as high as it should be.\n\n## Design discussion\n\nSome goals and design decisions:\n\n- Objects with an id are stored separately and can be looked up via this id. This is done by json-ld magic.\n- Collections are not stored. Instead for local items, the information that the item belongs to a collection is stored. `bovine_store.store.collection` contains the coroutines necessary to build the collection from this information. All collections are assumed to ActivityStreams 2 `OrderedCollection` and ordered by the database id.\n- Every object is currently assigned an `owner`. The idea was that an activity is owner by its actor. This can then be propagated to the subobjects, e.g. the object, attachments, and so on. Unfortunately, this is too naive:\n  - Some implementations include remote objects, e.g. the object being liked in a Like Activity.\n  - Mastodon includes its custom emojis. These have an id and should probably belong to the server.\n- There are three kinds of visibility.\n  - An object is always visible to its owner\n  - Public Objects are assigned `VisibilityType.PUBLIC`. These can viewed by all users providing valid authentication.\n  - Furthemore, by adding actors to the `VisibileTo` list of an object. This can be made visible to the corresponding actors.\n- An item is visible to be inside a collection if and only if said item is visible. This should probably be augmented by visible to the owner of the collection.\n- `bovine_store.blueprint` contains a quart blueprint with the basic retrievel mechanism for the stored objects.\n- `bovine_store.collection` contains the helper routine for collection responses.\n\n## Examples\n\nA demonstration webserver can be seen using\n\n```bash\npoetry run python examples/basic_app.py\n```\n\nNote this is a very basic example. Instructions what the example does are\nprinted to the command line after start.\n\nNote: This example creates two files `db.sqlite3`, which contains the\ndatabase and `context_cache.sqlite`, which contains the cache of json-ld\ncontexts.\n',
    'author': 'Helge',
    'author_email': 'helge.krueger@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://codeberg.org/bovine/bovine',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
