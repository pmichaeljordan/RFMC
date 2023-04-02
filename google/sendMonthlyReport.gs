// trigger to send on first of month automatically, will send prior months hours with total
function sendMonthlyReport() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var currentDate = new Date();
  var lastMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
  var rowsToInclude = [];
  
  // Find all rows with a date in the previous month
  for (var i = 1; i < data.length; i++) { // Starting from row 2 to ignore header row
    var rowDate = new Date(data[i][1]); // Date is in the second column (column B)
    if (rowDate.getMonth() === lastMonth.getMonth() && rowDate.getFullYear() === currentDate.getFullYear()) {
      rowsToInclude.push(data[i]);
    }
  }
  
  // Format the data into an HTML table
  var tableHtml = "<p>Please find attached the monthly report for " + lastMonth.toLocaleString('default', { month: 'long', year: 'numeric' }) + ":</p>";
  tableHtml += "<table style='border-collapse: collapse;'>";
  tableHtml += "<tr><th style='border: 1px solid black; padding: 5px;'>Date</th><th style='border: 1px solid black; padding: 5px;'>Elapsed Time</th><th style='border: 1px solid black; padding: 5px;'>Description</th></tr>";
  for (var i = 0; i < rowsToInclude.length; i++) {
    var row = rowsToInclude[i];
    var elapsedTime = new Date(row[3] - row[2]).toUTCString().split(" ")[4];
    tableHtml += "<tr><td style='border: 1px solid black; padding: 5px;'>" + Utilities.formatDate(row[1], "GMT-5", "MMM dd yyyy") + "</td><td style='border: 1px solid black; padding: 5px;'>" + elapsedTime + "</td><td style='border: 1px solid black; padding: 5px;'>" + row[5] + "</td></tr>";
  }
  tableHtml += "</table>";
  
  // Create a CSV file with the same data
  var csv = "Date,Elapsed Time,Description\n";
  for (var i = 0; i < rowsToInclude.length; i++) {
    var row = rowsToInclude[i];
    var elapsedTime = new Date(row[3] - row[2]).toUTCString().split(" ")[4];
    csv += Utilities.formatDate(row[1], "GMT-5", "MMM dd yyyy") + "," + elapsedTime + "," + row[5] + "\n";
  }
  
  // Send the email with the HTML table and CSV file attached
  var recipients = "user@gmail.com"; // Replace with your recipient email addresses
  var subject = "USER - Monthly Volunteer Hours Report for " + lastMonth.toLocaleString('default', { month: 'long', year: 'numeric' });
  var attachments = [{fileName: "mike_jordan_report.csv", content: csv, mimeType: "text/csv"}];
  MailApp.sendEmail(recipients, subject, "", {htmlBody: tableHtml, attachments: attachments});
}