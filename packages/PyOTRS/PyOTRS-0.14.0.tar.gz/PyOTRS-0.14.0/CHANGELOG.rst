Change Log
==========

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

0.x.y - 2023-xx-yy (unreleased)
--------------------------------

0.14.0 - 2023-05-23
-------------------
- final minor release before 1.0.0 (see #43)

0.12.7 - 2023-05-21
-------------------
- merge !35: fix link list result

0.12.6 - 2023-02-04
-------------------
- fix #47: making client.session_restore_or_create() run on Windows.

0.12.4 - 2021-12-30
-------------------
- fix: make sure fallback works

0.12.3 - 2021-12-21
-------------------
- fix #45: make sure SessionGet works (expects correct Result)

0.12.2 - 2021-12-11
-------------------
- fix #44: keep track in Session ID store if legacy_sessions are used
- fix: Switch timeout unit from minutes to seconds (!29)
- change: update recommendation in Exception (use session_restore_or_create)
- change: OTRS API documentation link

0.11.0 - 2021-07-21
-------------------
- add: support for OTRSv8+ by adding support for "AccessToken" instead of "SessionID"

0.10.0 - 2020-07-14
-------------------
- add: Client.session_get() - which uses a better way to check whether a SID is valid
- add: Client.session_restore_or_create()
- deprecated: session_check_is_valid use session_get
- deprecated: session_restore_or_set_up_new use session_restore_or_create

0.9.0 - 2020-04-23
------------------
- add: implement !23 (fix #31) adding support for CustomerUser

0.8.0 - 2020-04-17
------------------
- remove:  click and colorama from core dependencies

0.7.1 - 2020-04-06
------------------
- fix #27: GET must not contain a body (OTRS: #14203)

0.6.0 - 2020-03-13
------------------
- add: auth to Client (e.g. for HTTP BasicAuth)

0.5.1 - 2020-03-12
------------------
- add: client_auth_cert to Client
- add: Client.ticket_get_by_list return empty list if asked for empty
- remove: Python3.4 checks (colorama no longer works on py34)
- fix #18: Attachment.create_from_file did not decode "Content"
- fix: building the docs

0.4.1 - 2019-03-09 - Beta
-------------------------
- This has been in "alpha" way too long now marked as Beta

0.4.0 - 2019-03-08
------------------
- add: introduced deprecation mechanism
- add: include CI tests for Python 3.6, 3.7
- internal: PEP8 fixes
- internal: clean up and separate requirements file
- fix #21: update README to include webservice info

0.3.0 - 2018-10-07
------------------
- internal: Update build and test tooling

0.2.4 - 2018-10-07
------------------
- fix bug in Client.__init() - Default Connector Config was always used

0.2.3 - 2018-08-21
------------------
- add "webservice_path" to Client() to allow custom path

0.1.29 - 2017-10-03
-------------------
- fix missing TicketID in Client.ticket_update()
- complete test coverage

0.1.28 - 2017-07-25
-------------------
- add option to set a User Agent for HTTP requests

0.1.27 - 2017-07-13
-------------------
- fix #11: Attachment.create_from_file fails on binary file

0.1.26 - 2017-07-12
-------------------
- fix #9: Add Type/TypeID to Ticket.create_basic()
- fix #10: hardcoded operation "TicketGetList" in Client.ticket_get_by_id()

0.1.25 - 2017-06-22
-------------------

0.1.24 - 2017-05-23
-------------------
- fix #8: Article handling in Client.ticket_create()

0.1.23 - 2017-05-17
-------------------
- add store attachment feature to cli

0.1.22 - 2017-03-04
-------------------
- completed FAQ API

0.1.21 - 2016-11-14
-------------------
- FAQ api not yet completed
- updated unittests for FAQ api (as far as implemented)
- fixed CLI client (webservice removed)

0.1.19 - 2016-11-12
-------------------
- ticket_search - dynamic_fields takes either a DynamicField to a list of DynamicFields
- BREAKING: implement FAQ api

0.1.18 - 2016-11-06
-------------------
- ticket_search will now return [] for empty result

0.1.17 - 2016-11-06
-------------------
- change name of lists (e.g. list_dynamic_fields is now dynamic_fields)
- update to_dct() method (add flags to choose what to print)

0.1.16 - 2016-11-05
-------------------
- fix bug when https_verify is disabled
- add link api
- add dynamic_field_get access
- add article_get access
- add `dynamic_fields` to ticket_search

0.1.9 - 2016-09-11
------------------
- full text search was fixed upstream and is now in beta testing

0.1.7 - 2016-04-24
------------------
- fix PyOTRS Shell CLI

0.1.6 - 2016-04-24
------------------
- fix some docs
- first upload to public repo
- added ticket_get_by_ids to get multiple tickets in one request
- completed full unittest coverage
- added Gitlab config for Continuous Integration testing
- Client.ticket_create() - create a Ticket in OTRS
- Setuptools for proper packaging

0.1.0 - 2016-04-10
------------------
- Initial creation
