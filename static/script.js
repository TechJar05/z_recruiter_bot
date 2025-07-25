document.addEventListener("DOMContentLoaded", () => {

    // Get elements
    const uploadBtn = document.getElementById("upload-btn");
    const resumeUpload = document.getElementById("resume-upload");
    const linkedinConnectBtn = document.getElementById("linkedin-connect-btn");
    const statusMessage = document.getElementById("status-message");
    const linkedinStatus = document.getElementById("linkedin-status");

    // Handle Resume Upload
    uploadBtn.addEventListener("click", async () => {
        const file = resumeUpload.files[0];
        if (!file) {
            statusMessage.textContent = "Please upload a resume.";
            return;
        }

        const formData = new FormData();
        formData.append("resume", file);

        statusMessage.textContent = "Uploading resume...";

        try {
            const response = await fetch("/api/parse/", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                statusMessage.textContent = "Resume uploaded and parsed successfully!";
                console.log("Parsed Resume Data:", data.parsed_resume);
                displayParsedResume(data.parsed_resume);  // Display parsed data in UI
            } else {
                statusMessage.textContent = "Error parsing resume: " + data.error;
            }
        } catch (error) {
            statusMessage.textContent = "Error uploading resume: " + error.message;
        }
    });

    // Display parsed resume data (after upload)
    function displayParsedResume(parsedData) {
        const resumeContainer = document.getElementById("parsed-resume-container");
        resumeContainer.innerHTML = `
            <h3>Parsed Resume Data</h3>
            <p><strong>Name:</strong> ${parsedData.full_name || 'N/A'}</p>
            <p><strong>Email:</strong> ${parsedData.email_address || 'N/A'}</p>
            <p><strong>Phone:</strong> ${parsedData.contact_number || 'N/A'}</p>
            <p><strong>LinkedIn:</strong> <a href="${parsedData.linkedin_profile || '#'}" target="_blank">${parsedData.linkedin_profile || 'Not available'}</a></p>
            <p><strong>Work Experience:</strong> ${parsedData.work_experience ? parsedData.work_experience.map(job => `${job.company_name} (${job.start_date} - ${job.end_date})`).join('<br>') : 'N/A'}</p>
            <p><strong>Education:</strong> ${parsedData.education ? parsedData.education.map(edu => `${edu.degree} from ${edu.institution_name} (${edu.year_of_passing})`).join('<br>') : 'N/A'}</p>
        `;
    }

    // Handle LinkedIn Authentication
    linkedinConnectBtn.addEventListener("click", () => {
        // Redirect to LinkedIn authorization URL
        window.location.href = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=77efxh74ei8t5n&redirect_uri=https%3A%2F%2Fwww.rms.zecruiters.com%2FAI&state=xyz123&scope=r_liteprofile%20r_emailaddress%20w_member_social";
    });

    // Capture LinkedIn authorization code from URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    const state = urlParams.get("state");

    if (code) {
        linkedinStatus.textContent = "Connecting to LinkedIn...";

        // Send the code to backend for token exchange
        fetch("/api/linkedin/exchange/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: code,
                state: state
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "✅ LinkedIn profile saved successfully") {
                linkedinStatus.textContent = "LinkedIn profile successfully connected!";
            } else {
                linkedinStatus.textContent = "Error connecting LinkedIn: " + data.error;
            }
        })
        .catch(error => {
            linkedinStatus.textContent = "Error: " + error.message;
        });
    }

});
