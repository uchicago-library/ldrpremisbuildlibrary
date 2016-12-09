
from collections import namedtuple
from json import dumps, loads
import requests
from urllib.request import urlopen, Request
from urllib.parse import ParseResult

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a set of functions to use to retrieve existing or create new agent records in the ldr system"
__COPYRIGHT__ = "University of Chicago, 2016"

def load_json_from_url(url):
    data = requests.get(url)
    return data.json()

def construct_url_to_agent_events(agentid):
    a_url = ParseResult(scheme="https", netloc="y2.lib.uchicago.edu", fragment="", query="",
                        params="", path="/ldragents/agents/{}/events".format(agentid.strip()))
    return a_url.geturl()

def construct_url_to_get_a_user(agentid):
    a_url = ParseResult(scheme="https", netloc="y2.lib.uchicago.edu", fragments="", params="", path="/ldragents/agents/" + agentid.strip())
    return a_url.geturl()

def construct_url_to_search_for_matches(user_query):
    a_url = ParseResult(scheme="https", netloc="y2.lib.uchicago.edu", path="/ldragents/agents", fragment="", params="", query="term=" + user_query.strip())
    return a_url.geturl()

def construct_url_to_all_agents():
    a_url = ParseResult(scheme="https", netloc="y2.lib.uchicago.edu", path="/ldragents/agents", fragment="", params="", query="")
    return a_url.geturl()

def does_this_agent_exist(term):
    output = []
    searcher = construct_url_to_search_for_matches(term)
    result = load_json_from_url(searcher)
    if result.get("data") and result.get("data").get("agents"):
        result_values = list(result.get("data").get("agents").keys())
        for key in result_values:
            an_agent = result.get("data").get("agents").get(key)
            agent_dto = namedtuple("agentdata", "name identifier")(an_agent.get("name"), an_agent.get("identifier"))
            output.append(agent_dto)
        return (True, output)
    else:
        return (False, None)

def package_post_data_for_new_agent(agent_name, agent_type):
   output = {"fields":["name", "type"], "name":agent_name, "type":agent_type}
   return dumps(output).encode('utf-8')

def create_an_agent(agent_name, agent_type):
    print(agent_name)
    check = does_this_agent_exist(agent_name)
    if not check[0]:
        the_url = construct_url_to_all_agents()
        post_data = package_post_data_for_new_agent(agent_name, agent_type)
        request_to_make = Request(the_url, data=post_data, headers={"content-type": "application/json"})
        response = urlopen(request_to_make)
        if response.getcode() == 200:
            return (True, loads(response.read().decode("utf-8")))
        else:
            return (False, None)
    else:
        return (True, check[1])

def add_event_to_an_agent(event_id, identifier=None, agent_name=None):
    if agent_name:
        check = does_this_agent_exist(agent_name)
        if check[0] and len(check[1]) == 1:
            agent_id = check[1][0].identifier
        else:
             return ("too many options with that name", check[1])
    elif identifer:
        agent_id = identifier.strip()
    url = construct_url_to_agent_events(agent_id)
    return url

if __name__ == "__main__":
    new_agent = add_event_to_an_agent("foo", agent_name="tdanstrom")
    print(new_agent)
