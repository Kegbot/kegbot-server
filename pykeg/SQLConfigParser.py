from ConfigParser import RawConfigParser

class SQLConfigParser(RawConfigParser):
   """ A RawConfigParser that reads from SQL using a MySQLdb connection """

   def read(self, dbconn, table):
      q = """SELECT `key`,`value` FROM `%s` """ % (table,)
      c = dbconn.cursor()
      c.execute(q)

      for k, v in c.fetchall():
         section, optname = k.split('.')
         optname = self.optionxform(optname)
         if not self._sections.has_key(section):
            self._sections[section] = {'__name__': section}
         self._sections[section][optname] = v

class SQLObjectConfigParser(RawConfigParser):
   """ A RawConfigParser that reads from SQL using an SQLObject class"""

   def read(self, cls):
      for row in cls.select():
         k, v = row.id, row.value
         section, optname = k.split('.')
         optname = self.optionxform(optname)
         if not self._sections.has_key(section):
            self._sections[section] = {'__name__': section}
         self._sections[section][optname] = v

