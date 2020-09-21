# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    FollowupAction,
    AllSlotsReset,
)
import logging
from lxml import html
import requests
import json
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ActionExplainFaqs(Action):
    """Returns the chitchat utterance dependent on the intent"""

    def name(self) -> Text:
        return "action_explain"

    def run(self, dispatcher, tracker, domain) -> List[EventType]:
        topic = tracker.get_slot("source")
        logger.info("topic is :%s" %topic)
        if topic in ["who", "mohfw", "default", "us", "cdc"]:
            entities=tracker.latest_message['entities']
            if entities:
                entity=entities[0].get('entity')
                dispatcher.utter_message(template=f"utter_{topic}_{entity}")
            else:
                dispatcher.utter_message(template=f"utter_default")
        else:
            dispatcher.utter_message(template=f"utter_default")
        return []

class ActionForm(FormAction):

    def name(self):
        return "requests_source_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["source"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
                "source": [
                    self.from_entity(entity="source"),
                    self.from_text(not_intent="thankyou")]}

    def validate_source(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate source value."""

        if value.lower() in ["who","mohfw", "us", "cdc", "default"]:
            # validation succeeded, set the value of the source slot to value
            return {"source": value.lower()}
        else:
            dispatcher.utter_message(template="utter_wrong_source")
            return []
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            #return {"source": "default"}

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
            ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        dispatcher.utter_message(text=f"You are selected:  {tracker.get_slot('source')}")
        return []

class ActionResetSlot(Action):    

    def name(self) -> Text:
        return "action_reset_solts"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"you are welcome :)")
        return [AllSlotsReset()]

class ActionCovidCases(Action):

    def name(self) -> Text:
        return "action_covid_cases"

    def run(self, dispatcher, tracker, domain):
        res=requests.get("https://www.worldometers.info/coronavirus/")
        soup = BeautifulSoup(res.content, features="lxml")
        entities=tracker.latest_message['entities']
        if entities:
            entity=tracker.latest_message['entities'][0]
            country=entity.get('value').lower()
        else:
            dispatcher.utter_message(template=f"utter_default")
            return []
        trs=soup.find_all('tr')
        cases={}
        deaths={}
        recovered={}
        active={}
        for i in range(8, 232):
            tds=trs[i].find_all('td')
            cases.update({str(tds[1].get_text().strip().lower()) : int(tds[2].get_text().replace(",",""))})

        for i in range(8, 232):
            tds=trs[i].find_all('td')
            if tds[4].get_text() in ['N/A', '', ' ']:
                td=0
            else:
                td=int(tds[4].get_text().replace(",",""))
            deaths.update({str(tds[1].get_text().strip().lower()):td})

        for i in range(8, 232):
            tds=trs[i].find_all('td')
            if tds[6].get_text() in ['N/A', '', ' ']:
                td=0
            else:
                td=int(tds[6].get_text().replace(",",""))
            recovered.update({str(tds[1].get_text().strip().lower()):td})

        for i in range(8, 232):
            tds=trs[i].find_all('td')
            if tds[8].get_text() in ['N/A', '', ' ']:
                td=0
            else:
                td=int(tds[8].get_text().replace(",",""))
            active.update({str(tds[1].get_text().strip().lower()):td})

        infected=cases[country]
        death=deaths[country]
        recover=recovered[country]
        active_cases=active[country]
        dispatcher.utter_message(text=f"Infected : {infected}\nDeaths: {death}\nRecovered: {recover}\nActive: {active_cases}")
        return [] 
