import './device_policies.css'
import 'flowbite'

document.addEventListener("DOMContentLoaded", function () {
    //const saveBtn = document.getElementById("saveBtn");
    const editBtn = document.getElementById("editBtn");
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    const tableRows = document.querySelectorAll("#policyTable > tbody > tr");
    const inactiveCols = document.querySelectorAll("#policyTable > thead > tr > th.inactive-col");
    const containerRight = document.getElementById("container-right");
    const successMsg = document.getElementById("successMsg");
    const errorMsg = document.getElementById("errorMsg");
    let radioClicked = false;

    const saveBtn = document.createElement("button");
    saveBtn.className = "focus:outline-none text-white accent-2-space-cadet-light hover:accent-2-space-cadet focus:ring-4 focus:ring-base-french-gray font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:focus:ring-yellow-900"
    saveBtn.innerhtml = "Save Changes";

    saveBtn.addEventListener("click", function () {
        if (radioClicked) {
            const data = getTableData();
            sendPOSTRequest(data);
        }
        radioClicked = false;
        editBtn.style.display = "block";
        radioButtons.forEach(function (radio) {
            radio.disabled = true;
        });
    });

    function getTableData() {
        const data = [];

        tableRows.forEach(function (row) {
            const id = row.dataset.policyId;
            const domain = row.cells[0].innerText;
            const radioAllow = row.querySelector('input[value="allow"]');
            const radioBlock = row.querySelector('input[value="block"]');
            const hasCheckedRadio = radioAllow.checked || radioBlock.checked;
            let type = null
            let confirmed = null
            if (hasCheckedRadio) {
                type = radioAllow.checked ? "allow" : "block";
                confirmed = true;
            } else {
                type = row.parentNode.dataset.defaultPolicy;
                confirmed = false;
            }

            data.push({
                id: id,
                domain: domain,
                type: type,
                confirmed: confirmed
            });
        });

        return data;
    }

    async function sendPOSTRequest(data) {
        try {
            const response = await fetch(window.current_endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            if (response.redirected) {
                window.location = response.url;
                successMsg.className = "success-msg block";
            } else {
                throw new Error(`Redirect failed! status: ${response.status}`);
            }
            console.log("Changes saved successfully!");
        } catch (error) {
            console.error(error);
            errorMsg.className = "error-msg block";
        }
    }


    // Add event listener to radio buttons to set the boolean to true when clicked
    radioButtons.forEach(function (radio) {
        radio.addEventListener("change", function () {
            radioClicked = true;
        });
    });

    // Initially disable radio buttons and hide the "Save Changes" button
    radioButtons.forEach(function (radio) {
        radio.disabled = true;
    });
    saveBtn.style.display = "none";

    // Add event listener to "Edit" button
    editBtn.addEventListener("click", function () {
        radioClicked = false; // Reset the boolean when "Edit" is clicked
        radioButtons.forEach(function (radio) {
            radio.disabled = false;
        });
        inactiveCols.forEach(function (col) {
            col.className = "px-6 py-3 active-col";
        });
        replaceEditBtn()
    });

    function replaceEditBtn() {
        const editBtn = document.getElementById("editBtn");
        const editBtnParent = editBtn.parentNode;
        editBtnParent.replaceChild(saveBtn, editBtn);
    }
});
