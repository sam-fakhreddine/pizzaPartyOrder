const API_URL = '/orders'; // Use a relative URL to avoid specifying domain/IP

let userId = localStorage.getItem('userId');

// Generate a UUID for new users
function generateUUID() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

// Assign a UUID to the user if not already set in localStorage
if (!userId) {
    userId = generateUUID();
    localStorage.setItem('userId', userId);
}
console.log(`User ID for this session: ${userId}`);

document.addEventListener('DOMContentLoaded', () => {
    const pizzaPartyDateInput = document.getElementById('pizzaPartyDate');
    const today = new Date().toISOString().split('T')[0];
    pizzaPartyDateInput.setAttribute('min', today); // Prevents selecting past dates

    // Initialize date from localStorage if available
    const savedDate = localStorage.getItem('pizzaPartyDate');
    if (savedDate) {
        pizzaPartyDateInput.value = savedDate;
        fetchOrdersForDate(savedDate, userId);
    }

    // Handle date change and save to localStorage
    pizzaPartyDateInput.addEventListener('change', (event) => {
        const selectedDate = event.target.value;
        if (!selectedDate) {
            dateError.textContent = 'Please select a valid date.';
            return;
        }
        localStorage.setItem('pizzaPartyDate', selectedDate);
        dateError.textContent = '';  // Clear any previous errors
        fetchOrdersForDate(selectedDate, userId);
    });

    pizzaPartyDateInput.addEventListener('input', () => {
        dateError.textContent = ''; // Clear error message if the input is updated
    });
});

const dateError = document.getElementById('dateError');

// Fetch and display cumulative totals and user-specific orders for a given date
async function fetchOrdersForDate(date, userId) {
    try {
        if (!date) {
            dateError.textContent = 'Please select a Pizza Party date.';
            return;
        }
        const response = await fetch(`${API_URL}?date=${date}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin' // Allows cookies and credentials for same-origin requests
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('API Error:', errorData);
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        const { total_slices: totalSlices, pizzas_needed: pizzasNeeded, total_juice_boxes: totalJuiceBoxes, orders } = result;

        // Filter for user-specific orders
        const userOrders = orders.filter(order => order.user_id === userId);

        // Update the cumulative totals and user order displays
        updateOrderSummary(pizzasNeeded, totalJuiceBoxes);
        updateUserOrders(userOrders);
    } catch (error) {
        console.error('Error fetching orders:', error);
        dateError.textContent = 'Failed to load orders. Please try again.';
    }
}

// Display cumulative totals for pizzas and juice boxes
function updateOrderSummary(pizzasNeeded, totalJuiceBoxes) {
    const summaryContainer = document.getElementById('orderSummary');
    summaryContainer.innerHTML = '<h3>Pizzas Needed:</h3>';
    Object.keys(pizzasNeeded).forEach(pizzaType => {
        summaryContainer.innerHTML += `<p>${pizzaType}: ${pizzasNeeded[pizzaType]} pizzas</p>`;
    });
    summaryContainer.innerHTML += `<p>Total Juice Boxes: ${totalJuiceBoxes}</p>`;
}

// Display orders specific to the current user
function updateUserOrders(userOrders) {
    const lastOrdersContainer = document.getElementById('lastOrders');
    lastOrdersContainer.innerHTML = '';
    userOrders.forEach(order => {
        const orderDiv = document.createElement('div');
        orderDiv.className = 'order';
        const pizzaOrderString = Object.entries(order.pizza_slices)
            .filter(([type, count]) => count > 0)
            .map(([type, count]) => `${type}: ${count} slices`)
            .join(', ');

        orderDiv.innerHTML = `
            <p><strong>Student:</strong> ${order.student_name}</p>
            <p><strong>Pizza Slices:</strong> ${pizzaOrderString || 'None'}</p>
            <p><strong>Juice Boxes:</strong> ${order.juice_boxes}</p>
            <p><strong>Parent Volunteer:</strong> ${order.parent_volunteer || 'N/A'}</p>
        `;
        lastOrdersContainer.appendChild(orderDiv);
    });
}

// Handle form submission to place a new order
document.getElementById('orderForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const selectedDate = document.getElementById('pizzaPartyDate').value;
    const studentName = document.getElementById('studentName').value;
    const zaatar = parseInt(document.getElementById('zaatar').value, 10);
    const cheese = parseInt(document.getElementById('cheese').value, 10);
    const salami = parseInt(document.getElementById('salami').value, 10);
    const veggie = parseInt(document.getElementById('veggie').value, 10);
    const donair = parseInt(document.getElementById('donair').value, 10);
    const juiceBoxes = parseInt(document.getElementById('juiceBoxes').value, 10);
    const parentVolunteer = document.getElementById('parentVolunteer').value;

    const orderData = {
        user_id: userId,
        student_name: studentName,
        pizza_slices: {
            "Zaatar": zaatar,
            "Cheese": cheese,
            "Salami": salami,
            "Veggie": veggie,
            "Donair": donair
        },
        juice_boxes: juiceBoxes,
        parent_volunteer: parentVolunteer || ''
    };

    try {
        const response = await fetch(`${API_URL}?date=${selectedDate}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin', // Allows credentials for same-origin requests
            body: JSON.stringify(orderData)
        });

        if (response.ok) {
            alert('Order submitted successfully!');
            fetchOrdersForDate(selectedDate, userId); // Refresh orders after submission
        } else {
            alert('Error submitting the order.');
        }

        document.getElementById('orderForm').reset();
    } catch (error) {
        console.error('Error submitting order:', error);
    }
});
