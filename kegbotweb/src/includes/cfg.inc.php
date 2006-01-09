<?
$cfg['db']['host'] = 'localhost';
$cfg['db']['user'] = 'kegbot';
$cfg['db']['password'] = '';
$cfg['db']['db'] = 'kegbot';

$cfg['flow']['minticks'] = 2;

$cfg['dirs']['webdir'] = "/data/kegbot-beta/htdocs";
$cfg['dirs']['skindir'] = "/data/kegbot-beta/skins";
$cfg['dirs']['smartytmp'] = "/data/kegbot-beta/smartytmp";

$cfg['dirs']['imagedir'] = $cfg['dirs']['webdir'] . '/userpics';

$cfg['graph']['imgdir'] = $cfg['dirs']['webdir'] . '/graphs/img';
$cfg['graph']['scriptdir'] = $cfg['dirs']['webdir'] . '/graphs';
$cfg['graph']['datadir'] = $cfg['dirs']['webdir'] . '/graphs';
$cfg['graph']['imgurl'] = '/graphs/img';
$cfg['graph']['cmd'] = 'ploticus';

$cfg['smarty']['cachetime'] = 600;

$cfg['edition'] = 'default';

putenv("TZ=US/Pacific");
$cfg['timezone'] = 'PDT';
?>
