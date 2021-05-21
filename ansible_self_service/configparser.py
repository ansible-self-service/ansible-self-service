#!/usr/bin/python3
# Datum: 21.05.2021
# Author: dirk.loser@deepl.com
# Funktion: yaml file parsen und validieren
#
import sys,yaml
from cerberus.validator import Validator



class Parser():

    def parser_schema(self):
        """Return Schema"""
        schema = '''
          categories:
            type: dict
        
          items:
            type: dict
        '''
        return schema

    def open_config(self,self_service_cfg):
        "Reads self-service.cfg and Validates"
        schema = yaml.safe_load(self.parser_schema())
        with open('{}'.format(self_service_cfg)) as fobj:
            document = yaml.safe_load(fobj)
        vali = Validator(schema)
        if vali.validate(document) == True:
            return document
        else:
            raise ConfigValidationException(vali.errors)


class ConfigValidationException(Exception):
    pass


if __name__ == '__main__':
    o = Parser()
    o.open_config(sys.argv[1])
