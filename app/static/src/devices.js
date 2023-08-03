import 'flowbite'

document.addEventListener("DOMContentLoaded", function () {
    const trashBtns = document.querySelectorAll(".trash");
    const alertMsg = document.getElementById("alertMsg");

    trashBtns.forEach(function (trashBtn) {
       trashBtn.addEventListener("click", function () {
           if(confirm("Are you sure you want to delete this device?")) {
               const deviceId = trashBtn.parentNode.parentNode.dataset.deviceId;
               deleteDevice(deviceId);
           }
       });
    });

    async function deleteDevice(deviceId) {
        try {
            let url = undefined;
            if(window.SCRIPT_ROOT) {
                url = `${window.SCRIPT_ROOT}/delete-device/${deviceId}`;
            }
            else {
                url = `/delete-device/${deviceId}`;
            }
            const response = await fetch(url, {
                method: "DELETE",
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            if (response.redirected) {
                window.location = response.url;
            } else {
                throw new Error(`Redirect failed! status: ${response.status}`);
            }
            console.log("Changes saved successfully!");
            return response;
        } catch (e) {
            console.error(e);
            alertMsg.classList.replace("hidden", "flex");
        }
    }
});