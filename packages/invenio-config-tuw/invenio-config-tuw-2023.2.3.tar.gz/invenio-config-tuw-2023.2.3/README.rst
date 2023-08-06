..
    Copyright (C) 2020-2022 TU Wien.

    Invenio-Config-TUW is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

====================
 Invenio-Config-TUW
====================

Invenio module for tweaking InvenioRDM to the needs of TU Wien.

We use this module to customize the following:

* Permission policies
* OIDC authentication handling
* E-Mail notification on errors
* Configuration values


Details
=======

Permission policies
-------------------

Currently, we are still operating on a friendly-user basis.
That is, while we cannot lose any data that has been uploaded by our users, we do not
allow every registered user to create record drafts, upload data, or publish records
from the get-go.
Instead, we require users to have the ``trusted-user`` role in order to be able to
create record drafts and upload data.
Similarly, we have the ``trusted-publisher`` role as a requirement for publishing
records.
Generally, these roles have to be assigned to users manually by an administrator.

On the test system, we give out these permissions automatically if we detect that a
newly registered user is an employee of TU Wien.


OIDC authentication handling
----------------------------

Because we have some special requirements regarding the authentication and signup
process, we have customized some of the handler functions for the OAuth client
that's integrated in InvenioRDM.
These customizations are contained in the files in ``auth/``.


E-Mail notification on errors
-----------------------------

This module defines a custom log handler for error-level logs which sends out
notifications as e-mail to a set of configured recipient addresses.


Configuration values
--------------------

Last but not least, we also set some default configuration values for deployments
of InvenioRDM at TU Wien.
The relevant files here are ``config.py`` and ``ext.py``.
