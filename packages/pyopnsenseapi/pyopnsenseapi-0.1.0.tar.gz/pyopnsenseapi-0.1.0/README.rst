==========
pyopnsenseapi
==========
You can see the full rendered docs at: http://pyopnsense.readthedocs.io/en/latest/

A python API client for the OPNsense API. This provides a python interface for
interacting with the OPNsense API.


Installation
============
pyopnsenseapi is available via pypi so all you need to do is run::

   pip install -U pyopnsenseapi

to get the latest pyopnsenseapi release on your system. If you need to use a
development version of pyopnsenseapi you can clone the repo and install it locally
with::

  git clone https://github.com/11harveyj/pyopnsenseapi && pip install -e pyopnsenseapi

which will install pyopnsenseapi in your python environment in editable mode for
development.

.. _usage:

Usage
=====

To use pyopnsenseapi you need a couple pieces of information, the API key and the
API secret. Both can be created/found from the OPNsense web UI by navigating
to: `System->Access->Users` under `API keys`.

More information on this can be found in the OPNsense documentation:
https://docs.opnsense.org/development/how-tos/api.html

Once you have the API key and API secret you can use pyopnsenseapi to interact
with your OPNsense installation. You can do this by passing your credentials
to a client class. For example:

.. code-block:: python

    import pyopnsenseapi as opnsense

    api_key = 'XXXXXX'
    api_secret = 'XXXXXXXXXXXXXXX'
    host = '192.168.1.1'
    use_ssl = True
    verify_cert = False

    client = opnsense.Client(
        api_key, api_secret, host, use_ssl, verify_cert)

    print(client.modules.diagnostics.interface.get_arp())

which will print a dictionary mapping physical devices to their interface label.

This same formula can be used to access each individual API endpoint you need
to access. The basic structure of the library is setup to roughly mirror the
endpoint tree of the OPNsense API. Each client module maps to the base endpoint
and then there is a client class in those modules for the next level up off
that.

You can find more detail on how to use the clients in the API reference
documentation found here:

http://pyopnsenseapi.readthedocs.io/en/latest/api.html
