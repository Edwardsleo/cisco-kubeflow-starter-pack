## story_01
* greet
  - utter_greet
  - requests_source_form
  - form{"name": "requests_source_form"}
  - slot{"source": "mohfw"}
  - form{"name": null}

* covid
  - action_explain

* covid_cases
  - action_covid_cases

* thankyou
  - action_reset_solts

## story_02
* greet
  - utter_greet
  - requests_source_form
  - form{"name": "requests_source_form"}
  - slot{"source": "mohfw"}

* stop
  - utter_ask_continue

* deny
  - action_reset_solts
  - form{"name": null}

## story_03
* greet
  - utter_greet
  - requests_source_form
  - form{"name": "requests_source_form"}
  - slot{"source": "mohfw"}

* stop
  - utter_ask_continue

* affirm
  - requests_source_form
  - form{"name": "requests_source_form"}

## story_04
* covid_cases
  - action_covid_cases

* stop
  - utter_ask_continue

* deny
  - action_reset_solts
