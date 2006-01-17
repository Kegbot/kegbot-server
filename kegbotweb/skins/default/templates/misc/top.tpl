<html>
<head>
   {if $refresh}
   <META HTTP-EQUIV=Refresh CONTENT="10; URL=leaders.php?r=1">
   {/if}
   <title>kegbot kegerator</title>
   <style type="text/css" media="all">@import "{$css}";</style>
</head>
<body>
   {include file="boxes/top5.tpl"}
   <div class="mainheader">
      <p>
         <font size="+2" color="#ffffff"><b>kegbot beer device...</b> beer me!</font>
      </p>
      <div class="linkbar">
         <div style="padding-left:30px;">
         <a href="{module_url module="main"}">main</a> |
         <a href="{module_url module="all-drinkers"}">drinkers</a> |
         <a href="{module_url module="leaders"}">leader board</a> |
         <a href="{module_url module="account"}">account</a>
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
