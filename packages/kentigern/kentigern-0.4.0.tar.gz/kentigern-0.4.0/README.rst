=========
Kentigern
=========

This Sphinx_ theme_ integrates the Bootstrap_ CSS and JavaScript framework with various layout options, hierarchical menu navigation, and mobile-friendly responsive design.
It is designed to be configurable and extensible.
The `kentigern` theme is forked from the `Sphinx Bootstrap Theme`_.

Installation
============
Installation from PyPI_ is fairly straightforward:

1. Install the package::

      $ pip install kentigern

2. Edit the "conf.py" configuration file to point to the bootstrap theme::

      # At the top.
      import kentigern

      # ...

      # Activate the theme.
      html_theme = 'kentigern'
      html_theme_path = kentigern.get_html_theme_path()


Licenses
========

Kentigern is licensed under the MIT_ license.
Sphinx Bootstrap Theme is licensed under the MIT_ license.

`Bootstrap v3.1.0+`_ is licensed under the MIT license.

.. _`Sphinx Bootstrap Theme`: https://github.com/ryan-roemer/sphinx-bootstrap-theme/
.. _`MIT`: https://github.com/ryan-roemer/sphinx-bootstrap-theme/blob/master/LICENSE.txt
.. _`Bootstrap v2`: https://github.com/twbs/bootstrap/blob/v2.3.2/LICENSE
.. _`Bootstrap v3.1.0+`: https://github.com/twbs/bootstrap/blob/master/LICENSE

