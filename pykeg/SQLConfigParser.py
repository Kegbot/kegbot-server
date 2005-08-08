from ConfigParser import RawConfigParser

class SQLConfigParser(RawConfigParser):
   """ A RawConfigParser that reads from SQL """

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

