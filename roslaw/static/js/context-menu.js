document.addEventListener('DOMContentLoaded', function() {
    // Context menu elements
    const contextMenu = document.getElementById('context-menu');
    let activeElement = null;
    
    // Event listener for right click
    document.addEventListener('contextmenu', function(e) {
        const target = e.target.closest('.content-item');
        
        // Only show menu for content items
        if (target) {
            e.preventDefault();
            
            // Store the clicked element
            activeElement = target;
            
            // Get data attributes
            const itemType = target.getAttribute('data-type');
            const itemId = target.getAttribute('data-id');
            const canEdit = target.getAttribute('data-can-edit') === 'true';
            const canDelete = target.getAttribute('data-can-delete') === 'true';
            
            // Update menu links
            document.getElementById('view-link').href = `/${itemType}/${itemId}/`;
            document.getElementById('edit-link').href = `/${itemType}/${itemId}/edit/`;
            document.getElementById('delete-form').action = `/${itemType}/${itemId}/delete/`;
            
            // Show/hide edit and delete options based on permissions
            document.getElementById('edit-option').style.display = canEdit ? 'block' : 'none';
            document.getElementById('delete-option').style.display = canDelete ? 'block' : 'none';
            
            // Position and show the menu
            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.classList.add('show');
        }
    });
    
    // Hide context menu when clicking elsewhere
    document.addEventListener('click', function() {
        if (contextMenu) {
            contextMenu.classList.remove('show');
        }
    });
    
    // Delete confirmation handler
    document.getElementById('delete-button').addEventListener('click', function(e) {
        if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
            e.preventDefault();
        }
    });
});
