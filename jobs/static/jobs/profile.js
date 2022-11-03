document.addEventListener('DOMContentLoaded', function() {

    const owner = document.querySelector(`#profile-owner`);
    const editLink = document.querySelector('#edit-link-profile');

    // Add event listener to the edit link for switching between display and edit modes
    editLink.addEventListener('click',() => switchToEditView(true));

    // Hide the edit form initially
    switchToEditView(false);

    // hide the edit link if current user is not the owner of the profile
    if (owner == null) {
        editLink.style.display = 'none';
    }
});

function switchToEditView(flag) {
    /**
     * Switches between the edit and display views.
     */
    if (flag) {
        document.querySelector('#display-mode').style.display = 'none';
        document.querySelector('#edit-mode').style.display = 'block';
        document.querySelector('#edit-link-profile').style.display = 'none';
    } else {
        document.querySelector('#display-mode').style.display = 'block';
        document.querySelector('#edit-mode').style.display = 'none';
        document.querySelector('#edit-link-profile').style.block = 'none';
    }
}