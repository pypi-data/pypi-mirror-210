#!/usr/bin/env python3

import sys, re, traceback
from ..abstract import AbstractReader
from ..utils import *

try:
    import pymysql as mariadb
except:
    import MySQLdb as mariadb

# MariaDBReader

class MariaDBReader(AbstractReader):
    """
    read-only API for hdb++ databases, based on PyTangoArchiving AbstractReader
    """
    
    def __init__(self,config='',**kwargs):
        """
        Arguments accepted by pymysql connections:

        :param host: Host where the database server is located
        :param user: Username to log in as
        :param password: Password to use.
        :param database: Database to use, None to not use a particular one.
        :param port: MySQL port to use, default is usually OK. (default: 3306)
        :param bind_address: When the client has multiple network interfaces, specify
            the interface from which to connect to the host. Argument can be
            a hostname or an IP address.
        :param unix_socket: Optionally, you can use a unix socket rather than TCP/IP.
        :param read_timeout: The timeout for reading from the connection in seconds (default: None - no timeout)
        :param write_timeout: The timeout for writing to the connection in seconds (default: None - no timeout)
        :param charset: Charset you want to use.
        :param sql_mode: Default SQL_MODE to use.
        :param read_default_file:
            Specifies  my.cnf file to read these parameters from under the [client] section.
        :param conv:
            Conversion dictionary to use instead of the default one.
            This is used to provide custom marshalling and unmarshaling of types.
            See converters.
        :param use_unicode:
            Whether or not to default to unicode strings.
            This option defaults to true for Py3k.
        :param client_flag: Custom flags to send to MySQL. Find potential values in constants.CLIENT.
        :param cursorclass: Custom cursor class to use.
        :param init_command: Initial SQL statement to run when connection is established.
        :param connect_timeout: Timeout before throwing an exception when connecting.
            (default: 10, min: 1, max: 31536000)
        :param ssl:
            A dict of arguments similar to mysql_ssl_set()'s parameters.
        :param read_default_group: Group to read from in the configuration file.
        :param compress: Not supported
        :param named_pipe: Not supported
        :param autocommit: Autocommit mode. None means use server default. (default: False)
        :param local_infile: Boolean to enable the use of LOAD DATA LOCAL command. (default: False)
        :param max_allowed_packet: Max size of packet sent to server in bytes. (default: 16MB)
            Only used to limit size of "LOAD LOCAL INFILE" data packet smaller than default (16KB).
        :param defer_connect: Don't explicitly connect on contruction - wait for connect call.
            (default: False)
        :param auth_plugin_map: A dict of plugin names to a class that processes that plugin.
            The class will take the Connection object as the argument to the constructor.
            The class needs an authenticate method taking an authentication packet as
            an argument.  For the dialog plugin, a prompt(echo, prompt) method can be used
            (if no authenticate method) for returning a string from the user. (experimental)
        :param server_public_key: SHA256 authenticaiton plugin public key value. (default: None)
        :param db: Alias for database. (for compatibility to MySQLdb)
        :param passwd: Alias for password. (for compatibility to MySQLdb)
        :param binary_prefix: Add _binary prefix on bytes and bytearray. (default: False)
        """
        if config and isinstance(config,(str,bytes)):
            config = self.parse_config(config)

            
        self.config = config or {}
        self.config.update(kwargs)
            
        self.database = self.config.get('database','hdbpp')
        self.user = self.config.get('user','')
        self.password = self.config.get('password','')
        self.port = int(self.config.get('port','3306'))
        self.host = self.config.get('host','localhost')
        self.decimate = self.config.get('decimate',None)
        if self.decimate:
            if re.match('[0-9]+',decimate):
                self.decimate = int(self.decimate)
            elif str(self.decimate).lower().strip() == 'false':
                self.decimate = False
            elif str(self.decimate).lower().strip() in ('true','yes'):              
                decimate = True # decimation chosen by api

        self.attributes = {}
        self.tables = {} #table creators
        
        self._connect()
        
    def __del__(self):
        if getattr(self,'_cursor',None):
            self._cursor.close()
        if getattr(self,'db',None):
            self.db.close()
        
    def _connect(self):
        self.db = mariadb.connect(database=self.database,
            user=self.user, password=self.password, port=self.port, 
            host=self.host)
        self._cursor = self.db.cursor()
        return self._cursor
        
    def _query(self,query,prune=False):
        """
        query: SQL code
        """
        #print('%s.Query("%s")' % (self.database, query))
        self._cursor.execute(query)
        if prune:
            r,l = [],True
            while l:
                try:
                    l = self._cursor.fetchone()
                    if l and (not r or l[1:] != r[-1][1:]):
                        r.append(l)
                except:
                    print(r[-1:], l)
                    traceback.print_exc()
                    break
            return r
        else:
            return self._cursor.fetchall()
        
    def _describe_table(self,table):
        if not self.tables.get(table,None):
            self.tables[table] = self._query('describe %s' % table)
        return self.tables[table]
    
    def parse_config(self,config):
        """
        config string as user:password@host:port/database
        or dictionary like
        """
        try:
            if not isinstance(config,str):
                config = dict(config)
            elif re.match('.*[:].*[@].*',config):
                h = config.split('@')
                u,p = h[0].split(':')
                config = {'user':u,'password':p}
                if '/' in h[1]:
                    config['host'],config['database'] = h[1].split('/')
                else:
                    config['host'] = h[1]
                if ':' in config['host']:
                    config['host'],config['port'] = config['host'].split(':')
            else:
                if ';' in config:
                    config = '{%s}' % config.replace(';',',')
                if '{' in config:
                    config = dict(eval(config))
        except:
            raise Exception('Wrong format in config, should be dict-like')
        return config        

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
            self.get_attribute_id_table('*')
            
        if pattern:
            return [a for a in self.attributes if attr_match(pattern,a)]
            
        return sorted(self.attributes.keys())
    
    def get_attribute_name(self,attribute):
        """
        get attribute name as it is used in hdb++ (e.g. FQDN)
        """
        attribute = attr_translate(attribute)
        attrs = self.get_attributes(pattern=attribute, load=False)
        if len(attrs)>1:
            raise Exception('MultipleAttributeMatches')
        return attrs[0] if attrs else None

    def is_attribute_archived(self, attribute, active=False):
        """
        Returns if an attribute has values in DB.

        arguments:
            attribute: fqdn for the attribute.
            active: if true, only check for active attributes,
                    otherwise check all.
        """
        return bool(self.get_attribute_name(attribute))
    
    def get_attribute_id_table(self, attribute=''):
        """
        for each matching attribute returns name, ID and table name
        
        if no attribute or wildcard is given, all attribute info is loaded
        """
        if attribute and attribute not in ('*','%'):
            attribute = self.get_attribute_name(attribute)

        if attribute in self.attributes:
            return [self.attributes[attribute]] # return cached
        
        q = "select att_name,att_conf_id,data_type "
        q += " from att_conf as AC, att_conf_data_type as ACD where "
        q += "AC.att_conf_data_type_id = ACD.att_conf_data_type_id"
        if attribute and attribute not in ('*','%'):
            q += " and att_name like '%s'" % attribute
        
        data = [(a,i,'att_'+t) for (a,i,t) in self._query(q)]               
        self.attributes.update((str(t[0]).lower(),t) for t in data)
        return data

    def get_last_attributes_values(self, attributes, columns = '', n = 1):
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
        data = {}
        columns = columns or 'data_time, value_r, quality, att_error_desc_id'
        
        for a in attributes:
            try:
                a,i,t = self.get_attribute_id_table(a)[0]
                tdesc = str(self._query('describe %s'%t))
                tcol = ('int_time' if 'int_time' in tdesc else 'data_time')
                cols = ','.join(c for c in columns.split(',') 
                                if c.strip() in tdesc)
                data[a] = self._query('select %s from %s where '
                    'att_conf_id = %s order by %s desc limit %s'
                    % (cols, t, i, tcol, n))
            except:
                raise Exception('AttributeNotFound: %s' % a) 

        return data
    
    def get_attribute_values(self, attribute,
            start_date, stop_date=None,
            decimate=None,
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
        decimate = self.decimate if decimate is None else decimate
        attribute = self.get_attribute_name(attribute)
        r = self.get_attributes_values([attribute], start_date, stop_date, 
                                       decimate, False, **params)
        #print(r.keys(),start_date,stop_date)
        return r[attribute]

    def get_attributes_values(self, attributes,
            start_date, stop_date=None,
            decimate=None,
            correlate = False,
            columns = '', cast='DOUBLE',
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
                      {'timedelta0':(MIN, MAX,...)
                      , 'timedelta1':(AVG, COUNT,...)
                      ,...}
                      if None, returns raw data.
            correlate: if True, data is generated so that
                       there is available data for each timestamp of
                       each attribute.
            columns: columns separated by commas
                    time, r_value, w_value, quality, error_desc
            cast: it may be "DOUBLE" for return time as native python floats
                    or DECIMAL(17,6) to return full precission with us

        returns:
            {'attr0':[(epoch0, r_value, w_value, quality, error_desc),
            (epoch1, r_value, w_value, quality, error_desc),
            ... ],
            'attr1':[(...),(...)]}
        """
        data = {}
        columns = columns or 'data_time, value_r, quality, att_error_desc_id'
        if isinstance(start_date,(int,float)):
            start_date = time2str(start_date) 
        if stop_date is None:
            stop_date = now()
        if isinstance(stop_date,(int,float)):    
            stop_date = time2str(stop_date)
        
        for a in attributes:
            try:
                a,i,t = self.get_attribute_id_table(a)[0]
                #print('get_attribute_id_table({}) => {},{}'.format(a,i,t))
                
                int_time = 'int_time' in str(self._describe_table(t))
                if isinstance(start_date, datetime.datetime):
                    start_date = date2str(start_date)
                    stop_date = date2str(stop_date)
                    
                tb, te = str2time(start_date),str2time(stop_date)
                b,e = (tb, te) if int_time else (
                        "'%s'" % start_date, "'%s'" % stop_date)
                    
                cols = ','.join(c for c in columns.split(',') 
                                if c.strip() in str(self.tables[t]))

                if 'data_time,' in cols:
                    cols = cols.replace('data_time,',
                        'CAST(UNIX_TIMESTAMP(data_time) AS %s),' % cast)

                tcol = 'int_time' if int_time else 'data_time'
                q = ('select %s from %s where '
                    'att_conf_id = %s and %s between %s and %s '
                    % (cols, t, i, tcol, b, e))
                
                if decimate is True:
                    # decimation set to limit buffer size to 1080p (plotting)
                    decimate = int((te-tb)/1080.)
                    
                if decimate:
                    decimate = int(decimate)
                    q += ' and value_r is not NULL group by '
                    if int_time:
                        q += '(%s DIV %d)' % ('int_time', decimate)
                    else:
                        q += '(FLOOR(%s/%d))' % (
                            'UNIX_TIMESTAMP(data_time)', decimate)
                    if 'array' in t:
                        q += ',idx'
                        
                q += ' order by %s_time' % ('data','int')[int_time]
                    
                #print(q)
                data[a] = self._query(q, prune=decimate)
                #print('obtained data: {}'.format(len(data[a]),'L'))
            except:
                import traceback
                traceback.print_exc()
                data[a] = []

        return data        
        
        return {'attr0': [(time.time(), 0., 0., 0, '')]
                , 'attr1': [(time.time(), 0., 0., 0, '')]}
    
    
##############################################################################
           
if __name__ == '__main__':
    abstract.main(apiclass=MariadbReader,timeformatter=time2str)
    
