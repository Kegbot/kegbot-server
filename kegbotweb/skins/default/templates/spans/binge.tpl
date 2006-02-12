<tr>
   <td>{$binge->id}</td>
   <td>{$binge->getSize()|string_format:"%.1f"}</td>
   <td>{$binge->starttime|rel_date}</td>
   <td>{$binge->endtime|rel_date}</td>
</tr>
