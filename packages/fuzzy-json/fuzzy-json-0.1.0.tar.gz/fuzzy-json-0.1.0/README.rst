fuzzy-json-py
=============

Fuzzy JSON parser, python binding

Usage
-----

.. code:: python

   import fuzzy_json

   data = fuzzy_json.loads(
       """
   The data is
   {
       'x': nil,
       'a dog': [], // trailing comma is ok
   }.
   """
   )
   print(data)
