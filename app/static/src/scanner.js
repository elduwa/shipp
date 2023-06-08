document.addEventListener("DOMContentLoaded", function() {
  const table = document.getElementById("myTable");
  const editButton = document.getElementById("editButton");
  const scanButton = document.getElementById("scanButton");
  const confirmButton = document.getElementById("confirmButton");
  const formOverlay = document.querySelector(".form-overlay");
  const formContainer = document.querySelector(".form-container");

  let tableData = [];

  table.addEventListener("click", function(event) {
    // Handle row selection logic
  });

  editButton.addEventListener("click", function() {
    // Handle edit button click logic
  });

  scanButton.addEventListener("click", function() {
    // Perform network scanning logic
    fetch("/scan_network", { method: "POST" })
      .then(response => response.json())
      .then(data => {
        // Update the table with the scanned data
        tableData = data.table_data;
        renderTable(tableData);
      })
      .catch(error => {
        console.log("Network scanning error:", error);
      });
  });

  confirmButton.addEventListener("click", function() {
    // Send the updated table data to the backend
    const formData = {
      table_data: tableData
    };

    fetch("/update_table", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(formData)
    })
      .then(response => {
        if (response.ok) {
          console.log("Table data updated successfully.");
          // Perform any additional actions upon successful update
        } else {
          console.log("Failed to update table data.");
        }
      })
      .catch(error => {
        console.log("Update table data error:", error);
      });
  });

  function renderTable(data) {
    const tableBody = table.querySelector("tbody");
    tableBody.innerHTML = "";
    data.forEach(rowData => {
      const row = document.createElement("tr");
      Object.values(rowData).forEach(value => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      });
      tableBody.appendChild(row);
    });
  }

  // Handle form submission logic
});
