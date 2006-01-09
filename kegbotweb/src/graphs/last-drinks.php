<?
require('jpgraph.php');
require('jpgraph_line.php');

$graph = new Graph(300,300,"auto");
$graph->SetScale("linlin");
$graph->img->SetImgFormat("jpeg");

$graph->Stroke();
?>
