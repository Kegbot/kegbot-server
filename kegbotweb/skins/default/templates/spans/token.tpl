<tr>
   <td><a href="{module_url module="edit-token" id=$token->id}">{$token->keyinfo}</a>&nbsp;&nbsp;&nbsp;</td>
   <td><a href="{module_url module="edit-user" u=$token->owner_obj->id}">{$token->owner_obj->username}&nbsp;&nbsp;&nbsp;</a></td>
   <td>{$token->created|date_format:"%b %e %Y, %r"}</td>
</tr>
