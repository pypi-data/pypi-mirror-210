.. title:: API Reference
.. meta::
  :description: API Reference for JSON-RPC Python framework
  :keywords: python, asgi, jsonrpc, json, rpc, api, reference, interface, development

API Reference
=============

.. important::
  This part of the documentation covers only public classes, their methods and attributes.
  Private objects are only needed for internal use and accessing of them by hand is **discouraged**.

.. module:: jsonrpc

ASGI Entry Point
----------------

.. autoclass:: ASGIHandler
  :members:

Routing user-defined functions
------------------------------

.. autoclass:: AsyncDispatcher
  :members:

Error handling
--------------

.. autoclass:: ErrorEnum
  :members:

.. autoexception:: Error
  :members:

Requests & Responses
--------------------

.. autoclass:: Request
  :members:

.. autoclass:: BatchRequest
  :members:

.. autoclass:: Response
  :members:

.. autoclass:: BatchResponse
  :members:

Data Serialization
------------------

.. autoclass:: JSONSerializer
  :members:
