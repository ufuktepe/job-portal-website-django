document.addEventListener('DOMContentLoaded', function() {

    // Variable for identifying whether the current user is the resume owner or not
    const owner = document.querySelector(`#resume-owner`);

    // Add event listener to all remove links (class names starting with 'remove-link')
    document.querySelectorAll("[class^='remove-link']").forEach(removeLink => {
        removeLink.addEventListener('click', function() {
            removeItem(removeLink);
            return false;
        });

        // hide remove link if current user is not the owner of the resume
        if (owner == null) {
            removeLink.style.display = 'none';
        }
    });

    // Hide all edit forms and add event listener to all edit forms
    document.querySelectorAll("[class^='edit-form']").forEach(form => {
        // Initially hide the edit form
        switchToEditView(false, form);

        // Event listener for edit forms
        form.onsubmit = function () {
            // Get the data-id of the form
            const dataID = form.dataset.id;
            // Identify which section the edit form belongs to
            const identifier = form.className.split('-').pop();

            if (identifier === "resume") {
                // Get the new content and call the editResume function
                const newContent = form.querySelector("textarea").value;
                editResume(dataID, newContent);
            }
            else if (identifier === "experience") {
                // Get the new data
                const jobTitle = form.querySelector('#job-title').value;
                const companyName = form.querySelector('#company-name').value;
                const loc = form.querySelector('#location').value;
                let startMonth = form.querySelector('.month-field-start').value;
                let startYear = form.querySelector('.year-field-start').value;
                let endMonth = form.querySelector('.month-field-end').value;
                let endYear = form.querySelector('.year-field-end').value;
                const currentJob = document.querySelector(`.current-job-checkbox[data-id="${dataID}"]`).checked;
                const desc = form.querySelector('textarea').value;

                // Convert the start dates into integers
                if (!isNaN(startMonth)) { startMonth = parseInt(startMonth); }
                if (!isNaN(startYear)) { startYear = parseInt(startYear); }

                // Convert the end dates into integers if not current job
                if (!currentJob && !isNaN(endMonth)) { endMonth = parseInt(endMonth); }
                if (!currentJob && !isNaN(endYear)) { endYear = parseInt(endYear); }

                editExperience(dataID, jobTitle, companyName, loc, startMonth, startYear, endMonth, endYear, currentJob, desc);
            }
            else if (identifier === 'education') {
                // Get the new data
                const school = form.querySelector('#school').value;
                const degree = form.querySelector('#degree').value;
                const fieldOfStudy = form.querySelector('#field-of-study').value;
                let startMonth = form.querySelector('.month-field-start').value;
                let startYear = form.querySelector('.year-field-start').value;
                let endMonth = form.querySelector('.month-field-end').value;
                let endYear = form.querySelector('.year-field-end').value;

                // Convert the dates into integers
                if (!isNaN(startMonth)) { startMonth = parseInt(startMonth); }
                if (!isNaN(startYear)) { startYear = parseInt(startYear); }
                if (!isNaN(endMonth)) { endMonth = parseInt(endMonth); }
                if (!isNaN(endYear)) { endYear = parseInt(endYear); }

                editEducation(dataID, school, degree, fieldOfStudy, startMonth, startYear, endMonth, endYear);
            }
            return false;
        };
    });

    // Add event listener to all edit links (class names starting with 'edit-link') for
    // switching the edit forms on and off
    document.querySelectorAll("[class^='edit-link']").forEach(editLink => {
        editLink.addEventListener('click', function() {
            switchToEditView(true, editLink);
        });

        // Hide link if current user is not the owner of the resume
        if (owner == null) {
            editLink.style.display = 'none';
        }
    });

    // Populate all dropdown elements for selecting the months
    document.querySelectorAll("[class^='month-field']").forEach(selectMonth => {
        populateSelectMonth(selectMonth);
    });

    // Populate all dropdown elements for selecting the years
    document.querySelectorAll("[class^='year-field']").forEach(selectYear => {
        populateSelectYear(selectYear);
    });

    // Populate all dropdown elements for selecting the degrees
    document.querySelectorAll('.degree-field').forEach(selectDegree => {
        populateSelectDegree(selectDegree);
    });

    // Event listener for showing Add forms
    document.querySelectorAll('.add-link').forEach(addLink => {
        // Initially hide the Add form
        switchToAddView(false, addLink);

        // Add event listener for showing the Add form
        addLink.addEventListener('click', function () {
            switchToAddView(true, addLink);
        });

        // Hide link if current user is not the owner of the resume
        if (owner == null) {
            addLink.style.display = 'none';
        }
    });

    // Add event listener to "I currently work here" checkbox
    document.querySelectorAll('.checkbox-field').forEach(checkBoxDiv => {
        // Call deactivateEndDate initially
        deactivateEndDate(checkBoxDiv);

        // Get the checkBox
        const checkBox = checkBoxDiv.children[0];

        // Add on change event to checkBox to hide/show the end date
        checkBox.addEventListener('change', function () {
            deactivateEndDate(checkBoxDiv);
        });
    });
});

function editResume(dataID, newContent) {
    /**
     * Sends a PUT request to update the resume object. Gets the new data.
     * Then hides the edit form anf displays the new data.
     */

    // Get the CSRF token
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Send put request to edit the resume
    fetch(`/editresume/${dataID}`, {
        method: 'PUT',
        body: JSON.stringify({content: newContent}),
        headers: {"X-CSRFToken": token}
    })
        .then(response => response.json())
        .then(result => {
            // Get the relevant div
            const contentDiv = document.querySelector(`.content-resume[data-id="${dataID}"]`);

            // Update the content
            contentDiv.innerHTML = result.content;

            // Hide the edit form and show the content itself
            switchToEditView(false, contentDiv);
        })
        .catch(error => {
            console.log(error);
        });

    // Prevent the form from submitting
    return false;
}

function editExperience(dataID, jobTitle, companyName, loc, startMonth, startYear, endMonth, endYear, currentJob, desc) {
    /**
     * Validates the data then sends a PUT request to update the experience object. Gets the new data.
     * Then hides the edit form and displays the new data.
     */

    // Validate the inputs
    if (!validateExperienceForm(dataID, jobTitle, companyName, loc, startMonth, startYear, endMonth, endYear, currentJob, desc)) {
        return false;
    }

    // Get the CSRF token
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Send put request to edit the experience object
    fetch(`/editexperience/${dataID.substring(3)}`, {
        method: 'PUT',
        body: JSON.stringify({
            jobTitle: jobTitle,
            companyName: companyName,
            loc: loc,
            startMonth: startMonth,
            startYear: startYear,
            endMonth: endMonth,
            endYear: endYear,
            currentJob: currentJob,
            desc: desc}),
        headers: {"X-CSRFToken": token}
    })
        .then(response => response.json())
        .then(result => {

            // Update the relevant elements
            document.querySelector(`.display-title-large[data-id="${dataID}"]`).innerHTML = result.job_title;
            document.querySelector(`.display-title-medium[data-id="${dataID}"]`).innerHTML = result.company_name;
            document.querySelector(`.display-title-small[data-id="${dataID}"]`).innerHTML = result.location;
            document.querySelector(`.display-start-month[data-id="${dataID}"]`).innerHTML = result.start_month;
            document.querySelector(`.display-start-year[data-id="${dataID}"]`).innerHTML = result.start_year;

            // Set the end date
            const endDate = document.querySelector(`.date-field-display-end[data-id="${dataID}"]`);
            if (result.current_job) {
                endDate.innerHTML = 'Present';
            } else {
                endDate.innerHTML = result.end_month + '/' + result.end_year;
            }

            // Set the description and then hide the edit form and show the content itself
            const desc = document.querySelector(`.content-experience[data-id="${dataID}"]`);
            desc.innerHTML = result.description;
            switchToEditView(false, desc);
        })
        .catch(error => {
            console.log(error);
        });

    // Prevent the form from submitting
    return false;
}

function editEducation(dataID, school, degree, fieldOfStudy, startMonth, startYear, endMonth, endYear) {
    /**
     * Validates the data then sends a PUT request to update the education object. Gets the new data.
     * Then hides the edit form and displays the new data.
     */

    // Validate the inputs
    if (!validateEducationForm(dataID, school, degree, fieldOfStudy, startMonth, startYear, endMonth, endYear)) {
        return false;
    }

    // Get the CSRF token
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Send put request to edit the education object
    fetch(`/editeducation/${dataID.substring(3)}`, {
        method: 'PUT',
        body: JSON.stringify({
            school: school,
            degree: degree,
            fieldOfStudy: fieldOfStudy,
            startMonth: startMonth,
            startYear: startYear,
            endMonth: endMonth,
            endYear: endYear}),
        headers: {"X-CSRFToken": token}
    })
        .then(response => response.json())
        .then(result => {

            // Update the relevant elements
            document.querySelector(`.display-title-medium[data-id="${dataID}"]`).innerHTML = result.degree;
            document.querySelector(`.display-title-small[data-id="${dataID}"]`).innerHTML = result.field_of_study;
            document.querySelector(`.display-start-month[data-id="${dataID}"]`).innerHTML = result.start_month;
            document.querySelector(`.display-start-year[data-id="${dataID}"]`).innerHTML = result.start_year;
            document.querySelector(`.display-end-month[data-id="${dataID}"]`).innerHTML = result.end_month;
            document.querySelector(`.display-end-year[data-id="${dataID}"]`).innerHTML = result.end_year;

            // Update the school and then hide the edit form and show the content itself
            const school = document.querySelector(`.display-title-large[data-id="${dataID}"]`);
            school.innerHTML = result.school;
            switchToEditView(false, school);
        })
        .catch(error => {
            console.log(error);
        });

    // Prevent the form from submitting
    return false;
}

function removeItem(removeLink) {
    /**
     * Sends a PUT request to remove any resume, education, or experience item
     */

    // Get the field to identify the resume section
    const field = removeLink.className.split(' ')[0].split('-').pop();

    // Get the data-id to identify the primary key of the object
    const dataID = removeLink.dataset.id;

    // Create a variable containing both resume section and primary key info
    const fieldID = field + '_' + dataID.substring(3);

    // Get the CSRF token
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Send put request to remove the item
    fetch(`/removeitem/${fieldID}`, {
        method: 'PUT',
        headers: {"X-CSRFToken": token}
    })
        .then(response => response.json())
        .then(result => {
            console.log(result.message);
            // Get the div element
            const containerClass = 'container-item-' + field;
            const containerDiv = document.querySelector(`.${containerClass}[data-id="${dataID}"]`);
            // Set the animation play state to running so that animationend
            // event listener gets triggered to remove containerDiv
            containerDiv.style.animationPlayState = 'running';
        })
        .catch(error => {
            console.log(error);
        });

    // Prevent the form from submitting
    return false;
}

function switchToEditView(showEditForm, elm) {
    /**
     * Switches between the edit post form and the post itself.
     */

    // Get the data-id of the elm
    const dataID = elm.dataset.id;

    // Get the last part of the elm's class name
    const identifier = elm.className.split(' ')[0].split('-').pop();

    // Get the display and edit classes
    const displayClass  = 'display-mode-' + identifier;
    const editClass  = 'edit-mode-' + identifier;

    // Get the add button id
    const addID = 'add-' + identifier;

    // Get the edit link
    const editLinkClass = 'edit-link-' + identifier;
    const editLink = document.querySelector(`.${editLinkClass}[data-id="${dataID}"]`);

    if (showEditForm) {
        // Edit Mode
        document.querySelector(`.${displayClass}[data-id="${dataID}"]`).style.display = 'none';
        document.querySelector(`.${editClass}[data-id="${dataID}"]`).style.display = 'block';
        if (identifier === "experience" || identifier === "education") {
            document.querySelector(`#${addID}`).style.display = 'none';
        }
        if (editLink != null) {
            editLink.style.display = 'none';
        }

    } else {
        // Display Mode
        document.querySelector(`.${displayClass}[data-id="${dataID}"]`).style.display = 'block';
        document.querySelector(`.${editClass}[data-id="${dataID}"]`).style.display = 'none';
        if (identifier === "experience" || identifier === "education") {
            document.querySelector(`#${addID}`).style.display = 'block'
        }
        if (editLink != null) {
            editLink.style.display = 'block';
        }
    }
}

function switchToAddView(showAddForm, elm) {
    /**
     * Switches the add form on and off.
     */

    // Get the last part of the elm's class name
    const identifier = elm.id.split('-').pop();

    // Get the div elm
    const divClass  = 'add-mode-' + identifier;
    const divElm = document.querySelector(`.${divClass}`);

    // Get the error div elm
    const errorDiv = document.querySelector(`#${divClass}`)

    // Show the add form and hide the add button if showAddForm is true
    // or if there is a validation error for the form
    if (showAddForm || errorDiv != null) {
        divElm.style.display = 'block';
        elm.style.display = 'none';
    } else {
        // Hide the add form and show the add button
        divElm.style.display = 'none';
        elm.style.display = 'block';
    }
}

function populateSelectMonth(selectMonth) {
    /**
     * Adds months to the dropdown menu.
     */

    // Populate the dropdown menu
    for (let i = 0; i < 12; i++) {
        const opt = document.createElement('option');
        opt.value = i+1;
        opt.innerHTML = i+1;
        selectMonth.appendChild(opt);
    }

    // Set the value
    selectMonth.value = selectMonth.dataset.id;
}

function populateSelectYear(selectYear) {
    /**
     * Adds years to the dropdown menu.
     */

    // Get the current year
    const currentYear = (new Date()).getFullYear();

    // Add years to the dropdown
    for (var i = 1960; i <= currentYear; i++) {
        const opt = document.createElement('option');
        opt.innerHTML = i;
        opt.value = i;
        selectYear.appendChild(opt);
    }

    // Set the value
    selectYear.value = selectYear.dataset.id;
}

function populateSelectDegree(selectDegree) {
    /**
     * Adds degree types to the dropdown menu.
     */

    const degrees = ['High School', 'Vocational Degree', 'Associate\'s Degree',
        'Bachelor\'s Degree', 'Master\'s Degree', 'Doctoral Degree']

    // Add degrees to the dropdown
    for (let i = 0; i < degrees.length; i++) {
        const opt = document.createElement('option');
        opt.value = degrees[i];
        opt.innerHTML = degrees[i];
        selectDegree.appendChild(opt);
    }

    // Set the value
    selectDegree.value = selectDegree.dataset.id;
}

function validateExperienceForm(dataID, jobTitle, companyName, loc, startMonth, startYear, endMonth, endYear, currentJob, desc) {
    /**
     * Validates user inputs of the experience form
     */

    // Check the job title
    if (!validateLength(jobTitle, dataID, 'Please enter a job title.')) {
        return false;
    }

    // Check the company name
    if (!validateLength(companyName, dataID, 'Please enter a company name.')) {
        return false;
    }

    // Check the location
    if (!validateLength(loc, dataID, 'Please enter a location.')) {
        return false;
    }

    // Check the date
    if (!validateDate(dataID, startMonth, startYear, endMonth, endYear, !currentJob)) {
        return false;
    }

    // Check the description
    if (!validateLength(desc, dataID, 'Please enter a job description.')) {
        return false;
    }

    // Set the error message to empty string
    document.querySelector(`.error-msg[data-id="${dataID}"]`).innerHTML = '';
    return true;
}

function validateEducationForm(dataID, school, degree, fieldOfStudy, startMonth, startYear, endMonth, endYear) {
    /**
     * Validates user inputs of the education form
     */

    // Check the school name
    if (!validateLength(school, dataID, 'Please enter a school.')) {
        return false;
    }

    // Check the degree
    if (!validateLength(degree, dataID, 'Please enter a degree.')) {
        return false;
    }

    // Check the field of study
    if (!validateLength(fieldOfStudy, dataID, 'Please enter a field of study.')) {
        return false;
    }

    // Check the date
    if (!validateDate(dataID, startMonth, startYear, endMonth, endYear, true)) {
        return false;
    }

    // Set the error message to empty string
    document.querySelector(`.error-msg[data-id="${dataID}"]`).innerHTML = '';
    return true;
}

function validateLength(dataStr, dataID, msg) {
    /**
     * Checks if there is content in string
     */

    if (dataStr.length < 1) {
        document.querySelector(`.error-msg[data-id="${dataID}"]`).innerHTML = `${msg}`;
        return false;
    }
    return true;
}

function validateDate(dataID, startMonth, startYear, endMonth, endYear, checkEndDate) {
    /**
     * Validates the dates by checking if they are integers and if the date range is valid
     */

    // Check the start date
    if (isNaN(startMonth) || isNaN(startYear)) {
        document.querySelector(`.error-msg[data-id="${dataID}"]`).innerHTML = 'Please select a valid start date.';
        return false;
    }

    // Check the end date
    if (checkEndDate && (isNaN(endMonth) || isNaN(endYear))) {
        document.querySelector(`.error-msg[data-id="${dataID}"]`).innerHTML = 'Please select a valid end date.';
        return false;
    }

    // Check the date range
    if (checkEndDate && (endYear < startYear || (startYear === endYear && endMonth <= startMonth))) {
        document.querySelector(`.error-msg[data-id="${dataID}"]`).innerHTML = 'Please select a valid date range.';
        return false;
    }

    return true;
}

function deactivateEndDate(checkBoxDiv) {
    /**
     * Hides/shows the end date.
     */

    // Get the checkBox state
    const flag = checkBoxDiv.children[0].checked;

    // Get the end date div
    const dateFieldDiv = document.querySelector(`.date-field-edit-end[data-id="${checkBoxDiv.dataset.id}"]`)

    // Get the children of end date div
    const subDivs = dateFieldDiv.children;

    // Hide/show the end date dropdowns
    for (let i = 0; i < subDivs.length - 1; i++) {
        if (flag) {
            subDivs[i].style.display = 'none';
        } else {
            subDivs[i].style.display = 'block';
        }
    }

    // Hide/show "Present"
    if (flag) {
        subDivs[subDivs.length - 1].style.display = 'block';
    } else {
        subDivs[subDivs.length - 1].style.display = 'none';
    }
}

