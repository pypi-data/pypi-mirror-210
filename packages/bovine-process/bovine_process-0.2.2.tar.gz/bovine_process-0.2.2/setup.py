# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bovine_process',
 'bovine_process.incoming',
 'bovine_process.outgoing',
 'bovine_process.utils']

package_data = \
{'': ['*']}

install_requires = \
['bovine-store>=0.2.1,<0.3.0', 'tortoise-orm[asyncpg]>=0.19.3,<0.20.0']

setup_kwargs = {
    'name': 'bovine-process',
    'version': '0.2.2',
    'description': 'Processing of Side Effects of ActivityPub Activities for an ActivityPub Server',
    'long_description': "# bovine_process\n\n`bovine_process` consists of the side effect logic of Activity objects. This means it contains the code, the logic that for an incoming object, one executes:\n\n- Store object in bovine_store\n- Add reference to inbox\n- Perform side effects\n- Enque object for bovine_pubsub\n\nAnd a similar list of effects for outgoing objects, i.e\n\n- Store object in bovine_store\n- Add reference to outbox\n- Perform side effects\n- Send objects to follower's inbox\n- Enque object for bovine_pubsub\n\nThe behavior defined in this package corresponds to [6. Client to Server Interactions](https://www.w3.org/TR/activitypub/#client-to-server-interactions) and [7. Server to Server Interactions](https://www.w3.org/TR/activitypub/#server-to-server-interactions) of the ActivityPub specification. However, only a small subset of side effects is implemented.\n\n## Implemented Side Effects\n\n- Create, Update, Delete. Deletes are handled by replacing the object with a Tombstone. Various checks are performed to ensure only appropriate Updates happen.\n- [ ] Specify Update checks\n- Follow and Accept\n  - Outgoing Accept of Follow adds to followers\n  - Incoming Accept of Follows adds to following\n- [ ] Implement other side effects, in particular Like, Announce, and inReplyTo\n- [ ] Authority checks.\n\nThat's it. Currently, no collections for replies and likes are kept in bovine_store, so implementing these side effects cannot happen yet:\n\n- [ ] Announce -> add to share collection\n- [ ] Like -> add to likes collection\n- [ ] Create with inReplyTo -> add to replies collection\n\n## Tests\n\nThe folder `tests/data` contains test cases what side effects happen in the database for certain cases.\n",
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
