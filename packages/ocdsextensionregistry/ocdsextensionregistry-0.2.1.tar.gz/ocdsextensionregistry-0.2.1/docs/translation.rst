Translation
===========

Setup
-----

:doc:`Install this package with command-line tools<cli>`, `install the Transifex Client <https://developers.transifex.com/docs/cli>`__, and install ``sphinx-intl``:

.. code-block:: bash

    pip install sphinx-intl

Create new translations
-----------------------

Create a project on Transifex (in this example, our project's identifier is ``ocds-extensions``).

Generate POT files for all versions of all extensions:

.. code-block:: bash

    ocdsextensionregistry generate-pot-files build/locale

Or, generate POT files for only live versions of extensions:

.. code-block:: bash

    ocdsextensionregistry generate-pot-files --no-frozen build/locale

Or, generate POT files for the versions of extensions you want to translate, for example:

.. code-block:: bash

    ocdsextensionregistry generate-pot-files build/locale lots bids==v1.1.4

Remove any existing ``.tx/config`` file:

.. code-block:: bash

    rm -f .tx/config

Create a new ``.tx/config`` file:

.. code-block:: bash

    sphinx-intl create-txconfig

Update the ``.tx/config`` file based on the POT files (replace ``open-contracting-partnership-1`` with your organization and ``ocds-extensions`` with your project):

.. code-block:: bash

    sphinx-intl update-txconfig-resources --transifex-organization-name open-contracting-partnership-1 --transifex-project-name ocds-extensions --pot-dir build/locale --locale-dir locale

Push source files to Transifex for translation:

.. code-block:: bash

    tx push -s

Once you've translated strings on Transifex, email data@open-contracting.org so that we can pull translation files from Transifex, build MO files, and commit the changes:

.. code-block:: bash

    tx pull -f -a
    sphinx-intl build -d locale

Update existing translations
----------------------------

Existing translations are stored in `ocds-extensions-translations <https://github.com/open-contracting/ocds-extensions-translations>`__.

Follow the steps for creating new translations, then clone the repository:

.. code-block:: bash

    git clone https://github.com/open-contracting/ocds-extensions-translations.git

Change into its directory:

.. code-block:: bash

    cd ocds-extensions-translations

And push its translations. See `Transifex's documentation <https://developers.transifex.com/docs/using-the-client#pushing-files-to-transifex>`__ for more information on how to specify which languages or resources to push:

.. code-block:: bash

    tx push -t

Once you've translated strings on Transifex, follow the same final step under creating new translations.
