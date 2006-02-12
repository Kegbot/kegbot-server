{* no line breaks because of MSIE shittiness (adds extra space and screws up border) *}
<div style="border:{$border}px solid black; width:{$d}; height:{$d};{$extra}">{if $href}<a href="{$href}">{/if}<img border="0" width="{$d}" height="{$d}" src="{module_url module="images" image=$u->getMugshotFilename()}">{if $href}</a>{/if}</div>
