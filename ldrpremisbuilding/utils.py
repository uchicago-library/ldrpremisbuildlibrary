
from collections import namedtuple
from os import makedirs
from os.path import abspath, dirname, exists, join
from uuid import uuid4
from sys import stderr

from pypairtree.utils import identifier_to_path
from pypremis.lib import PremisRecord
from pypremis.nodes import *

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a command line tool to find all premis records in longTermStorage and if not already in livePremis copy the file into livePremis"
__COPYRIGHT__ = "University of Chicago, 2016"

# start of premis node creation functions

def build_a_premis_event(event_type, event_date, outcome_status, outcome_message, agent, objid):
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
    new_event = Event(event_id, event_type, event_date)
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
# start of premis record creation functions

def write_out_a_complete_file_tree(directory_string):
    """a function to write out a complete directory hierarchy to disk

    ___Args__
    1. directory_string (str): a string representing a path that needs to be written to disk
    """
    if abspath(directory_string) == directory_string:
        directory_string = directory_string[1:]
    new_output = "/"
    for n_part in directory_string.split("/"):
        new_output = join(new_output, n_part)
        if exists(new_output):
            pass
        else:
            makedirs(new_output, exist_ok=True)
    return True

def create_new_premis_agent(agents_root, dto, edit_identifier=None):
    """a function to create a new PREMIS record for an agent

    __Args__
    1. agents_root (str): a string that is a valid path to agent records in livePremis
    2. dto (AgentDataTransferObject): an object to pass Agent data from an api this function
    """
    if edit_identifier:
        identifier = edit_identifier
        pairtree_identifier = path_to_identifier(edit_identifier)
    else:
        identifier = uuid4().hex
        pairtreee_identifier = str(identifier_to_path(identifier))
    path_to_new_agent_record = join(agents_root, pairtreee_identifier, "prf", "agent.xml")
    agent_id = AgentIdentifier("DOI", identifier)
    new_agent = Agent(agent_id)
    new_agent.set_agentType(dto.type)
    new_agent.set_agentName(dto.name)
    new_record = PremisRecord(agents=[new_agent])
    write_out_a_complete_file_tree(dirname(path_to_new_agent_record))
    new_record.write_to_file(path_to_new_agent_record)
    return identifier

# end of premis record creation functions

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

def find_mimetype_from_premis(object_chars):
    return object_chars.get_format()[0].get_formatDesignation().get_formatName()

def find_objid_from_premis(premis_object):
    """a function the object identifier of a particular PremisRecord instance

    __Args__
    1. premis_object (PremisRecord): an instance of pypremis.lib.PremisRecord
    """
    return premis_object.get_objectIdentifier()[0].get_objectIdentifierValue()

def find_related_objects_from_premis(premis_object):
    """a function to find related objects for a given premis record

    __Args__
    1. premis_record (PremisRecord): an instance of pypremis.node.Object
    """
    related_objects_list = []
    try:
        relationships = premis_object.get_relationship()
    except KeyError:
        return []
    for n_relationship in relationships:
        if n_relationship.get_relatedObjectIdentifier():
            for n_related_object in n_relationship.get_relatedObjectIdentifier():
                related_objects_list.append(n_related_object.get_relatedObjectIdentifierValue())
    return related_objects_list

def extract_identity_data_from_premis_record(premis_file):
    """a function to extract data needed to run a fixity check from a particular premis xml file

    __Args__
    1. premis_file (str or PremisRecord): a string pointing to a premis record on-disk or
    an instance of a PremisRecord
    """
    def premis_data_packager(content_loc, this_record, objid, file_size, fixity_digest,
                             mimetype, events, related_objects):
        """a function to return a data transfer object for extracting identity data
           from a particular PremisRecord instance
        """
        return namedtuple("premis_data",
                          "content_loc premis_record objid file_size fixity_to_test " + \
                          "mimetype events_list related_objects")\
                         (content_loc, this_record, objid, int(file_size), fixity_digest,
                          mimetype, events, related_objects)
    this_record = open_premis_record(premis_file)
    this_object = this_record.get_object_list()[0]
    the_characteristics = find_object_characteristics_from_premis(this_object)
    objid = find_objid_from_premis(this_object)
    file_size = find_size_info_from_premis(the_characteristics)
    file_mimetype = find_mimetype_from_premis(the_characteristics)
    fixity_digest = find_fixities_from_premis(the_characteristics, 'md5')
    content_loc = this_object.get_storage()[0].get_contentLocation().get_contentLocationValue()
    events = get_events_from_a_premis_record(this_record)
    related_objects = find_related_objects_from_premis(this_object)
    data = premis_data_packager(content_loc, this_record, objid, int(file_size), fixity_digest,
                                file_mimetype, events, related_objects)
    return data

def extract_core_information_agent_record(premis_file):
    def data_packager():
        return namedtuple("agent_data", "name identifier type events")\
        (agent_name, agent_identifier, agent_type, agent_events)

    this_record = open_premis_record(premis_file)
    this_agent = this_record.get_agent_list()[0]
    stderr.write(str(this_agent))
    agent_identifier = this_agent.get_agentIdentifier()[0].get_agentIdentifierValue()
    agent_type = this_agent.get_agentType()
    agent_name = this_agent.get_agentName()
    try:
        agent_events = this_agent.get_linkingEventIdentifier()
    except KeyError:
        agent_events = []
    data = data_packager()
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
