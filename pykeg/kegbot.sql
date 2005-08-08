-- KEGBOT_SCHEMA_VERSION=1
-- NOTE: do not modify the above line

-- 
-- Table structure for table `beerinfo`
-- 

CREATE TABLE IF NOT EXISTS `beerinfo` (
  `id` smallint(5) unsigned NOT NULL default '0',
  `abv` float NOT NULL default '0',
  `calories_oz` float NOT NULL default '0',
  `carbs_oz` float NOT NULL default '0'
) TYPE=MyISAM;

-- 
-- Dumping data for table `beerinfo`
-- 


-- --------------------------------------------------------

-- 
-- Table structure for table `billing`
-- 

CREATE TABLE IF NOT EXISTS `billing` (
  `id` mediumint(9) NOT NULL auto_increment,
  `foruid` mediumint(9) NOT NULL default '0',
  `date` bigint(20) NOT NULL default '0',
  `type` enum('charge','credit') NOT NULL default 'charge',
  `subtype` enum('cash','gift','membership','correction') NOT NULL default 'cash',
  `amount` float NOT NULL default '0',
  `name` tinytext NOT NULL,
  `descr` mediumtext NOT NULL,
  `mandatory` enum('no','yes') NOT NULL default 'no',
  UNIQUE KEY `id` (`id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- 
-- Dumping data for table `billing`
-- 


-- --------------------------------------------------------

-- 
-- Table structure for table `config`
-- 

CREATE TABLE IF NOT EXISTS `config` (
  `key` varchar(64) NOT NULL default '',
  `value` mediumtext NOT NULL,
  UNIQUE KEY `key` (`key`)
) TYPE=MyISAM COMMENT='kegbot master config';

-- 
-- Dumping data for table `config`
-- 

INSERT INTO `config` VALUES ('logging.logformat', '%(asctime)s %(levelname)s %(message)s');
INSERT INTO `config` VALUES ('logging.logfile', 'keg.log');
INSERT INTO `config` VALUES ('logging.use_sql', 'false');
INSERT INTO `config` VALUES ('logging.logtable', 'logging');
INSERT INTO `config` VALUES ('logging.use_logfile', 'true');
INSERT INTO `config` VALUES ('logging.use_stream', 'true');
INSERT INTO `config` VALUES ('flow.tick_skew', '1.0');
INSERT INTO `config` VALUES ('flow.polltime', '0.3');
INSERT INTO `config` VALUES ('flow.tick_metric', '2200');
INSERT INTO `config` VALUES ('bot.typerate', '0.05');
INSERT INTO `config` VALUES ('bot.startup_command', 'load aiml b');
INSERT INTO `config` VALUES ('bot.startup_file', 'beer-startup.xml');
INSERT INTO `config` VALUES ('bot.do_save_brain', 'true');
INSERT INTO `config` VALUES ('bot.save_brain', 'beer.brn');
INSERT INTO `config` VALUES ('bot.defaults', 'beertender.cfg');
INSERT INTO `config` VALUES ('devices.lcd', '/dev/lcd');
INSERT INTO `config` VALUES ('devices.onewire', '/dev/onewire');
INSERT INTO `config` VALUES ('devices.thermo', '/dev/thermo');
INSERT INTO `config` VALUES ('devices.flow', '/dev/flow');
INSERT INTO `config` VALUES ('aim.profile', 'please don''t ask me to beer you.');
INSERT INTO `config` VALUES ('aim.use_aim', 'false');
INSERT INTO `config` VALUES ('aim.password', 'pass');
INSERT INTO `config` VALUES ('aim.screenname', 'botname');
INSERT INTO `config` VALUES ('ui.keypad_pipe', '/dev/input/event0');
INSERT INTO `config` VALUES ('ui.use_lcd', 'true');
INSERT INTO `config` VALUES ('ui.translation_file', 'keymap.cfg');
INSERT INTO `config` VALUES ('ui.lcd_model', 'lk204-25');
INSERT INTO `config` VALUES ('timing.ib_idle_min_disconnected', '5');
INSERT INTO `config` VALUES ('timing.ib_missing_ceiling', '3.0');
INSERT INTO `config` VALUES ('timing.freezer_event_min', '60');
INSERT INTO `config` VALUES ('timing.ib_refresh_timeout', '0.75');
INSERT INTO `config` VALUES ('timing.fc_status_timeout', '0.1');
INSERT INTO `config` VALUES ('timing.ib_idle_timeout', '60');
INSERT INTO `config` VALUES ('timing.ib_verify_timeout', '0.1');
INSERT INTO `config` VALUES ('sounds.sound_dir', '/home/kegbot/svnbox/pykeg/sounds/');
INSERT INTO `config` VALUES ('sounds.use_sounds', 'false');
INSERT INTO `config` VALUES ('thermo.use_thermo', 'false');
INSERT INTO `config` VALUES ('thermo.logging_timeout', '30.0');
INSERT INTO `config` VALUES ('thermo.temp_max_low', '2.0');
INSERT INTO `config` VALUES ('thermo.main_sensor', '1');
INSERT INTO `config` VALUES ('thermo.temp_max_high', '4.5');
INSERT INTO `config` VALUES ('db.schema_version', '1');

-- --------------------------------------------------------

-- 
-- Table structure for table `drinks`
-- 

CREATE TABLE IF NOT EXISTS `drinks` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `frag` tinyint(4) NOT NULL default '0',
  `ticks` mediumint(8) unsigned NOT NULL default '0',
  `totalticks` mediumint(9) NOT NULL default '0',
  `starttime` bigint(20) default NULL,
  `endtime` bigint(20) default NULL,
  `bac` float NOT NULL default '0',
  `user_id` mediumint(8) unsigned NOT NULL default '0',
  `keg_id` int(10) unsigned NOT NULL default '0',
  `grant_id` int(10) unsigned NOT NULL default '0',
  `status` enum('valid','invalid') NOT NULL default 'valid',
  PRIMARY KEY  (`id`,`frag`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- 
-- Dumping data for table `drinks`
-- 


-- --------------------------------------------------------

-- 
-- Table structure for table `grants`
-- 

CREATE TABLE IF NOT EXISTS `grants` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `foruid` int(10) unsigned NOT NULL default '0',
  `expiration` enum('none','time','ounces','drinks') NOT NULL default 'none',
  `status` enum('active','expired','deleted') NOT NULL default 'active',
  `forpolicy` int(10) unsigned NOT NULL default '0',
  `exp_ounces` float unsigned NOT NULL default '0',
  `exp_time` bigint(20) NOT NULL default '0',
  `exp_drinks` tinyint(3) unsigned NOT NULL default '0',
  `total_ounces` float unsigned NOT NULL default '0',
  `total_drinks` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM AUTO_INCREMENT=3 ;

-- 
-- Dumping data for table `grants`
-- 

INSERT INTO `grants` VALUES (1, 1, 'none', 'active', 1, 0, 0, 0, 0, 0);
INSERT INTO `grants` VALUES (2, 2, 'none', 'active', 1, 0, 0, 0, 0, 0);

-- --------------------------------------------------------

-- 
-- Table structure for table `kegs`
-- 

CREATE TABLE IF NOT EXISTS `kegs` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `tickmetric` float NOT NULL default '38.75',
  `startounces` float NOT NULL default '1984',
  `startdate` datetime NOT NULL default '0000-00-00 00:00:00',
  `enddate` datetime NOT NULL default '0000-00-00 00:00:00',
  `status` enum('online','offline','coming soon') NOT NULL default 'online',
  `beername` text NOT NULL,
  `alccontent` float NOT NULL default '5',
  `description` text NOT NULL,
  `origcost` float NOT NULL default '0',
  `beerpalid` int(10) unsigned NOT NULL default '0',
  `ratebeerid` int(11) NOT NULL default '0',
  `calories_oz` float NOT NULL default '0',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM COMMENT='listing of keg information' AUTO_INCREMENT=1 ;

-- 
-- Dumping data for table `kegs`
-- 


-- --------------------------------------------------------

-- 
-- Table structure for table `logging`
-- 

CREATE TABLE IF NOT EXISTS `logging` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `logtime` timestamp(14) NOT NULL,
  `name` text NOT NULL,
  `lvl` tinyint(2) NOT NULL default '0',
  `pathname` text NOT NULL,
  `lineno` int(10) unsigned NOT NULL default '0',
  `msg` text NOT NULL,
  `exc_info` text NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- 
-- Dumping data for table `logging`
-- 


-- --------------------------------------------------------

-- 
-- Table structure for table `policies`
-- 

CREATE TABLE IF NOT EXISTS `policies` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `type` enum('fixed-cost','free') NOT NULL default 'fixed-cost',
  `unitcost` float NOT NULL default '0',
  `unitounces` float NOT NULL default '0',
  `description` text NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM AUTO_INCREMENT=2 ;

-- 
-- Dumping data for table `policies`
-- 

INSERT INTO `policies` VALUES (1, 'free', 0, 1, '');

-- --------------------------------------------------------

-- 
-- Table structure for table `thermolog`
-- 

CREATE TABLE IF NOT EXISTS `thermolog` (
  `rectime` bigint(20) NOT NULL default '0',
  `sensor` tinyint(2) unsigned NOT NULL default '0',
  `temp` float NOT NULL default '0',
  `fridgestatus` tinyint(1) NOT NULL default '0'
) TYPE=MyISAM MAX_ROWS=1000;

-- 
-- Dumping data for table `thermolog`
-- 


-- --------------------------------------------------------

-- 
-- Table structure for table `tokens`
-- 

CREATE TABLE IF NOT EXISTS `tokens` (
  `id` mediumint(8) unsigned NOT NULL auto_increment,
  `ownerid` mediumint(8) unsigned NOT NULL default '0',
  `keyinfo` text NOT NULL,
  `created` timestamp(14) NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM PACK_KEYS=0 AUTO_INCREMENT=2 ;

-- 
-- Dumping data for table `tokens`
-- 

INSERT INTO `tokens` VALUES (1, 2, '1D00000991BAA201', '20040601000000');

-- --------------------------------------------------------

-- 
-- Table structure for table `users`
-- 

CREATE TABLE IF NOT EXISTS `users` (
  `id` mediumint(8) unsigned NOT NULL auto_increment,
  `username` varchar(32) NOT NULL default '',
  `email` text NOT NULL,
  `im_aim` text NOT NULL,
  `admin` enum('no','yes') NOT NULL default 'no',
  `password` text NOT NULL,
  `gender` enum('male','female') NOT NULL default 'male',
  `weight` float NOT NULL default '0',
  `image_url` mediumtext NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `uid_2` (`id`),
  KEY `uid` (`id`)
) TYPE=MyISAM AUTO_INCREMENT=3 ;

-- 
-- Dumping data for table `users`
-- 

INSERT INTO `users` VALUES (1, 'admin', '', '', 'yes', '9c48f5613d775e190b7fdfbaff821f50', 'male', 185, '');
INSERT INTO `users` VALUES (2, 'mikey', 'mike@kegbot.org', '', 'no', 'f76172be594f4ac604a84cfda1f2d064', 'male', 185, '');

-- --------------------------------------------------------

-- 
-- Table structure for table `wall`
-- 

CREATE TABLE IF NOT EXISTS `wall` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `user_id` bigint(20) unsigned NOT NULL default '0',
  `postdate` bigint(20) NOT NULL default '0',
  `message` text NOT NULL,
  `bac` float NOT NULL default '0',
  UNIQUE KEY `id` (`id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- 
-- Dumping data for table `wall`
-- 


