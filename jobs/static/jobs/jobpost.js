document.addEventListener('DOMContentLoaded', function() {

    // Add event listener to the edit link for switching between display and edit modes
    const editButton = document.querySelector('#edit-button');
    if (editButton != null) {
        document.querySelector('#edit-button').addEventListener('click',
            () => switchToEditView(true));
    }

    // Add event listener to the apply button
    const applyButton =  document.querySelector('.application-btn');
    if (applyButton != null) {
        applyButton.addEventListener('click', () => applyJob(applyButton.dataset.id));
    }

    // Hide the edit form initially
    switchToEditView(false);
});

function applyJob(jobPostID) {
    /**
     * creates/cancels a job application.
     */

    // Get the CSRF token
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Send PUT request to apply for a job
    fetch(`/applyjob/${jobPostID}`, {
        method: 'PUT',
        headers: {"X-CSRFToken": token}
    })
        .then(response => response.json())
        .then(application => {
            // Update the number of applicants value in HTML
            document.querySelector(`#num-of-applicants`).innerHTML = `Applicants: ${application.applicants}`;

            // Update the button
            const applyButton = document.querySelector(`.application-btn`);
            if (application.applied) {
                // Convert the button into a cancellation button
                applyButton.classList.remove('btn-success');
                applyButton.classList.add('btn-danger');
                applyButton.children[0].innerHTML = 'Cancel Application';

            } else {
                // Convert the button into an application button
                applyButton.classList.remove('btn-danger');
                applyButton.classList.add('btn-success');
                applyButton.children[0].innerHTML = 'Apply';
            }
        });

    return false;
}

function switchToEditView(flag) {
    /**
     * Switches between the edit and display views.
     */

    const showEditDiv = document.querySelector(`#show-edit-mode`);
    const editButton = document.querySelector('#edit-button');

    // Show the edit view if either flag or showEditDiv are true
    if (flag || showEditDiv != null) {

        document.querySelectorAll('.display-mode').forEach(displayModeDiv => {
            displayModeDiv.style.display = 'none';
        });

        document.querySelectorAll('.edit-mode').forEach(editModeDiv => {
            editModeDiv.style.display = 'block';
        });

        if (editButton != null) {
            document.querySelector('#edit-button').style.display = 'none';
        }

    } else {

        document.querySelectorAll('.display-mode').forEach(displayModeDiv => {
            displayModeDiv.style.display = 'block';
        });

        document.querySelectorAll('.edit-mode').forEach(editModeDiv => {
            editModeDiv.style.display = 'none';
        });
        if (editButton != null) {
            document.querySelector('#edit-button').style.display = 'block';
        }
    }
}