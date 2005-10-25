<html>
<head>
   {if $refresh}
   <META HTTP-EQUIV=Refresh CONTENT="10; URL=leaders2.php">
   {/if}
   <title>kegbot online</title>
   <style type="text/css" media="all">@import "{$css}";</style>
</head>
<body> 
   <div class="mainheader">
      <p>
         <font size="+2"><b>kegBot: live stats</b></font>
      </p>
      <div class="linkbar">
         <div style="padding-left:30px;">
         <a href="/">main</a> |
         <a href="/leaders2.php">leader board</a> |
         <a href="/account.php">account</a>
         { if $s_drinker->admin }
         | <a href="/admin-info.php">kebgot admin</a>
         { /if}
         { if $s_drinker }
         | <a href="/login.php?action=logout">logout</a>
         {/if}
      </div>
      </div>
   </div>
   <br>
