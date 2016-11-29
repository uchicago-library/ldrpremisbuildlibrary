from uuid import uuid4

from pypremis.lib import PremisRecord
from pypremis.nodes import *

def build_fixity_premis_event(event_type, event_date, outcome_status, outcome_message, agent, objid):
    """a function to generate a minimal PREMIS event record

    __Args__
    1. event_type (str): a label that defines the category of event that is being created
    2. event_date (str): an ISO date string representing the time that this event occurred
    3. outcome_status (str): either SUCCESS or FAILURE, a label defining whether or not the
                             event was able to be completed
    4. outcome_message (str): a brief (1-2 sentence(s)) description of what happened in this event
    5. agent (str): the official name for the agent that performed this event
    6. objid (str): the PREMIS identifier for the object that this event occurred on
    """
    event_id = EventIdentifier("DOI", str(uuid4()))
    linkedObject = LinkingObjectIdentifier("DOI", objid)
    linkedAgent = LinkingAgentIdentifier("DOI", str(uuid4()))
    event_detail = EventOutcomeDetail(eventOutcomeDetailNote=outcome_message)
    event_outcome = EventOutcomeInformation(outcome_status, event_detail)
    new_event = Event(event_id, "fixity check", event_date)
    new_event.set_linkingAgentIdentifier(linkedAgent)
    new_event.set_eventOutcomeInformation(event_outcome)
    new_event.set_linkingObjectIdentifier(linkedObject)
    return new_event

def add_event_to_a_premis_record(premis_record, an_event):
    """a function to add a PREMIS event to a particular premis record

    __Args__
    1. premis_record (PremisRecord) an instance of pyremis.lib.PremisRecord
    2. an_event (Event): an instance of pypremis.nodes.Event
    """
    try:
        premis_record.add_event(an_event)
        return True
    except ValueError:
        return False

def write_a_premis_record(premis_record, file_path):
    """a function to write a Premis Record to a particular file on-disk
    ___Args__
    1. premis_record (Premis Record): an instance of pypremis.lib.PremisRecord
    2. file_path (str): a string representing a valid location on-disk
    """
    try:
        print(file_path)
        premis_record.write_to_file(file_path)
    except Except as e:
        raise(e)
