<tr>
   <td><a href="edit-token.php?id={$token->id}">{$token->keyinfo}</a>&nbsp;&nbsp;&nbsp;</td>
   <td><a href="edit-user.php?u={$token->ownerid}">{$token->getOwnerName()}&nbsp;&nbsp;&nbsp;</a></td>
   <td>{$token->created|date_format:"%b %e %Y, %r"}</td>
</tr>
