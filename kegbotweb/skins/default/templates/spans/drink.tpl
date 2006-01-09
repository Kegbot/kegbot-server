<tr>
   <td><a href="{$drink->infoURL()}"><img border="0" src="/images/info.png"></a></td>
   <td align="right">{$drink->getSize()|string_format:"%.1f"}&nbsp;</td> 
   <td>ounces</td>
   <td align="right">{$drink->getCalories()|string_format:"%.0f"}&nbsp;</td> 
   <td>cal&nbsp;</td>
   <td>{$drink->drinker_obj->getNameLinkified()}</td>
   <td>{$drink->endtime|rel_date|lower}</td>
   <td>{$drink->bac|string_format:"%.3f"|bac_format}</td>
</tr>
