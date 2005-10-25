<tr>
   <td><a href="{$drink->infoURL()}">{$drink->id}</a></td>
   <td align="right">{$drink->getSize()|string_format:"%.1f"}&nbsp;</td> <td>ounces</td>
   <td>{$drink->endtime|rel_date|lower}</td>
   <td>{$drink->bac|string_format:"%.3f"}</td>
</tr>
