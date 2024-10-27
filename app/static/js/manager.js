document.addEventListener("DOMContentLoaded", async () => {
  const ordersDiv = document.getElementById("orders");

  // Fetch orders
  const response = await fetch("/manager/orders");
  const orders = await response.json();
  ordersDiv.innerHTML = JSON.stringify(orders, null, 2);
});

document.getElementById("menuForm").addEventListener("submit", async function(event) {
  event.preventDefault();
  const itemName = document.getElementById("itemName").value;
  const itemType = document.getElementById("itemType").value;

  const response = await fetch("/manager/menu", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: itemName, type: itemType })
  });
  const result = await response.json();
  document.getElementById("menuMessage").textContent = result.message || result.error;
});
