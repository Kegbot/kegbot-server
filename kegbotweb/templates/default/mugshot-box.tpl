{* no line breaks because of MSIE shittiness (adds extra space and screws up border) *}
<div style="border:{$border}px solid black; width:{$d}; height:{$d};">{if $href}<a href="{$href}"><img border="0" width="{$d}" height="{$d}" src="{$u->getMugshotURL()}"></a>{else}<img border="0" width="{$d}" height="{$d}" src="{$u->getMugshotURL()}">{/if}</div>
