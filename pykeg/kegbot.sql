-- MySQL dump 9.11
--
-- Description: this is a dump of the kegbot database schema as of 6/12/2005.
-- this will likely change down the road.

--
-- Table structure for table `beerinfo`
--

CREATE TABLE `beerinfo` (
  `id` smallint(5) unsigned NOT NULL default '0',
  `abv` float NOT NULL default '0',
  `calories_oz` float NOT NULL default '0',
  `carbs_oz` float NOT NULL default '0'
) TYPE=MyISAM;

--
-- Table structure for table `billing`
--

CREATE TABLE `billing` (
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
) TYPE=MyISAM;

--
-- Table structure for table `drinks`
--

CREATE TABLE `drinks` (
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
) TYPE=MyISAM;

--
-- Table structure for table `generic_cache`
--

CREATE TABLE `generic_cache` (
  `name` varchar(32) default NULL,
  `value` varchar(32) default NULL,
  UNIQUE KEY `name_2` (`name`),
  KEY `name` (`name`)
) TYPE=MyISAM;

--
-- Table structure for table `grants`
--

CREATE TABLE `grants` (
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
) TYPE=MyISAM;

--
-- Table structure for table `kegs`
--

CREATE TABLE `kegs` (
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
) TYPE=MyISAM COMMENT='listing of keg information';

--
-- Table structure for table `logging`
--

CREATE TABLE `logging` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `logtime` timestamp(14) NOT NULL,
  `name` text NOT NULL,
  `lvl` tinyint(2) NOT NULL default '0',
  `pathname` text NOT NULL,
  `lineno` int(10) unsigned NOT NULL default '0',
  `msg` text NOT NULL,
  `exc_info` text NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Table structure for table `policies`
--

CREATE TABLE `policies` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `type` enum('fixed-cost','free') NOT NULL default 'fixed-cost',
  `unitcost` float NOT NULL default '0',
  `unitounces` float NOT NULL default '0',
  `description` text NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Table structure for table `thermolog`
--

CREATE TABLE `thermolog` (
  `rectime` bigint(20) NOT NULL default '0',
  `sensor` tinyint(2) unsigned NOT NULL default '0',
  `temp` float NOT NULL default '0',
  `fridgestatus` tinyint(1) NOT NULL default '0'
) TYPE=MyISAM MAX_ROWS=1000;

--
-- Table structure for table `tokens`
--

CREATE TABLE `tokens` (
  `id` mediumint(8) unsigned NOT NULL auto_increment,
  `ownerid` mediumint(8) unsigned NOT NULL default '0',
  `keyinfo` text NOT NULL,
  `created` timestamp(14) NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM PACK_KEYS=0;

--
-- Table structure for table `user_cache`
--

CREATE TABLE `user_cache` (
  `id` mediumint(8) unsigned NOT NULL default '0',
  `username` varchar(32) NOT NULL default '',
  `totaldrinks` int(10) unsigned NOT NULL default '0',
  `totaloz` float NOT NULL default '0',
  `kegdrinks` int(11) unsigned NOT NULL default '0',
  `kegoz` float NOT NULL default '0',
  `totaldrinkers` int(11) NOT NULL default '0',
  `maxBAC` float NOT NULL default '0',
  `lastdrink` bigint(20) NOT NULL default '0',
  `starttime` bigint(20) NOT NULL default '92233720368547758',
  `totaltime` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `uid` (`id`),
  KEY `uid_2` (`id`)
) TYPE=MyISAM COMMENT='Generic Cache';

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
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
) TYPE=MyISAM;

--
-- Table structure for table `wall`
--

CREATE TABLE `wall` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `user_id` bigint(20) unsigned NOT NULL default '0',
  `postdate` bigint(20) NOT NULL default '0',
  `message` text NOT NULL,
  `bac` float NOT NULL default '0',
  UNIQUE KEY `id` (`id`)
) TYPE=MyISAM;

