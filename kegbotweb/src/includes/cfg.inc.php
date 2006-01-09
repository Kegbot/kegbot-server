<?
$cfg['db']['host'] = 'localhost';
$cfg['db']['user'] = 'kegbot';
$cfg['db']['password'] = '';
$cfg['db']['db'] = 'kegbot';

$cfg['flow']['minticks'] = 2;

$cfg['graph']['imgdir'] = '/data/kegbot/htdocs/graphs/img';
$cfg['graph']['scriptdir'] = '/data/kegbot/htdocs/graphs';
$cfg['graph']['datadir'] = '/data/kegbot/htdocs/graphs';
$cfg['graph']['imgurl'] = '/graphs/img';
$cfg['graph']['cmd'] = 'ploticus';

$cfg['smarty']['basedir'] = "/data/kegbot/kegbot-smarty";
$cfg['smarty']['cachetime'] = 600;
$cfg['dirs']['imagedir'] = "/data/kegbot/htdocs/userpics";

$cfg['edition'] = 'default';

putenv("TZ=US/Pacific");
$cfg['timezone'] = 'PDT';
?>
