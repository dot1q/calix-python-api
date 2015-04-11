<?php
#THIS SCRIPT IS DESIGNED TO START OR STOP SERVICE FOR A PARTICULAR ONT, BY TAKING IN THE FSAN


#Python execute function
function executeScript($serial, $value) {
   echo "Executing script...<br />";
   $command = escapeshellcmd('python ../services-ont.py Ont '.$serial.' '.$value);
   $output = shell_exec($command);
   echo $output;


}

$serial = "000000";
	if(isset($_GET['serial'])) {
	   $serial = $_GET['serial'];
	   if((isset($_GET['state'])) and ($_GET['state'] == '0')){
	      $state = 0;
	   }else{
	      $state = 1;
	   }
	   echo("Serial was obtained via GET! ".$serial."<br />");
	   echo("State is: ".$state."<br />");
	   echo("<hr>");
	   executeScript($serial, $state);
	}else{
	   echo("Serial was not found via GET<br />");
?>
	   <form action="" method="get">
	      Serial: <input type="text" name="serial"><br>
	      Suspend: <input type="checkbox" name="state" value="0" /><br>
	      <input type="submit">
	   </form>
<?php
	}
?>
