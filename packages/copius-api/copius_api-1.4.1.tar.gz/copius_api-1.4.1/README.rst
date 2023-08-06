|DOI| |CircleCI|

copius_api
==========

This is a Python-api to the transcription and orthography toolset at
https://copius.eu/ortho.php:

“This toolset is a loose conglomeration of applications aiming to help
you handle various character encodings, orthographies, transcriptions
and transliterations you might encounter when working with Uralic
languages and other languages of Europe and Northern Asia that use
variants of the Latin or Cyrillic alphabet.” (Copyright © 2021 COPIUS)

How to install:

::

   $ pip install copius_api

How to use:

::

   >>> from copius_api import api
   >>> api.transcribe("ke̮")
   "kɘ"

::

   >>> from copius_api import api
   >>> api.transcribe("lol","kom","lc")
   "лол"

::

   >>> from copius_api import api
   >>> api.transcribe("kiki","mns","9c")
   "кики"

::

   >>> from copius_api import api
   >>> api.transcribe("буба","mns","c9")
   "buba"

To see the language abbreviations:

::

   >>> from copius_api import api
   >>> api.lang_dict
   {'Mari (Hill Mari)': 'mhr', 'Udmurt': 'udm', 'Komi': 'kom', 'Erzya': 'myv', 'Moksha': 'mdf', 'Mansi': 'mns', 'Tatar': 'tat', 'Bashkir': 'bak', 'Chuvash': 'chv', 'Russian': 'rus'}

To see the script abbrevations:

::

   >>> from copius_api import api
   >>> api.orth_dict
   {'Cyrillic to Cyrillic': 'cc', 'Cyrillic to Latin': 'cl', 'Cyrillic to IPA': 'ci', 'Cyrillic to ISO9': 'c9', 'Latin to Cyrillic': 'lc', 'Latin to Latin': 'll', 'Latin to IPA': 'li', 'Latin to ISO9': 'l9', 'IPA to Cyrillic': 'ic', 'IPA to Latin': 'il', 'IPA to ISO9': 'i9', 'ISO9 to Cyrillic': '9c', 'ISO9 to Latin': '9l', 'ISO9 to IPA': '9i', '<1917 to Cyrillic': '3c', '<1917 to Latin': '3l', '<1917 to IPA': '3i', '<1917 to ISO9': '39'}

.. |DOI| image:: https://zenodo.org/badge/428920599.svg
   :target: https://zenodo.org/badge/latestdoi/428920599
.. |CircleCI| image:: https://circleci.com/gh/martino-vic/copius_api/tree/master.svg?style=svg
   :target: https://circleci.com/gh/martino-vic/copius_api/tree/master
