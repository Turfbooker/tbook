document.addEventListener('DOMContentLoaded', function() {
    // Handle date selection for turf booking
    const dateSelector = document.getElementById('booking_date');
    const bookingForm = document.getElementById('booking-form');
    
    if (dateSelector && bookingForm) {
        dateSelector.addEventListener('change', function() {
            // Redirect to the same page with date parameter
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('date', this.value);
            window.location.href = currentUrl.toString();
        });
    }
    
    // Handle time slot selection
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    const timeSlots = document.querySelectorAll('.time-slot');
    let selectedStartSlot = null;
    
    if (startTimeInput && endTimeInput && timeSlots.length) {
        timeSlots.forEach(slot => {
            if (slot.classList.contains('available')) {
                slot.addEventListener('click', function() {
                    const time = this.dataset.time;
                    
                    if (!selectedStartSlot) {
                        // First click selects start time
                        selectedStartSlot = this;
                        startTimeInput.value = time;
                        this.classList.add('selected', 'bg-primary');
                        timeSlots.forEach(s => {
                            if (s !== this && s.classList.contains('available')) {
                                s.classList.add('potential-end');
                            }
                        });
                    } else {
                        // Second click selects end time
                        const startTime = selectedStartSlot.dataset.time;
                        
                        if (time <= startTime) {
                            // End time must be after start time
                            alert('End time must be after start time');
                            return;
                        }
                        
                        // Check if there are any booked slots between start and end
                        let hasBookedSlotsBetween = false;
                        let inBetween = false;
                        
                        timeSlots.forEach(s => {
                            const slotTime = s.dataset.time;
                            
                            if (slotTime === startTime) {
                                inBetween = true;
                            } else if (slotTime === time) {
                                inBetween = false;
                            }
                            
                            if (inBetween && s.classList.contains('booked')) {
                                hasBookedSlotsBetween = true;
                            }
                        });
                        
                        if (hasBookedSlotsBetween) {
                            alert('There are already booked slots in your selected time range');
                            resetTimeSelection();
                            return;
                        }
                        
                        // Set end time and highlight all selected slots
                        endTimeInput.value = time;
                        this.classList.add('selected', 'bg-success');
                        
                        // Highlight all slots between start and end
                        let highlighting = false;
                        timeSlots.forEach(s => {
                            const slotTime = s.dataset.time;
                            
                            if (slotTime === startTime) {
                                highlighting = true;
                            } else if (slotTime === time) {
                                highlighting = false;
                            } else if (highlighting && s.classList.contains('available')) {
                                s.classList.add('selected', 'bg-info');
                            }
                            
                            s.classList.remove('potential-end');
                        });
                        
                        // Calculate price
                        calculatePrice();
                    }
                });
            }
        });
        
        // Add reset button functionality
        const resetButton = document.getElementById('reset-time-selection');
        if (resetButton) {
            resetButton.addEventListener('click', resetTimeSelection);
        }
    }
    
    function resetTimeSelection() {
        selectedStartSlot = null;
        
        // Only set input values if they exist
        if (startTimeInput) startTimeInput.value = '';
        if (endTimeInput) endTimeInput.value = '';
        
        if (timeSlots && timeSlots.length) {
            timeSlots.forEach(slot => {
                slot.classList.remove('selected', 'bg-primary', 'bg-success', 'bg-info', 'potential-end');
            });
        }
        
        // Reset price display
        const priceDisplay = document.getElementById('calculated-price');
        if (priceDisplay) {
            priceDisplay.textContent = '';
        }
    }
    
    function calculatePrice() {
        if (!startTimeInput || !endTimeInput || !startTimeInput.value || !endTimeInput.value) return;
        
        const startTime = startTimeInput.value;
        const endTime = endTimeInput.value;
        
        // Convert times to hours
        const startHours = parseFloat(startTime.split(':')[0]) + parseFloat(startTime.split(':')[1]) / 60;
        const endHours = parseFloat(endTime.split(':')[0]) + parseFloat(endTime.split(':')[1]) / 60;
        
        // Calculate duration in hours
        const duration = endHours - startHours;
        
        // Get hourly rate
        const hourlyRateElement = document.getElementById('hourly-rate');
        if (!hourlyRateElement || !hourlyRateElement.dataset.price) return;
        
        const hourlyRate = parseFloat(hourlyRateElement.dataset.price);
        
        // Calculate total price
        const totalPrice = duration * hourlyRate;
        
        // Display price
        const priceDisplay = document.getElementById('calculated-price');
        if (priceDisplay) {
            priceDisplay.textContent = `₹${totalPrice.toFixed(2)}`;
        }
    }
    
    // Calendar date navigation
    const prevDateBtn = document.getElementById('prev-date');
    const nextDateBtn = document.getElementById('next-date');
    
    if (prevDateBtn && nextDateBtn && dateSelector) {
        prevDateBtn.addEventListener('click', function() {
            const currentDate = new Date(dateSelector.value);
            currentDate.setDate(currentDate.getDate() - 1);
            
            const year = currentDate.getFullYear();
            const month = String(currentDate.getMonth() + 1).padStart(2, '0');
            const day = String(currentDate.getDate()).padStart(2, '0');
            
            const newDate = `${year}-${month}-${day}`;
            dateSelector.value = newDate;
            
            // Trigger change event to reload the page
            const event = new Event('change');
            dateSelector.dispatchEvent(event);
        });
        
        nextDateBtn.addEventListener('click', function() {
            const currentDate = new Date(dateSelector.value);
            currentDate.setDate(currentDate.getDate() + 1);
            
            const year = currentDate.getFullYear();
            const month = String(currentDate.getMonth() + 1).padStart(2, '0');
            const day = String(currentDate.getDate()).padStart(2, '0');
            
            const newDate = `${year}-${month}-${day}`;
            dateSelector.value = newDate;
            
            // Trigger change event to reload the page
            const event = new Event('change');
            dateSelector.dispatchEvent(event);
        });
    }
});
