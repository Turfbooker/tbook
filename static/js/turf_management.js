document.addEventListener('DOMContentLoaded', function() {
    // Handle turf deletion confirmation
    const deleteTurfButtons = document.querySelectorAll('.delete-turf-btn');
    
    if (deleteTurfButtons.length) {
        deleteTurfButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                if (!confirm('Are you sure you want to delete this turf? This action cannot be undone.')) {
                    event.preventDefault();
                }
            });
        });
    }
    
    // Handle booking status updates
    const statusUpdateButtons = document.querySelectorAll('.status-update-btn');
    
    if (statusUpdateButtons.length) {
        statusUpdateButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                const status = this.dataset.status;
                const bookingId = this.dataset.bookingId;
                
                if (!confirm(`Are you sure you want to ${status} this booking?`)) {
                    event.preventDefault();
                }
            });
        });
    }
    
    // Turf form amenities tags input
    const amenitiesInput = document.getElementById('amenities');
    const amenitiesDisplay = document.getElementById('amenities-display');
    const amenitiesAddBtn = document.getElementById('add-amenity');
    
    if (amenitiesInput && amenitiesDisplay && amenitiesAddBtn) {
        // Initialize from existing value
        if (amenitiesInput.value) {
            const existingAmenities = amenitiesInput.value.split(',').map(item => item.trim());
            
            existingAmenities.forEach(amenity => {
                if (amenity) {
                    addAmenityTag(amenity);
                }
            });
        }
        
        // Add new amenity when button is clicked
        amenitiesAddBtn.addEventListener('click', function() {
            const amenityInput = document.getElementById('new-amenity');
            
            if (amenityInput && amenityInput.value.trim()) {
                addAmenityTag(amenityInput.value.trim());
                
                // Update hidden input
                updateAmenitiesInput();
                
                // Clear input
                amenityInput.value = '';
            }
        });
        
        // Function to add amenity tag
        function addAmenityTag(amenity) {
            const tag = document.createElement('span');
            tag.classList.add('badge', 'bg-primary', 'me-2', 'mb-2', 'amenity-tag');
            
            tag.innerHTML = `
                ${amenity}
                <button type="button" class="btn-close btn-close-white ms-2" aria-label="Remove"></button>
            `;
            
            amenitiesDisplay.appendChild(tag);
            
            // Add event listener to remove button
            const removeBtn = tag.querySelector('.btn-close');
            removeBtn.addEventListener('click', function() {
                tag.remove();
                updateAmenitiesInput();
            });
        }
        
        // Function to update hidden input with comma-separated list
        function updateAmenitiesInput() {
            const tags = document.querySelectorAll('.amenity-tag');
            const amenitiesList = Array.from(tags).map(tag => {
                // Get text content without the close button text
                return tag.textContent.trim();
            }).join(', ');
            
            amenitiesInput.value = amenitiesList;
        }
    }
    
    // Revenue charts for turf owner dashboard
    const revenueChart = document.getElementById('revenue-chart');
    
    if (revenueChart) {
        // Get revenue data from the data attributes
        const labels = JSON.parse(revenueChart.dataset.labels || '[]');
        const data = JSON.parse(revenueChart.dataset.values || '[]');
        
        // Create chart
        new Chart(revenueChart, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue (₹)',
                    data: data,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value;
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '₹' + context.raw;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Booking statistics chart for turf owner dashboard
    const bookingStatsChart = document.getElementById('booking-stats-chart');
    
    if (bookingStatsChart) {
        // Get booking data from the data attributes
        const labels = JSON.parse(bookingStatsChart.dataset.labels || '[]');
        const data = JSON.parse(bookingStatsChart.dataset.values || '[]');
        
        // Create chart
        new Chart(bookingStatsChart, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Bookings',
                    data: data,
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.7)',
                        'rgba(25, 135, 84, 0.7)',
                        'rgba(220, 53, 69, 0.7)',
                        'rgba(255, 193, 7, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
});
