from uuid import uuid4

from pypremis.lib import PremisRecord
from pypremis.nodes import *

def build_fixity_premis_event(event_type, event_date, outcome_status, outcome_message, agent, objid):
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
    try:
        premis_record.add_event(an_event)
        return True
    except ValueError:
        return False

def write_a_premis_record(premis_record, file_path):
    try:
        print(file_path)
        premis_record.write_to_file(file_path)
    except Except as e:
        raise(e)
