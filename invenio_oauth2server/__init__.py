# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module that implements OAuth 2 server.
Invenio-OAuth2Server
====================

Features
--------
- Implements the OAuth 2.0 authentication protocol.
    - Provides REST API to provide access tokens.
    - Provides decorators that can be used to restrict access to resources.
- Handles authentication using JSON Web Tokens.

Overview
--------
Understanding API Authentication in Invenio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There are 2 ways to authenticate users in an Invenio application:

1. One way is to use a session based or
   `JSON Web Token <https://jwt.io/introduction/>`_
   authentication provided by
   `Invenio-Accounts <https://invenio-accounts.readthedocs.io/en/latest/>`_.

   The traditional Session authentication functionality is mainly
   powered by `Flask-Login <https://flask-login.readthedocs.io/en/latest/>`_
   and passes the user id with the session cookie, so that the users can be
   retrieved and their access permissions can be verified. The JWT
   authentication procedure is different as it makes use of the
   `Authorization` header using the `Bearer` schema, and in this way allows
   to omit the use of cookies. The aforementioned ways of
   authenication are used typically when the user logs in via a browser.

2. A second way would be to use an access token.

   An access token can substitute the user credentials and can also be
   provided to third parties, enabling delegation of rights. In turn,
   there can be different levels of access granted to the third party,
   which are defined by the scopes of the token. Finally, there can be
   differences in the type of token regarding the nature of the
   requesting client. The different scenarios are explained in more
   detail further down.

Obtaining a session and JWT token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To obtain a session:

1. the user logs in by providing his login credentials
2. Invenio-Accounts adds the newly created session to the DB

After this point we can add a CSRF token to not be prone to CSRF attacks.

3. For the CSRF token we can use the JWT as it contains user information and
   it fulfills the key properties of a CSRF token.

By default, the JWT is embedded in the DOM tree using the Jinja context
processor ``{{jwt()}}`` or ``{{jwt_token()}}`` from a template.
By passing the JWT with each request, the user state is never saved in
server memory making this a stateless authentication mechanism. Then the
server just looks for and validates the JWT in the ``Authorization``
header, to allow access to the protected resources.

Obtaining an access token
~~~~~~~~~~~~~~~~~~~~~~~~~
In the case where the client request an access token is the resource owner,
the token will allow all permissions the user would have by providing his
username and password credentials. For example to use a personal access token
to send REST API requests, the procedure is the following:

1. First the user logs in and navigates to his profile page
2. Clicks on ``Create New Personal Token``
3. Stores the generated string in a variable ``$ACCESS_TOKEN``
4. Now requests can be made to protected resources by passing
   it as a parameter, e.g.

.. code-block:: console

    curl -XPOST -d '{some_record_data}' $HOST:5000/records/\?access_token=$ACCESS_TOKEN

In the case where the client is a third party, a web application for example
requesting access to an onwer's protected resources, the procedure is
different. Let's see the case where a user goes to ``example.com`` and
chooses to log in via Invenio. The setup to enable this is as follows:

1. First, the application has to be registered as an authorized application
2. This can be done by the settings page, as it was for the personal access
   tokens, but now clicking on ``New Application``
3. After filling out the form and setting a ``Redirect URL``, a ``Client ID``
   and ``Client Secret`` are generated
4. These have to be set in the ``example.com`` application, in order to be
   able to make requests

Now a user can navigate to ``example.com`` and can select to log in via
Invenio. The procedure will be along the following lines:

5. A request is sent to the ``/authorize`` endpoints in Invenio from
   ``example.com`` with the ``Client ID`` and ``Client Secret`` passed
   as parameters
6. The user is redirected to an Invenio page where he is asked to log in
7. After logging in, a form shows what type of permissions the ``example.com``
   is requesting, and the user can decide to authorize it
8. Invenio redirects back to the ``Redirect URL`` set for this application,
   and returns an authorization code with a limited lifespan
9. The authorization can be used to obtain an access token by querying the
   ``/token`` endpoint in Invenio
10. ``example.com`` can now send requests to Invenio using this access token to
    access resources available to the user

Oauth2 flows
------------
There are different Oauth2 flows you should use depending mostly on the type of
your ``Client`` but also in other parameters such as the level of trust of the
``Client``. By different flows we mean that Oauth2 provides different grant
types that you can use. ``Grant types`` are different ways of retrieving an
``access token`` that eventually will lead you to access a protected resource.
Before analyzing the different Oauth2 flows let's see some Oauth2 terminology:

-   `Resource owner`: the entity that has the
    ownership of a protected resource. Can be
    an the application itself or an end user.
-   `Client`: an application that requests
    access to a protected resource on behalf of the `resource
    owner`.
-   `Resource server`: the server in which
    the protected resource is stored. This is the API you want
    to have access.
-   `Authorization server`: this is the
    server that authenticates the `resource owner` and issues an
    `access token` to the `Client` after getting proper
    authorization. In our case this is the `oauth2server`
    package.
-   `User Agent`: the agent used by the
    Resource Owner to interact with the `Client`, for example a
    browser or a native application.

The crucial thing to decide which Oauth2 grant type is most
suitable for you to use, as we said, is the type of your
`Client`. Having in mind that we define the below 4 cases.


Client is the resource owner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is the case that the application that requests access to a
protected resource is also the owner of this resource. In that
case the application holds the `client id` and the `client
secret` and uses them to authenticate itself through the
`authentication server` and retrieve the access token. Such an
example could be a service running on the client server and
trying to get access to a resource on the same server. A typical
flow diagram is the following:

[TODO: diagram]

If this case is the one that suits your needs then you should
use the `Client Credentials grant`.

Client is an application running on a web server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In that case you should use the ``Authorization Code grant``. In
this flow the Client requests an access token from the
authorization server in order to access the protected
resource. The Client gets an access token after first the
resource owner is authorized.

[TODO: diagram?]

Client is trusted with user Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In that case probably you should use the ``Resource Owner
Password Credentials Grant``. In this flow the end user trusts
the ``Client`` with his/her credentials in order to be used by the
client to authenticate him/her through the authorization server.
This a grant type that is by default disabled in
Invenio-OAuth2Server and should be used only if there is no
possibily to use another redirect-based flow.


Client is a Single Page Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If your application is a single page application then you should use the
``Implicit grant``. In this grant type instead of getting
first an authorization code in order to ask for an access token
you directly ask for the token. In the plus side this method is
faster as there is no need for round trip to get an access
token. However, there is a security risk as the access token is exposed to
the `user agent`(e.g user's browser). Also you should consider that the
`Implicit grant` doesn't return refresh tokens.

Invenio implementation of flows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Let's have a look on how Invenio-OAuth2Server implements this flows.

- Authorization Code Grant -> examples in oauthclient, graph with endpoint
  interaction /authorize

.. code-block:: console

    $ http://<OAuth2Server>/oauth/authorize?response_type=code&
                                                client_id=j9TeGI9QpIzJeWdhewqUmx2UUHkvcSdGBnLtkICT&
                                                redirect_uri=http://<OAuth2Client>/authorized&
                                                scope=test:scope&
                                                state=oubyFlr1aOO71SEOtfEeuCntdNOtKB

- Client credentials grant /token endpoint
- Implicit grant:  /authorize
    - TODO: check life time of tokens, and confidential vs public clients. Understand security implications for SPAs (e.g implicit tokens must not be refreshable).
- Refreshing an access token

(- Security considerations: Cross-Origin Resource Sharing (CORS) considerations
    with session authentication this becomes a liability, cookie will be passed
    XSS attacks are possible. -> don't allow any origin access to the API)

Usage
=====

Protecting your REST API with authentication
--------------------------------------------

If you want to have your REST API endpoints protected using OAuth you
should register their blueprint inside the API app
(InvenioOAuth2ServerREST) which by default includes a ``before_request`` hook.
This hook will, if there is an OAuth token, verify it and set the current user
accordingly. It is important to highlight that this configuration allows
either authenticated clients or anonymous clients.

In case you need to allow access to a resource only for authenticated clients,
you should use the `require_api_auth
<api.html#invenio_oauth2server.decorators.require_api_auth>`__
decorator which requires OAuth2 login:

.. code-block:: python

    @app.route('/api/resource', methods=['GET'])
    @require_api_auth()
    def index():
        return 'Protected resource'

However, protecting your resources only with authentication is not
recommended. Instead, you should add an extra layer using always
`scopes <api.html#invenio_oauth2server.models.Scope>`__. This is because,
basically, any client that owns a token has control over every user resource.
Therefore, using scopes gives a fine-grain control. Here an example using
the default ``email_scope``:

.. code-block:: python

    from invenio_oauth2server.scopes import email_scope

    @app.route('/api/email', methods=['GET'])
    @require_api_auth()
    @require_oauth_scopes(email_scope.id_)
    def index():
        return 'admin@inveniosoftware.org'

Delegating rights via scopes
----------------------------

As mentioned before, the recommended way to protect your endpoints is to use
fine-grain control with scopes. Invenio-OAuth2Server offers the possibility to
create new ones:

.. code-block:: python

    from invenio_oauth2server.models import Scope

    homepage_read = Scope('homepage:read',
                          help_text='Access to the homepage',
                          group='test')

Next, you should add them to ``setup.py`` entrypoints so they get initialized
at start up:

.. code-block:: python

    setup(
        ...
        entry_points={
            'invenio_oauth2server.scopes': [
                'homepage_read = path.to.scopes.file:homepage_read',
            ]
        }
        ...
    )

And then, they can be used in your application:

.. code-block:: python

    from path.to.scopes.file import homepage_read

    @app.route('/', methods=['GET'])
    @require_api_auth()
    @require_oauth_scopes(homepage_read.id_)
    def index():
        return 'Front page content.'

So, finally, with this example, we would allow any authenticated client with
rights to use the ``homepage_scope`` to read the homepage but, prevent from
reading the email if they do not have rights for using the ``email_scope``.

To test this features you can build your own application or use the provided
:doc:`example app </examplesapp>` as boilerplate.

Access control
--------------

It is important to remember that the usage of authentication and scopes is not
enough in most of the cases so access control need to be configured as well.
For more information about access control in Invenio you can visit
`Invenio-Access
<http://invenio-access.readthedocs.io/en/latest/>`__ documentation.


"""

from __future__ import absolute_import, print_function

from .ext import InvenioOAuth2Server, InvenioOAuth2ServerREST
from .proxies import current_oauth2server
from .version import __version__
from .decorators import require_api_auth, require_oauth_scopes

__all__ = (
    '__version__',
    'InvenioOAuth2Server',
    'InvenioOAuth2ServerREST',
    'require_api_auth',
    'require_oauth_scopes',
    'current_oauth2server',
)
