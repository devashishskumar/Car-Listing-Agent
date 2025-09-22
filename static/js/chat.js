// Chat Interface JavaScript

class ChatInterface {
    constructor() {
        this.userId = this.generateUserId();
        this.isTyping = false;
        this.initializeElements();
        this.setupEventListeners();
        this.startConversation();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.quickActions = document.getElementById('quickActions');
        this.listingsModal = document.getElementById('listingsModal');
        this.listingsContainer = document.getElementById('listingsContainer');
    }

    setupEventListeners() {
        // Send button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter key to send, Shift+Enter for new line
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.updateCharCount();
            this.updateSendButton();
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.messageInput.value = message;
                this.sendMessage();
            });
        });

        // New chat button
        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.startNewChat();
        });

        // Search mode button
        document.getElementById('searchModeBtn').addEventListener('click', () => {
            window.location.href = '/';
        });

        // Modal close
        document.addEventListener('click', (e) => {
            if (e.target === this.listingsModal) {
                this.closeListingsModal();
            }
        });
    }

    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }

    async startConversation() {
        try {
            const response = await fetch('/start-conversation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: this.userId })
            });

            const data = await response.json();
            if (data.success) {
                this.addMessage('assistant', data.welcome_message);
            }
        } catch (error) {
            console.error('Error starting conversation:', error);
            this.addMessage('assistant', "Hi! I'm your car buying assistant. How can I help you find your perfect car?");
        }
    }

    startNewChat() {
        this.chatMessages.innerHTML = '';
        this.userId = this.generateUserId();
        this.startConversation();
        this.showQuickActions();
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    updateCharCount() {
        const count = this.messageInput.value.length;
        document.querySelector('.char-count').textContent = `${count}/500`;
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();
        this.updateCharCount();
        this.updateSendButton();

        // Hide quick actions
        this.hideQuickActions();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.userId
                })
            });

            const data = await response.json();
            this.hideTypingIndicator();

            if (data.success) {
                // Add assistant response
                this.addMessage('assistant', data.response);

                // If it's a search request, show results
                if (data.type === 'search_request' && data.listings) {
                    this.showSearchResults(data);
                    
                    // Add follow-up message if available
                    if (data.follow_up) {
                        setTimeout(() => {
                            this.addMessage('assistant', data.follow_up);
                        }, 1000);
                    }
                } else if (data.search_error) {
                    this.addMessage('assistant', data.search_error);
                }

                // Show quick actions for general conversation
                if (data.type === 'conversation') {
                    setTimeout(() => this.showQuickActions(), 1000);
                }
            } else {
                this.addMessage('assistant', "I'm sorry, I encountered an error. Please try again.");
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('assistant', "I'm having trouble connecting. Please check your internet connection and try again.");
        }
    }

    addMessage(role, content, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role} new-message`;
        
        const time = timestamp || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        const avatar = role === 'user' ? 'U' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                ${this.formatMessage(content)}
                <div class="message-time">${time}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Remove new-message class after animation
        setTimeout(() => {
            messageDiv.classList.remove('new-message');
        }, 500);
    }

    formatMessage(content) {
        // Convert line breaks to HTML
        return content.replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
    }

    showQuickActions() {
        this.quickActions.style.display = 'block';
        this.quickActions.classList.add('slide-up');
    }

    hideQuickActions() {
        this.quickActions.style.display = 'none';
    }

    showSearchResults(data) {
        if (data.listings && data.listings.length > 0) {
            this.listingsContainer.innerHTML = '';
            
            data.listings.forEach((listing, index) => {
                const listingEl = this.createListingElement(listing, index + 1);
                this.listingsContainer.appendChild(listingEl);
            });

            // Add analysis if available
            if (data.analysis) {
                const analysisDiv = document.createElement('div');
                analysisDiv.className = 'analysis-section';
                analysisDiv.innerHTML = `
                    <h4><i class="fas fa-brain"></i> AI Analysis</h4>
                    <div class="analysis-content">${this.formatMessage(data.analysis)}</div>
                `;
                this.listingsContainer.appendChild(analysisDiv);
            }

            this.listingsModal.style.display = 'flex';
        }
    }

    createListingElement(listing, index) {
        const listingEl = document.createElement('div');
        listingEl.className = 'car-listing';
        
        const titleElement = listing.url && listing.url !== 'N/A' 
            ? `<a href="${listing.url}" target="_blank" rel="noopener noreferrer" class="listing-title-link">
                 ${listing.title} 
                 <i class="fas fa-external-link-alt"></i>
               </a>`
            : `<div class="listing-title">${listing.title}</div>`;
        
        listingEl.innerHTML = `
            <div class="listing-header">
                ${titleElement}
                <div class="listing-price">${listing.price}</div>
            </div>
            <div class="listing-details">
                <div class="listing-detail">
                    <i class="fas fa-road"></i>
                    <span>${listing.mileage}</span>
                </div>
                <div class="listing-detail">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${listing.location}</span>
                </div>
                <div class="listing-source">
                    <i class="fas fa-globe"></i>
                    <span class="source-badge">${listing.source}</span>
                    ${listing.url && listing.url !== 'N/A' 
                        ? `<a href="${listing.url}" target="_blank" rel="noopener noreferrer" class="view-listing-btn">
                             <i class="fas fa-eye"></i> View Listing
                           </a>`
                        : ''
                    }
                </div>
            </div>
        `;
        return listingEl;
    }

    closeListingsModal() {
        this.listingsModal.style.display = 'none';
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Global function for modal close
function closeListingsModal() {
    window.chatInterface.closeListingsModal();
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatInterface = new ChatInterface();
    
    // Add some nice console styling
    console.log('%c🚗 Car Chat Agent', 'color: #667eea; font-size: 20px; font-weight: bold;');
    console.log('%cChat interface loaded successfully! 🚀', 'color: #764ba2; font-size: 14px;');
});

// Add CSS for analysis section
const analysisStyles = `
<style>
.analysis-section {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1rem;
    border: 2px solid #dee2e6;
}

.analysis-section h4 {
    color: #333;
    margin-bottom: 0.75rem;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.analysis-section h4 i {
    color: #667eea;
}

.analysis-content {
    color: #495057;
    line-height: 1.6;
    font-size: 0.875rem;
}

.slide-up {
    animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', analysisStyles);

