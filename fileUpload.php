<?php

  $file_path = "uploads/";
  $data = file_get_contents($_FILES['uploaded_file']['tmp_name']);

  $imageFile = imagecreatefromstring($data);
  $imagePath = "uploads/camera.png";
  $imageSave = imagepng($imageFile, $imagePath); 
  
  $output = array();
  exec("python3 sudoku.py ".$imagePath, $output);
  $solution = array();
  exec("python solver.py ".$output[0], $solution);

  echo $solution[0];
?>



