<?php
#THIS SCRIPT IS DESIGNED TO START OR STOP SERVICE FOR A PARTICULAR ONT, BY TAKING IN THE FSAN


#Python execute function
function executeScript($serial) {
   echo "Executing script";
   $command = escapeshellcmd('../service-ont.py');
   $output = shell_exec($command);
   echo $output;


}

$serial = "000000";
	if(isset($_GET['serial'])) {
	   $serial = $_GET['serial'];
	   echo("Serial was obtained via GET! ".$serial);
	   echo("<hr>");
	   executeScript($serial);
	}else{
	   echo("Serial was not found via GET: ".$serial);
?>
	   <form action="" method="get">
	      Serial: <input type="text" name="serial"><br>
	      <input type="submit">
	   </form>
<?php
	}
?>
