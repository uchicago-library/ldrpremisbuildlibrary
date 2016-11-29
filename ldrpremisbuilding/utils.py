from collections import namedtuple
from uuid import uuid4

from pypremis.lib import PremisRecord
from pypremis.nodes import *

# start of premis node creation functions

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

# end of premis node creation functions

# start of premis loading and writing functions 

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

def open_premis_record(premis_file_path):
    """a function to attempt to create an instance of a PremisRecord

    __Args__
    1. premis_file_path (str): a string pointing to the location of a premis xml file on-disk
    """
    output = None
    try:
        output = PremisRecord(frompath=premis_file_path)
    except ValueError:
        stderr.write("{} is not a valid premis record\n".format(premis_file_path))
    return output

# end of premis loading and writing functions

# start of premis searchiing functions

def find_object_characteristics_from_premis(premis_object):
    """a function to return the object characteristics node from the a PremisRecord object

    __Args__
    1. premis_object (PremisRecord): an instance of the pypremis.lib.PremisRecord class
    """
    return premis_object.get_objectCharacteristics()[0]

def find_fixities_from_premis(object_chars, digest_algo_filter):
    """a function to return the messageDigest value for a particular algorithm
       if it exists in the object characteristics presented

    __Args__
    1. object_chars (list): a list of pypremis.nodes.ObjectCharacteristic nodes
    2. digest_algo_filter (str): a string label for a particular digest
       algorithm that needs to be found
    """
    obj_fixiites = object_chars.get_fixity()
    for fixity in obj_fixiites:
        if fixity.get_messageDigestAlgorithm() == digest_algo_filter:
            return fixity.get_messageDigest()
    return None

def find_size_info_from_premis(object_chars):
    """a function to find the size element value of a particular object characteristic

    __Args__
    1. object_chars (list): a list of pypremis.nodes.ObjectCharacteristic nodes
    """
    return object_chars.get_size()

def find_objid_from_premis(premis_object):
    """a function the object identifier of a particular PremisRecord instance

    __Args__
    1. premis_object (PremisRecord): an instance of pypremis.lib.PremisRecord
    """
    return premis_object.get_objectIdentifier()[0].get_objectIdentifierValue()

def extract_identity_data_from_premis_record(premis_file):
    """a function to extract data needed to run a fixity check from a particular premis xml file

    __Args__
    1. premis_file (str or PremisRecord): a string pointing to a premis record on-disk or
    an instance of a PremisRecord
    """
    def premis_data_packager(content_loc, this_record, objid, file_size, fixity_digest, events):
        """a function to return a data transfer object for extracting identity data
           from a particular PremisRecord instance
        """
        return namedtuple("premis_data", "content_loc premis_record objid file_size fixity_to_test events_list")\
                         (content_loc, this_record, objid, int(file_size), fixity_digest, events)
    this_record = open_premis_record(premis_file)
    this_object = this_record.get_object_list()[0]
    the_characteristics = find_object_characteristics_from_premis(this_object)
    objid = find_objid_from_premis(this_object)
    file_size = find_size_info_from_premis(the_characteristics)
    fixity_digest = find_fixities_from_premis(the_characteristics, 'md5')
    content_loc = this_object.get_storage()[0].get_contentLocation().get_contentLocationValue()
    events = get_events_from_a_premis_record(this_record)
    data = premis_data_packager(content_loc, this_record, objid, int(file_size), fixity_digest, events)
    return data

def find_particular_event(event_list, event_string):
    """a function to seek out a particular type of event from a list of events in a PremisRecord

    __Args__
    1. event_list (list): a list of pypremis.lib.Event nodes
    2. event_string (str): a string representing an eventCategory that needs to be searched for
    """
    output = None
    for n_event in event_list:
        if n_event.get_eventCategory() == event_string:
            output = n_event
            break
    return output

def get_events_from_a_premis_record(premis_record):
    """a function to retrieve a list of events from a given premis record
    __Args__
    1, premis_record (PremisRecord):
    """
    if not isinstance(premis_record, PremisRecord):
        raise ValueError("{} is not a valid PremisRecord instance\n".format(str(premis_record)))
    premis_events = premis_record.get_event_list()
    events = []
    for n_event in premis_events:
        event_date = n_event.get_eventDateTime()
        event_type = n_event.get_eventType()
        event_outcome = n_event.get_eventOutcomeInformation()[0].get_eventOutcome()
        events.append((event_type, event_date, event_outcome))
    return events

# end of premis searching functions
