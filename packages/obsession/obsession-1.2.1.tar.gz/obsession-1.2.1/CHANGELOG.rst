1.2.1 (released 2023-05-25)
---------------------------

- Bugfix: fix content iterator not being closed in SessionMiddleware

1.2.0 (released 2022-06-23)
---------------------------

- Bugfix: fix error in MemoryBackend.modified_at()
- Add tests for python 3.8 - 3.11
- Expire session cookie when the session is deleted
- Auto extend cookie lifetime while session is active

1.1.1 (released 2021-02-25)
---------------------------

- Fixed error in __len__ implementation

1.1.0 (released 2020-08-26)
---------------------------

- Fixed deprecation warnings when running under Python 3.6+
- Added SameSite attribute for cookies

1.0.0 (released 2020-01-15)
---------------------------

- Dropped Python 2.7 support
- Bugfix: allow sessions to be saved when empty

0.2 (released 2018-03-12)
-------------------------

- Added JSON serializer
- Bugfix: session ids ending in periods are no longer silently dropped
- Only set a session id cookie when new session are created or when the id has
  changed, avoiding unnecessary Set-Cookie headers being sent.

0.1
----

- Initial release
