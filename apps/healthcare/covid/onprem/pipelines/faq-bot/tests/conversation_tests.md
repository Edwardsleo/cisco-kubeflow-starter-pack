#### This file contains tests to evaluate that your bot behaves as expected.
#### If you want to learn more, please see the docs: https://rasa.com/docs/rasa/user-guide/testing-your-assistant/

## story_01
* covid_cases: confirmed cases in indaia
  - action_covid_cases

* covid_cases: confirmed cases in world
  - action_covid_cases

* deny: no
  - action_reset_solts

* stop: ok
  - utter_ask_continue

* thankyou: bye
  - action_reset_solts
