Software Heritage GraphQL API
=============================

This repository holds the development of Software Heritage GraphQL API.
The service is available at https://archive.softwareheritage.org/graphql/
A staging version of this service is available at https://graphql.staging.swh.network

Running locally
---------------

Refer to https://docs.softwareheritage.org/devel/getting-started.html#getting-started for
running software heritage services locally.

If you wish to run SWH-GraphQL independently, and have access to SWH storage services,
following make targets can be used.

* make run-dev: Use the config file at ``swh/graphql/config/dev.yml`` and start the service in
  auto-reload mode using uvicorn

* make run-dev-stable: Use the config file at ``swh/graphql/config/dev.yml`` and start the
  service using uvicorn

* make run-dev-docker: Run the service inside a docker container and Use the config file
  at ``swh/graphql/config/dev.yml``

* make run-wsgi-docker: Run the service inside a docker container and Use the config file
  at ``swh/graphql/config/staging.yml``

* visit http://localhost:8000 to use the query explorer

Running a query
---------------

The easiest way to run a query is using the query explorer.
Please provide an SWH API token if you wish to run bigger queries.

Using curl
----------

.. code-block:: console

   curl -i -H 'Content-Type: application/json' -H "Authorization: bearer your-api-token" -X POST -d '{"query": "query {origins(first: 2) {nodes {url}}}"}' http://127.0.0.1:8000


Using Python requests
---------------------

.. code-block:: python

   import requests

   url = "http://127.0.0.1:8000"
   query = """
   {
     origins(first: 2) {
       pageInfo {
         hasNextPage
           endCursor
       }
       edges {
         node {
           url
         }
       }
     }
   }
   """
   json = {"query" : query}
   api_token = "your-api-token"
   headers = {'Authorization': 'Bearer %s' % api_token}

   r = requests.post(url=url, json=json, headers=headers)
   print (r.json())


Pagination
----------

The server can return either a Node object (eg: Origin type) or a Connection object.
All the connection objects can be paginated using cursors.

All the entrypoints that return a Connection (eg: origins entrypoint that
returns an OriginConnection type) will accept the following arguments.

* ``first``: An integer. The number of objects to return a.k.a the page size.
  This is a mandatory argument for most of the connections.
  The maximum value of ``first`` is limited to 1000.
  There are some entrypoints where the ``first`` argument is not mandatory.
  (eg: statuses inside a Visit type) Default value of ``first`` will be set to 50 in those cases.

* ``after``: A string. The cursor to be used for pagination.
  If no cursor is given, the server will return ``first`` number of objects from the beginning.

Every connection type will have the following fields.

* ``edges``: This will be a list of objects with the following fields.

  * ``node``: The requested SWH object.

  * ``cursor``: Cursor to the specific object (item cursor). (This field is not available in all connections
    for the time being). This cursor can be used to paginate starting from this particular object.

* ``nodes``: A list of SWH objects. This is a shortcut to access the SWH objects without going through
  the ``edges`` layer, but it not possible to get an item cursor using nodes.

* ``pageInfo``: Data to be used for querying subsequent pages. Contains the following fields.

  * ``endCursor``: Cursor to request the next page.

  * ``hasNextPage`` A boolean value.

* ``totalCount``: Total number of objects available in the connection after applying the given filters.
  This is not available for many connections for the time being.

Example for pagination using edges
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get the contents of a directory

.. code-block::

  query getDirectoryContent {
    directory(swhid: "swh:1:dir:b0b6050efa0634ecded8508a7ab9c6774ca69ac8") {
      entries(first: 5, after: "NQ==") {
        totalCount
        edges {
          node {
            name {
              text
            }
          }
          cursor
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
    }
  }

Example for pagination using nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

  query getDirectoryContent {
    directory(swhid: "swh:1:dir:b0b6050efa0634ecded8508a7ab9c6774ca69ac8") {
      entries(first: 2, after: "NTA=") {
        totalCount
        nodes {
          name {
            text
          }
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
    }
  }
