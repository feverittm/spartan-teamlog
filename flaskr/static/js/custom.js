
// Auto-focus the quick check-in input when page loads
window.addEventListener('DOMContentLoaded', function() {{
    const quickCheckinInput = document.querySelector('.quick-checkin input[name="member_name"]');
    if (quickCheckinInput) {{
        // Auto-focus the input field when dashboard loads
        quickCheckinInput.focus();
        
        // Add enter key handler
        quickCheckinInput.addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                this.form.submit();
            }}
        }});
        
        // Auto-complete suggestion (simple implementation)
        quickCheckinInput.addEventListener('input', function() {{
            // Clear previous timeout
            clearTimeout(this.searchTimeout);
            
            // Add slight delay for better UX
            this.searchTimeout = setTimeout(() => {{
                // Here you could add AJAX search suggestions in the future
            }}, 300);
        }});
    }}
}});
