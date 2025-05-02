$(document).ready(function() {
    // Initialize Select2
    $('#competencies').select2({
        theme: "bootstrap-5",
        width: $( this ).data( 'width' ) ? $( this ).data( 'width' ) : $( this ).hasClass( 'w-100' ) ? '100%' : 'style',
        placeholder: $( this ).data( 'placeholder' ),
        closeOnSelect: false, // Keep dropdown open for multiple selections
    });

    // Custom validation for Select2 minimum selection
    $('#recommendation-form').on('submit', function(event) {
        const competenciesSelect = $('#competencies');
        if (competenciesSelect.val().length === 0) {
            // Add Bootstrap's 'is-invalid' class to the Select2 container
            competenciesSelect.next('.select2-container').addClass('is-invalid');
             // Show the custom invalid feedback message
            competenciesSelect.siblings('.invalid-feedback').show();
            event.preventDefault(); // Prevent form submission
            event.stopPropagation();
        } else {
            competenciesSelect.next('.select2-container').removeClass('is-invalid');
            competenciesSelect.siblings('.invalid-feedback').hide();
            // Proceed with AJAX submission
             handleSubmit(event);
        }
         // Add Bootstrap's was-validated class to show validation styles for other fields if needed
        $(this).addClass('was-validated');

    });

     // Clear validation state when changing selection
    $('#competencies').on('change', function() {
        if ($(this).val().length > 0) {
            $(this).next('.select2-container').removeClass('is-invalid');
            $(this).siblings('.invalid-feedback').hide();
        }
    });

    // Handle form submission via AJAX
    function handleSubmit(event) {
        event.preventDefault(); // Prevent default page reload

        const jobTitle = $('#job-title').val();
        const jobLevel = $('#job-level').val();
        const competencies = $('#competencies').val(); // Already an array from Select2

        const resultsArea = $('#results-area');
        const loadingIndicator = $('#loading-indicator');
        const recommendationsList = $('#recommendations-list');
        const errorMessage = $('#error-message');
        const noResultsMessage = $('#no-results-message');

        // Show loading indicator and hide previous results/errors
        resultsArea.show();
        loadingIndicator.show();
        recommendationsList.empty().hide(); // Clear previous recommendations and hide
        errorMessage.hide();
        noResultsMessage.hide();


        fetch('/recommend', { // Changed to use relative path
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                job_title: jobTitle,
                job_level: jobLevel,
                competencies: competencies
            })
        })
        .then(response => {
            if (!response.ok) {
                 // Try to parse error message from backend if available
                return response.json().then(errData => {
                   throw new Error(errData.error || `HTTP error! status: ${response.status}`);
                }).catch(() => {
                    // Fallback if response is not JSON or error structure is different
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            loadingIndicator.hide();
            if (data && data.length > 0) {
                recommendationsList.show(); // Show the list container
                data.forEach(rec => {
                    const assessment = rec.assessment;
                    const score = rec.score;
                    const listItem = `
                        <div class="list-group-item list-group-item-action flex-column align-items-start mb-2 shadow-sm border-start border-primary border-4">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">${assessment.name} <span class="badge bg-secondary">${assessment.type}</span></h5>
                                <small class="text-muted">Score: ${score}</small>
                            </div>
                            <p class="mb-1">${assessment.description}</p>
                            <small class="text-muted">Relevant Competencies: ${assessment.competencies.join(', ')}</small><br/>
                            <small class="text-muted">Typical Job Levels: ${assessment.job_levels.join(', ')}</small>
                        </div>
                    `;
                    recommendationsList.append(listItem);
                });
            } else {
                 noResultsMessage.show(); // Show no results message
            }
        })
        .catch(error => {
            console.error('Error fetching recommendations:', error);
            loadingIndicator.hide();
            errorMessage.text(`Failed to get recommendations: ${error.message}`).show();
        });
    }
});