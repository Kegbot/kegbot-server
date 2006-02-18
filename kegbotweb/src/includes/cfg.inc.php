<?
global $cfg;
$cfg['db']['host'] = 'localhost';
$cfg['db']['user'] = 'root';
$cfg['db']['password'] = '';
$cfg['db']['db'] = 'kegbot2';

$cfg['flow']['minticks'] = 2;

$cfg['urls']['baseurl'] = "/kegbotweb/src";
$cfg['dirs']['webdir'] = "/var/www/localhost/htdocs/kegbotweb/src";
$cfg['dirs']['skindir'] = "/var/www/localhost/htdocs/kegbotweb/skins";
$cfg['dirs']['smartytmp'] = "/var/www/localhost/htdocs/kegbotweb/smartytmp";

$cfg['dirs']['imagedir'] = $cfg['dirs']['webdir'] . '/userpics';

$cfg['graph']['imgdir'] = $cfg['dirs']['webdir'] . '/graphs/img';
$cfg['graph']['scriptdir'] = $cfg['dirs']['webdir'] . '/graphs';
$cfg['graph']['datadir'] = $cfg['dirs']['webdir'] . '/graphs';
$cfg['graph']['imgurl'] = '/graphs/img';
$cfg['graph']['cmd'] = 'ploticus';

$cfg['smarty']['cachetime'] = 600;

$cfg['edition'] = 'default';

// locale stuff... TODO organize me
putenv("TZ=US/Pacific");
setlocale(LC_MONETARY, 'en_US');
$cfg['timezone'] = 'PDT';
?>
