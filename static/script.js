document.addEventListener("DOMContentLoaded", function () {
    // Function to fetch and display settings
    function displaySettings() {
        fetch("http://localhost:8080/manager/sharia_module/settings")
            .then((response) => response.json())
            .then((data) => {
                const settingsList = document.getElementById("settings-list");

                // Clear the list before adding new data
                settingsList.innerHTML = "";
                console.log(data)
                console.log(data.words)

                data.words.forEach((word) => {
                    const li = document.createElement("li");
                    li.textContent = word;
                    settingsList.appendChild(li);
                });
            })
            .catch((error) => {
                console.error("Error fetching settings:", error);
            });
    }

    // Initial display of settings
    displaySettings();

    // Event listener for the "Add New Word" button
    document.getElementById("add-word-button").addEventListener("click", function () {
        const newWord = prompt("Enter a new word:");
        if (newWord) {
            fetch("http://localhost:8080/manager/sharia_module/settings", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ word: newWord }),
            })
                .then(() => {
                    // Refresh the settings list after adding a new word
                    displaySettings();
                })
                .catch((error) => {
                    console.error("Error adding word:", error);
                });
        }
    });
});
