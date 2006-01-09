<div class="box" style="margin-bottom: 5px;">
<table border="0" cellspacing="0" cellpadding="3">
   <tr>
      <td rowspan="2" valign="top">
         {include file="mugshot-box.tpl" u=$tag->drinker_obj d=32 href="/drinker/`$tag->drinker_obj->username`"}
      </td>
      <td height="20">
         <font size="-2">&nbsp;</font><b>{$tag->message}</b>
      </td>
   </tr>
   <tr>
      <td width="100%" align="right">
         <font size="-2">&nbsp;{$tag->postdate|rel_date|lower} / {$tag->bac|string_format:"%.3f"}% alcohol</font>
      </td>
   </tr>
</table>
</div>
