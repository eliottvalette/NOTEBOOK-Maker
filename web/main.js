document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    document.getElementById('result').textContent = "Running pipeline...";

    const response = await fetch('/run-pipeline', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        if (data.success) {
            document.getElementById('result').innerHTML = `Pipeline complete! <a href="${data.notebook_url}" download>Download notebook</a>`;
        } else {
            document.getElementById('result').textContent = "Pipeline failed: " + data.error;
        }
    } else {
        document.getElementById('result').textContent = "Server error.";
    }
}); 