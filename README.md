# MemberZone
A minimalist site to keep track of your memberships and subscriptions

## About the project
MemberZone is a personal hobby project which I chose to develop to deepen my understanding of and familiarity with the Django framework.
It is hosted on Heroku, with Cloudflare providing the domain [www.member-zone.net]() and related DNS and ancillary services.
The source code is freely available to use, modify and distribute under the terms of the AGPLv3 licence.

## Underlying technology
The project is built using the Django framework, including templates, views and the ORM. The following technologies are used for various aspects of the project:
  - PostgreSQL for the database
  - Celery with Redis as a broker to manage scheduled tasks
  - htmx and hyperscript to make a lightweight, interactive front-end
  - Tailwind CSS
  - Django Crispy Forms for form styling
  - Whitenoise for managing and serving static files
  - Pytest and Selenium Webdriver for testing

## Known issues
  - The suite of tests (run with the `pytest` command) is currently pretty flaky, and doesn't pass in the production environment
  (even though the full functionality which the tests are supposed to cover has been confirmed to work). I will work on this when I have time.

## Contributing
If you discover a problem with the code or want to suggest an improvement, feel free to open an issue here on GitHub.
Additionally, you can open a pull request with your proposed changes.
