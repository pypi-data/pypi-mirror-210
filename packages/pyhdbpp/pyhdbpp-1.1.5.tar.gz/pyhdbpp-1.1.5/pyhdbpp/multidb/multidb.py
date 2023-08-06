#!/usr/bin/env python3

import sys, re, traceback
from ..abstract import AbstractReader
from ..utils import *
from ..reader import reader

# MultiDBReader

class MultiDBReader(AbstractReader):
    
    def __init__(self, config='',**kwargs):
        """
        config would be:
         - a list of dbnames
         - a comma-separated string
         - a {dbname:config} dictionary
        
        if just names are given, config for each db 
        will be read from tango db
        """
        self.readers = {}
        self.attributes = {}
        self.configs = {}
        if isinstance(config,str):
            config = [s.strip() for s in config.split(',')]
        if isinstance(config,list):
            config = dict((s, load_config_from_tango(s))
                for s in config)
        if isinstance(config,dict):
            for k,data in config.items():
                try:
                    if isinstance(data, str):
                        data = load_config_from_tango(v)
                    rd = reader(apiclass=data['apiclass'],config=data)
                    self.configs[k] = data
                    self.readers[k] = rd
                except:
                    logger.warning('Unable to load %s schema' % k)

        self.get_attributes(load=True)


    def get_connection(self, attribute=None, schema=None):
        """
        Return the connection object to avoid a client
        to open one for custom queries.
        The returned object will be implementation specific.
        """
        if attribute:
            attribute = self.get_attribute_name(attribute)
            for k,v in self.attributes.items():
                if attribute in v:
                    return self.readers[k]
        elif schema:
            return self.readers.get(schema,None)
        else:
            return self.readers


    def get_attributes(self, active=False, pattern='', load=False):
        """
        Queries the database for the current list of archived attributes.
        
        Once it has been queried, result is cached unless load=True is passed.
        
        arguments:
            active: True: only attributes currently archived
                    False: all attributes, even the one not archiving anymore
            regexp: '' :filter for attributes to retrieve
        """
        if load or not self.attributes:
            for k,v in self.readers.items():
                self.attributes[k] = [a.lower() for a in v.get_attributes()]
            
        return sorted(set(a for k,v in self.attributes.items() for a in v 
                    if not pattern or attr_match(pattern,a)))
    
    def get_attribute_name(self,attribute):
        """
        get attribute name as it is used in hdb++ (e.g. FQDN)
        """
        attribute = attr_translate(attribute)
        attrs = self.get_attributes(pattern=attribute, load=False)
        if len(attrs)>1:
            raise Exception('MultipleAttributeMatches')
        if not len(attrs):
            raise Exception('AttributeNotArchived')
        return attrs[0]

    def is_attribute_archived(self, attribute, *args, **kwargs):
        """
        Returns if an attribute has values in DB.

        arguments:
            attribute: fqdn for the attribute.
            active: if true, only check for active attributes,
                    otherwise check all.
        """
        return bool(self.get_attribute_name(attribute))

    def get_last_attribute_value(self, attribute):
        """
        Returns last value inserted in DB for an attribute

        arguments:
            attribute: fqdn for the attribute.
        returns:
            (epoch, r_value, w_value, quality, error_desc)
        """
        attribute = self.get_attribute_name(attribute)
        db = self.get_connection(attribute)
        return db.get_last_attributes_values([attribute])[attribute]

    def get_last_attributes_values(self, attributes, columns = 'time, r_value'):
        """
        Returns last values inserted in DB for a list of attributes

        arguments:
            attribute: fqdn for the attribute.
            columns: requested columns separated by commas
        returns:
            {'att1':(epoch, r_value, w_value, quality, error_desc),
             'att2':(epoch, r_value, w_value, quality, error_desc),
             ...
            }
        """
        return dict((a,self.get_last_attribute_values(a)) for a in attributes)

    def get_attribute_values(self, attribute,
            start_date, stop_date=None,
            decimate=True,
            **params):
        """
        Returns attribute values between start and stop dates.

        arguments:
            attribute: fqdn for the attribute.
            start_date: datetime, beginning of the period to query.
            stop_date: datetime, end of the period to query.
                       if None, now() is used.
            decimate: aggregation function to use in the form:
                      {'timedelta0':(MIN, MAX, ...)
                      , 'timedelta1':(AVG, COUNT, ...)
                      , ...}
                      if None, returns raw data.
        returns:
            [(epoch0, r_value, w_value, quality, error_desc),
            (epoch1, r_value, w_value, quality, error_desc),
            ... ]
        """
        attribute = self.get_attribute_name(attribute)
        db = self.get_connection(attribute)
        if isinstance(start_date,(int,float)) and start_date < 0:
            start_date = now() + start_date
        stop_date = stop_date or now()
        return db.get_attribute_values(attribute, start_date, stop_date, 
                                       decimate, **params)

    def get_attributes_values(self, attributes,
            start_date, stop_date=None,
            decimate=None,
            correlate = False,
            columns = 'time, r_value',
            **params):
        """
        Returns attributes values between start and stop dates
        , using decimation or not, correlating the values or not.

        arguments:
            attributes: a list of the attributes' fqdn
            start_date: datetime, beginning of the period to query.
            stop_date: datetime, end of the period to query.
                       if None, now() is used.
            decimate: aggregation function to use in the form:
                      {'timedelta0':(MIN, MAX, ...)
                      , 'timedelta1':(AVG, COUNT, ...)
                      , ...}
                      if None, returns raw data.
            correlate: if True, data is generated so that
                       there is available data for each timestamp of
                       each attribute.
            columns: columns separated by commas
                    time, r_value, w_value, quality, error_desc                       

        returns:
            {'attr0':[(epoch0, r_value, w_value, quality, error_desc),
            (epoch1, r_value, w_value, quality, error_desc),
            ... ],
            'attr1':[(...),(...)]}
        """
        return dict((a,self.get_attribute_values(a, start_date, stop_date,
                    decimate)) for a in attributes)

