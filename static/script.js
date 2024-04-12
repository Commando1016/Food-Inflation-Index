function validateForm() {
    var startYear = document.getElementById("start").value;
    var endYear = document.getElementById("end").value;

    console.log(startYear);
    console.log(endYear);

    if (parseInt(endYear) <= parseInt(startYear)) {
        document.getElementById("endYearError").innerText = "End year must be after start year.";
        return false; // Prevent form submission
    }
    return true; // Allow form submission
}