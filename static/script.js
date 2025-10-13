class ShipManager {
    constructor() {
        this.apiBase = '/ships';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadShips();
    }

    bindEvents() {
        // Add ship form
        document.getElementById('addShipForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addShip();
        });

        // Edit ship form
        document.getElementById('editShipForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateShip();
        });

        // Modal close events
        document.querySelector('.close').addEventListener('click', () => this.closeModal());
        document.getElementById('cancelEdit').addEventListener('click', () => this.closeModal());
        
        // Close modal when clicking outside
        document.getElementById('editModal').addEventListener('click', (e) => {
            if (e.target.id === 'editModal') {
                this.closeModal();
            }
        });
    }

    async loadShips() {
        try {
            const response = await fetch(this.apiBase);
            const ships = await response.json();
            this.displayShips(ships);
        } catch (error) {
            console.error('Error loading ships:', error);
            this.showError('Failed to load ships');
        }
    }

    displayShips(ships) {
        const container = document.getElementById('shipsList');
        
        if (ships.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No Ships in Fleet</h3>
                    <p>Add your first ship to get started</p>
                </div>
            `;
            return;
        }

        container.innerHTML = ships.map(ship => `
            <div class="ship-card" data-ship-id="${ship.id}">
                <h3>${this.escapeHtml(ship.name)}</h3>
                <div class="ship-info">
                    <div class="ship-info-item">
                        <span class="ship-info-label">ID:</span>
                        <span class="ship-info-value">#${ship.id}</span>
                    </div>
                    <div class="ship-info-item">
                        <span class="ship-info-label">Displacement:</span>
                        <span class="ship-info-value">${ship.displacement} tons</span>
                    </div>
                    <div class="ship-info-item">
                        <span class="ship-info-label">Home Port:</span>
                        <span class="ship-info-value">${this.escapeHtml(ship.port)}</span>
                    </div>
                    <div class="ship-info-item">
                        <span class="ship-info-label">Captain:</span>
                        <span class="ship-info-value">${this.escapeHtml(ship.captain)}</span>
                    </div>
                    <div class="ship-info-item">
                        <span class="ship-info-label">Berth Number:</span>
                        <span class="ship-info-value">${ship.berth_num}</span>
                    </div>
                    <div class="ship-info-item">
                        <span class="ship-info-label">Destination:</span>
                        <span class="ship-info-value">${this.escapeHtml(ship.target)}</span>
                    </div>
                </div>
                <div class="ship-actions">
                    <button class="btn btn-secondary" onclick="shipManager.editShip(${ship.id})">
                        Edit
                    </button>
                    <button class="btn btn-danger" onclick="shipManager.deleteShip(${ship.id})">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    async addShip() {
        const form = document.getElementById('addShipForm');
        const formData = new FormData(form);
        
        const shipData = {
            name: formData.get('name'),
            displacement: parseFloat(formData.get('displacement')),
            port: formData.get('port'),
            captain: formData.get('captain'),
            berth_num: parseInt(formData.get('berth_num')),
            target: formData.get('target')
        };

        try {
            const response = await fetch(this.apiBase, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(shipData)
            });

            if (response.ok) {
                form.reset();
                this.loadShips();
                this.showMessage('Ship added successfully!', 'success');
            } else {
                throw new Error('Failed to add ship');
            }
        } catch (error) {
            console.error('Error adding ship:', error);
            this.showError('Failed to add ship');
        }
    }

    async editShip(shipId) {
        try {
            const response = await fetch(`${this.apiBase}/${shipId}`);
            const ship = await response.json();

            document.getElementById('editId').value = ship.id;
            document.getElementById('editName').value = ship.name;
            document.getElementById('editDisplacement').value = ship.displacement;
            document.getElementById('editPort').value = ship.port;
            document.getElementById('editCaptain').value = ship.captain;
            document.getElementById('editBerthNum').value = ship.berth_num;
            document.getElementById('editTarget').value = ship.target;

            this.openModal();
        } catch (error) {
            console.error('Error loading ship for edit:', error);
            this.showError('Failed to load ship data');
        }
    }

    async updateShip() {
        const shipId = document.getElementById('editId').value;
        const form = document.getElementById('editShipForm');
        const formData = new FormData(form);
        
        const shipData = {
            name: formData.get('name'),
            displacement: parseFloat(formData.get('displacement')),
            port: formData.get('port'),
            captain: formData.get('captain'),
            berth_num: parseInt(formData.get('berth_num')),
            target: formData.get('target')
        };

        try {
            const response = await fetch(`${this.apiBase}/${shipId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(shipData)
            });

            if (response.ok) {
                this.closeModal();
                this.loadShips();
                this.showMessage('Ship updated successfully!', 'success');
            } else {
                throw new Error('Failed to update ship');
            }
        } catch (error) {
            console.error('Error updating ship:', error);
            this.showError('Failed to update ship');
        }
    }

    async deleteShip(shipId) {
        if (!confirm('Are you sure you want to delete this ship?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/${shipId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.loadShips();
                this.showMessage('Ship deleted successfully!', 'success');
            } else {
                throw new Error('Failed to delete ship');
            }
        } catch (error) {
            console.error('Error deleting ship:', error);
            this.showError('Failed to delete ship');
        }
    }

    openModal() {
        document.getElementById('editModal').style.display = 'block';
    }

    closeModal() {
        document.getElementById('editModal').style.display = 'none';
    }

    showMessage(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? 'var(--green)' : 'var(--red)'};
            color: var(--navy-dark);
            border-radius: 8px;
            font-weight: bold;
            z-index: 1001;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize the ship manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.shipManager = new ShipManager();
});

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);