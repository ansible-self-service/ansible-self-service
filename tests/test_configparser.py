from ansible_self_service.configparser import Parser
import os

VALID_CONFIG = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets', 'self-service.yaml')

def test_parse_valid_file():
    o = Parser()
    result = o.open_config(VALID_CONFIG)
    assert result['categories'] == {'Misc':{} } 
