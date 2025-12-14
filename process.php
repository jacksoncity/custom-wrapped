<?php
// Check if the form was submitted by checking if the submit button's name is set
if (isset($_POST['wrappedSubmit'])) {
    // Get the value of the submit button
    $submitValue = $_POST['wrappedSubmit'];
    

    // // You can also access other form fields
    // $username = $_POST['username'];
    // echo "<br>Username entered: " . htmlspecialchars($username);
} else {
    echo "Form was not submitted.";
}
