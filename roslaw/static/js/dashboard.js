$(document).ready(function() {
   


    // Get URL parameters from the data attributes we'll set in the HTML
    const activeChapter = $('#content-data').data('active-chapter');
    const activeSection = $('#content-data').data('active-section');
    const activeSubsection = $('#content-data').data('active-subsection');
    const dashboardUrl = $('#content-data').data('dashboard-url');

    // Initially hide all dropdown content
    $('.sections-container').hide();
    $('.subsections-container').hide();
    $('.qa-container').hide();

    // Apply animation to hierarchy items
    applyHierarchyAnimations();

    // Chapter click handler (for navigation, not accordion)
    $(document).on('click', '.accordion-button', function(e) {
        // Don't navigate when clicking accordion buttons - they'll just expand/collapse
        e.stopPropagation();
    });

    // QA item click handler
    $('.list-group-item[data-id]').click(function(e) {
        const qaId = $(this).data('id');
        if ($(this).find('.badge').length) {
            e.preventDefault();
            alert('Navigate to QA item ' + qaId + ' (to be implemented)');
        }
    });

    // Add Chapter button handler
    $('.add-chapter').click(function() {
        $('#createChapterModal').modal('show');
    });

    // Add Section button handler
    $('.add-section').click(function() {
        const chapterId = $(this).data('chapter');
        $('#sectionChapterId').val(chapterId);
        $('#createSectionModal').modal('show');
    });

    // Add Subsection button handler
    $('.add-subsection').click(function() {
        const sectionId = $(this).data('section');
        $('#subsectionSectionId').val(sectionId);
        $('#createSubsectionModal').modal('show');
    });

    // Add QA button handler
    $('.add-qa').click(function() {
        const subsectionId = $(this).data('subsection');
        $('#qaSubsectionId').val(subsectionId);
        $('#createQAModal').modal('show');
    });

    // Submit Chapter handler
    $('#submitChapter').click(function() {
        const form = $('#createChapterForm');
        const formData = {
            title: $('#chapterTitle').val(),
            description: $('#chapterDescription').val(),
            order: $('#chapterOrder').val(),
            csrfmiddlewaretoken: form.find('input[name="csrfmiddlewaretoken"]').val()
        };

        $.ajax({
            url: '/chapter/create/',
            method: 'POST',
            data: formData,
            success: function(response) {
                $('#createChapterModal').modal('hide');
                window.location.reload();
            },
            error: function(xhr, status, error) {
                alert('Произошла ошибка при создании главы. Пожалуйста, проверьте введенные данные.');
            }
        });
    });

    // Submit Section handler
    $('#submitSection').click(function() {
        const form = $('#createSectionForm');
        const formData = {
            title: $('#sectionTitle').val(),
            description: $('#sectionDescription').val(),
            order: $('#sectionOrder').val(),
            chapter_id: $('#sectionChapterId').val(),
            csrfmiddlewaretoken: form.find('input[name="csrfmiddlewaretoken"]').val()
        };

        $.ajax({
            url: '/section/create/',
            method: 'POST',
            data: formData,
            success: function(response) {
                $('#createSectionModal').modal('hide');
                window.location.reload();
            },
            error: function(xhr, status, error) {
                alert('Произошла ошибка при создании раздела. Пожалуйста, проверьте введенные данные.');
            }
        });
    });

    // Submit Subsection handler
    $('#submitSubsection').click(function() {
        const form = $('#createSubsectionForm');
        const formData = {
            title: $('#subsectionTitle').val(),
            description: $('#subsectionDescription').val(),
            order: $('#subsectionOrder').val(),
            section_id: $('#subsectionSectionId').val(),
            csrfmiddlewaretoken: form.find('input[name="csrfmiddlewaretoken"]').val()
        };

        $.ajax({
            url: '/subsection/create/',
            method: 'POST',
            data: formData,
            success: function(response) {
                $('#createSubsectionModal').modal('hide');
                window.location.reload();
            },
            error: function(xhr, status, error) {
                alert('Произошла ошибка при создании подраздела. Пожалуйста, проверьте введенные данные.');
            }
        });
    });

    // Submit QA handler
    $('#submitQA').click(function() {
        console.log('QA submission clicked');

        const form = $('#createQAForm');
        const formData = {
            title: $('#qaTitle').val(),
            content: $('#qaContent').val(),
            subsection_id: $('#qaSubsectionId').val(),
            csrfmiddlewaretoken: form.find('input[name="csrfmiddlewaretoken"]').val()
        };

        console.log('Form data:', formData);

        $.ajax({
            url: '/qa/create/',
            method: 'POST',
            data: formData,
            success: function(response) {
                console.log('Success:', response);
                $('#createQAModal').modal('hide');
                window.location.reload();
            },
            error: function(xhr, status, error) {
                console.error('Error details:', xhr.responseText);
                alert('Произошла ошибка при создании вопроса-ответа: ' + (xhr.responseJSON ? xhr.responseJSON.error : error));
            }
        });
    });

    // Clear forms when modals are closed
    $('#createChapterModal').on('hidden.bs.modal', function () {
        $('#createChapterForm')[0].reset();
    });

    $('#createSectionModal').on('hidden.bs.modal', function () {
        $('#createSectionForm')[0].reset();
    });

    $('#createSubsectionModal').on('hidden.bs.modal', function () {
        $('#createSubsectionForm')[0].reset();
    });

    $('#createQAModal').on('hidden.bs.modal', function () {
        $('#createQAForm')[0].reset();
    });

    // Function to apply animations to hierarchy items
    function applyHierarchyAnimations() {
        $('.accordion-item').each(function(index) {
            $(this).css({
                'animation': 'fadeIn 0.5s ease-in-out ' + (index * 0.1) + 's'
            });
        });
    }
});