import './device_policies.css'
import 'flowbite'

document.addEventListener("DOMContentLoaded", function () {
    //const saveBtn = document.getElementById("saveBtn");
    const editBtn = document.getElementById("editBtn");
    const cancelBtn = document.getElementById("cancelBtn");
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    const tableRows = document.querySelectorAll("#policyTable > tbody > tr");
    const successMsg = document.getElementById("successMsg");
    const errorMsg = document.getElementById("errorMsg");
    const lockContainer = document.getElementById('lock-container');
    const lockClosed = document.getElementById('lock-closed');
    const lockOpen = document.getElementById('lock-open');
    const select = document.getElementById("underline_select");

    let radioClicked = false;
    const editedPolicies = new Set();

    const saveBtn = document.createElement("button");
    saveBtn.className = "focus:outline-none text-white bg-accent-2-space-cadet-li hover:bg-accent-2-space-cadet focus:ring-4 focus:ring-base-french-gray font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:focus:ring-yellow-900"
    saveBtn.innerHTML = "Save Changes";

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

    // Add event listener to radio buttons to set the boolean to true when clicked
    radioButtons.forEach(function (radio) {
        radio.addEventListener("change", function () {
            radioClicked = true;
            editedPolicies.add(radio.parentNode.parentNode.dataset.policyId);
            console.log("Edited policy: " + radio.parentNode.parentNode.dataset.policyId);
        });
    });

    // Initially disable radio buttons and hide the "Save Changes" button
    radioButtons.forEach(function (radio) {
        radio.disabled = true;
    });

    function replaceEditBtn() {
        const editBtn = document.getElementById("editBtn");
        const editBtnParent = editBtn.parentNode;
        editBtnParent.replaceChild(saveBtn, editBtn);
    }

    function makeEditable() {
        toggleLockVisibility()
        radioClicked = false; // Reset the boolean when "Edit" is clicked
        console.log("Making radio buttons editable");
        radioButtons.forEach(function (radio) {
            radio.disabled = false;
        });

        replaceEditBtn()
        cancelBtn.classList.replace("hidden", "block");
    }

// Add event listener to "Edit" button
    editBtn.addEventListener("click", function () {
        makeEditable();
    });

    const lockHandler = function () {
        makeEditable();
        lockContainer.removeEventListener("click", lockHandler);
    }

    // Add event listener to lock icon
    lockContainer.addEventListener("click", lockHandler);

    // Add event listener to "Cancel" button
    cancelBtn.addEventListener("click", function (event) {
        let confirmation = window.confirm("Are you sure you want to cancel? All unsaved changes will be lost.");
        if (confirmation) {
            window.location.reload();
        }
    });

    select.addEventListener("change", function (event) {
        let confirmation = true;
        if (radioClicked) {
            confirmation = window.confirm("Are you sure you want to change the device? All unsaved changes will be lost.");
        }
        if (!confirmation) {
            event.preventDefault();
        }
        else {
            sendGetRequest(event.target.value)
                .then(response => {
                    window.location = response.url;
                    window.location.reload();
                })
        }
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
                successMsg.className = "success-msg flex";
            } else {
                throw new Error(`Redirect failed! status: ${response.status}`);
            }
            console.log("Changes saved successfully!");
        } catch (error) {
            console.error(error);
            errorMsg.className = "error-msg flex";
        }
    }

    function replaceDeviceIdInUrl(url, newNumber) {
        // Use a regular expression to find the number at the end of the URL
        const regex = /\d+$/;

        // Replace the old number with the new one using the replace() method
        const newUrl = url.replace(regex, newNumber);

        return newUrl;
    }

    async function sendGetRequest(deviceId) {
        try {
            let endpoint = undefined;
            if (deviceId) {
                endpoint = replaceDeviceIdInUrl(window.current_endpoint, deviceId);
            } else {
                endpoint = window.current_endpoint;
            }
            const response = await fetch(endpoint);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            console.log("Loaded policies for device " + deviceId ? deviceId : underline_select.value);
        } catch (error) {
            console.error(error);
        }
    }

    // toggle the visibility of the SVGs
    function toggleLockVisibility() {
        lockClosed.classList.toggle('hidden');
        lockOpen.classList.toggle('hidden');
    }

});
