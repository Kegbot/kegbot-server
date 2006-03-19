<div class="contenthead">
   the liquor cabinet
</div>
<div class="content">
   <p>
      hello, {$drinker->username}! welcome to the liquor cabinet. (<a href="{module_url module="login" action="logout"}">logout</a>)
   </p>
   {if $oneshot_msg}
   <p>
      <b>{$oneshot_msg}</b>
   </p>
   {/if}
</div>

<div class="contenthead">
   change password
</div>
<div class="content">
   <p>
      <table>
         <form method="post" action="{module_url module="change-password"}">
         <input type="hidden" name="action" value="login">
         <tr>
            <td><b>new password:</b></td>
            <td><input type="password" name="newpass" size="20"></td>
         </tr>
         <tr>
            <td><b>again:</b></td>
            <td><input type="password" name="confirm" size="20"></td>
         </tr>
         <tr>
            <td>&nbsp;</td>
            <td><input type="submit" name="submit"></td>
         </tr>
         </form>
      </table>
   </p>
</div>

<div class="contenthead">
   drinker bio
</div>
<div class="content">
   <form method="post" action="{module_url module="update-account"}">
   <p>
      please be sure that your gender and weight are generally accurate. both
      are used solely for calculating your BAC, so the more accurate you are,
      the more accurate we can caluclate it. your weight will not be visible to
      anyone else.
   </p>
   <p>
      <input type="hidden" name="action" value="update">
      <table border="0" cellpadding="3">
      {if $DISABLED}
         <tr>
            <td align="right" valign="center"><b>drinking name:</b></td>
            <td>
               <input type="text" size="30" name="username" value="{$drinker->username}">
            </td>
         </tr>
      {else}
               <input type="hidden" name="username" value="{$drinker->username}">
         {/if}
         <tr>
            <td align="right" valign="center"><b>weight:</b></td>
            <td>
               <input type="text" size="4" name="weight" value="{$drinker->weight}"> pounds
            </td>
         </tr>
         <tr>
            <td align="right" valign="center"><b>gender:</b></td>
            <td>
               {html_options name="gender" values=$genders output=$genders selected=$drinker->gender}
            </td>
         </tr>
         <tr>
            <td>&nbsp;</td>
            <td><input type="submit" name="submit" value="update"></td>
         </tr>
      </table>
      </form>
   </p>
</div>
<div class="contenthead">
   account balance
</div>
<div class="content">
   <p>
      your account balance is shown below. this is a listing of all charges you
      have made on this account, along with any credits (cash paid, and so on).
      depending on the mood of the kegbot, a larger outstanding balance here
      may negatively affect your ability to get beer -- best to keep the kegbot
      happy!
   </p>
   <p>
      <div class="box">
      <table cellspacing=0 border=0 width="430">
      <tr>
         <td><b>name</b></td>
         <td><b>cost</b></td>
      </tr>
      {foreach name=bills item="charge" from=$charges}
         <tr >
         { include file="spans/charge.tpl"}
         </tr>
         <tr>
      {/foreach}
         <td colspan="3">
            <B>TOTAL:</b> {$balance|money_fmt}
         </td>
      </table>
      </div>
   </p>
</div>
<div class="contenthead">
   summary of permissions
</div>
<div class="content">
   <p>
      below, you may view your capabilities to drink beer, and the cost for
      doing so. when you pour a beer, the kegerator will always select the
      cheapest way to get you that beer.
   </p>
   <p>
      <div class="box">
      <table cellspacing=0 border=0 width="430">
      <tr>
         <td><b>description</b></td>
         <td><b>cost/oz</b></td>
         <td><b>expires</b></td>
         <td><b>to go</b></td>
      </tr>
      {foreach name=grants item="grant" from=$grants}
         <tr>
         { include file="spans/grant.tpl" grant=$grant}
         </tr>
      {/foreach}
      </table>
      </div>
   </p>
</div>

<div class="contenthead">
   mug shot
</div>
<div class="content">
   <p>
      be sure to keep a wild picture of your drinking face handy. please upload
      one here.
   </p>

   <p>
      <b>note:</b> make sure your picture is a <b>square</b>, around 160x160
      pixels. (larger, but not too much larger, won't hurt.)
   </p>
   <p>
      you are strongly encouraged to use your real likeness here.
   </p>
   <form enctype="multipart/form-data" action="/upload-mug.php" method="post">
   <p>
   <div class="box">
   <table>
   <tr>
      <td valign="top">
         <input type="hidden" name="slot" value="1" />
         <input type="hidden" name="MAX_FILE_SIZE" value="200000" />
         <input name="userfile" type="file" /><br>
         <input type="submit" value="Send File" />
      </td>
      <td>
         <b>current:</b><br>
         { include file="boxes/mugshot-box.tpl" u=$drinker d=128}
      </td>
   </table>
   </div>
   </p>
   </form>
</div>
<div class="contenthead">
   post a tag
</div>
<div class="content">
   <p>
      quick message, probably to announce that you are drunk.
   </p>
   <form method="post" action="post-tag.php">
   <p>
   <b>message:</b><input type="text" name="message" size="50" maxlength="50"><input type="submit" value="tag">
   </p>
   </form>
</div>
