..
    Copyright (C) 2020-2023 TU Wien.

    Invenio Config TUW is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version 2023.2 (released 2023-04-24, updated 2023-05-26)

- v11 compat: Update permission policies and disable archive download
- Set affiliation (hard-coded) to TU Wien in `user.profile`
- Set a default template for the `description` metadata field
- Add a null check for the current_user in the logging formatter


Version 2023.1 (released 2023-01-13)

- Update definition of the default creator for new uploads


Version 2022.3 (released 2022-10-28, updated 2022-11-30)

- v10 compat: Discard imports of removed Admin/SuperUser generators
- Rework the initialization procedure used for some custom overrides
- Migrate from setup.py to setup.cfg
- Move Flask config override from Invenio-Theme-TUW to Invenio-Config-TUW
- Update "Terms of Use" link in registration form


Version 2022.2 (released 2022-07-19, updated 2022-10-22)

- v9 compat: Chase changes in Invenio-{Accounts,OAuthClient} 2.x
- v9 compat: Update permission policies
- v9 compat: Hack in permission policy for communities
- Refactor permissions and config
- Remove leftover views.py
- Set deposit form file size limits
- Fix permissions
- Reverse contents of CHANGES.rst (recent changes are shown on top)
- Attach SMTP error handler to the application in production mode
- Add custom logging formatter
- Auto-confirm newly registered users' e-mail addresses if ``SECURITY_CONFIRMABLE`` is ``False``
- Set default user preferences (``visibility=public``, ``email_visibility=restricted``)
- Set default value for ``version`` metadata to ``1.0.0``
- Add config item to put the system into "read-only mode"


Version 2022.1 (released 2022-03-23, updated 2022-04-06)

- Update permissions for creating and editing drafts
- Use the OAI metadata implementation from Invenio-RDM-Records
- Change the default file size and bucket quota limits to 75GB


Version 2021.2 (released 2021-12-07, updated 2021-12-20)

- Make ready for InvenioRDM v7
- Add requests permission policy
- Enforce a rate limit for HTTP requests
- Change method of overriding the record permission policy
- Add datacite and oai_datacite metadataPrefixes to the OAI endpoint


Version 2021.1 (released 2021-07-15)

- Initial public release.
- Update the list of citation styles
