<tr>
   <td><a href="{module_url module="drink-info" drink=$drink->id}"><img border="0" src="images/info.png"></a></td>
   <td align="right">{$drink->getSize()|string_format:"%.1f"}&nbsp;</td> 
   <td>ounces</td>
   <td align="right">{$drink->getCalories()|string_format:"%.0f"}&nbsp;</td> 
   <td>cal&nbsp;</td>
   <td>{include file="misc/drinker-link.tpl drinker=$drink->drinker_obj}</td>
   <td>{$drink->endtime|rel_date|lower}</td>
   <td>{$drink->bac|string_format:"%.3f"|bac_format}</td>
</tr>
