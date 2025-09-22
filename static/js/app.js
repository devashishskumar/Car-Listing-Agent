// Car Listing Agent - Frontend JavaScript

class CarListingApp {
    constructor() {
        this.initializeEventListeners();
        this.setupKeyboardShortcuts();
    }

    initializeEventListeners() {
        // Search button click
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.performSearch();
        });

        // Enter key in search input
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Example tag clicks
        document.querySelectorAll('.example-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                const query = tag.getAttribute('data-query');
                document.getElementById('searchInput').value = query;
                this.performSearch();
            });
        });

        // Search input focus effects
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('focus', () => {
            searchInput.parentElement.style.transform = 'scale(1.02)';
        });

        searchInput.addEventListener('blur', () => {
            searchInput.parentElement.style.transform = 'scale(1)';
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
            
            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                document.getElementById('searchInput').focus();
            }
        });
    }

    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        this.showLoading();
        this.hideResults();
        this.hideError();

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || 'An error occurred while searching');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        document.getElementById('loadingIndicator').style.display = 'block';
        document.getElementById('searchBtn').disabled = true;
        document.getElementById('searchBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Searching...</span>';
    }

    hideLoading() {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('searchBtn').disabled = false;
        document.getElementById('searchBtn').innerHTML = '<i class="fas fa-search"></i><span>Search</span>';
    }

    displayResults(data) {
        // Show enhanced query
        const enhancedQueryEl = document.getElementById('enhancedQuery');
        enhancedQueryEl.textContent = `"${data.enhanced_query}"`;

        // Show results count
        const resultsCountEl = document.getElementById('resultsCount');
        resultsCountEl.textContent = `Found ${data.total_found} car listing${data.total_found !== 1 ? 's' : ''}`;

        // Display listings
        const listingsContainer = document.getElementById('listingsContainer');
        listingsContainer.innerHTML = '';

        if (data.listings && data.listings.length > 0) {
            data.listings.forEach((listing, index) => {
                const listingEl = this.createListingElement(listing, index + 1);
                listingsContainer.appendChild(listingEl);
            });
        } else {
            listingsContainer.innerHTML = '<p class="no-results">No listings found. Try adjusting your search criteria.</p>';
        }

        // Display AI analysis
        const analysisContent = document.getElementById('analysisContent');
        analysisContent.innerHTML = this.formatAnalysis(data.analysis);

        // Show results section
        document.getElementById('resultsSection').style.display = 'block';

        // Smooth scroll to results
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    createListingElement(listing, index) {
        const listingEl = document.createElement('div');
        listingEl.className = 'car-listing';
        
        // Create clickable title if URL is available
        const titleElement = listing.url && listing.url !== 'N/A' 
            ? `<a href="${listing.url}" target="_blank" rel="noopener noreferrer" class="listing-title-link">
                 ${listing.title} 
                 <i class="fas fa-external-link-alt external-link-icon"></i>
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

    formatAnalysis(analysis) {
        // Split analysis into paragraphs and format
        const paragraphs = analysis.split('\n\n').filter(p => p.trim());
        return paragraphs.map(paragraph => {
            const trimmed = paragraph.trim();
            if (trimmed.startsWith('1.') || trimmed.startsWith('2.') || trimmed.startsWith('3.') || 
                trimmed.startsWith('4.') || trimmed.startsWith('5.')) {
                return `<p><strong>${trimmed}</strong></p>`;
            }
            return `<p>${trimmed}</p>`;
        }).join('');
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
        
        // Smooth scroll to error
        errorSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'center'
        });
    }

    hideError() {
        document.getElementById('errorSection').style.display = 'none';
    }

    hideResults() {
        document.getElementById('resultsSection').style.display = 'none';
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
}

// Modal functions
function showAbout() {
    document.getElementById('aboutModal').style.display = 'flex';
}

function showHelp() {
    document.getElementById('helpModal').style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function hideError() {
    document.getElementById('errorSection').style.display = 'none';
}

// Close modals when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// Utility functions
function formatPrice(priceStr) {
    // Extract numbers from price string and format
    const numbers = priceStr.replace(/[^0-9]/g, '');
    if (numbers) {
        return `$${parseInt(numbers).toLocaleString()}`;
    }
    return priceStr;
}

function formatMileage(mileageStr) {
    // Extract numbers from mileage string and format
    const numbers = mileageStr.replace(/[^0-9]/g, '');
    if (numbers) {
        return `${parseInt(numbers).toLocaleString()} miles`;
    }
    return mileageStr;
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CarListingApp();
    
    // Add some nice animations
    const elements = document.querySelectorAll('.car-listing, .ai-analysis, .enhanced-query');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });

    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add typing animation to search placeholder
    const searchInput = document.getElementById('searchInput');
    const placeholders = [
        'What kind of car are you looking for?',
        'Honda Civic under $20,000',
        'BMW X3 with low mileage',
        'Toyota Camry 2020 or newer',
        'Electric car under $30,000'
    ];
    
    let placeholderIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    
    function typePlaceholder() {
        const currentPlaceholder = placeholders[placeholderIndex];
        
        if (isDeleting) {
            searchInput.placeholder = currentPlaceholder.substring(0, charIndex - 1);
            charIndex--;
        } else {
            searchInput.placeholder = currentPlaceholder.substring(0, charIndex + 1);
            charIndex++;
        }
        
        if (!isDeleting && charIndex === currentPlaceholder.length) {
            setTimeout(() => { isDeleting = true; }, 2000);
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            placeholderIndex = (placeholderIndex + 1) % placeholders.length;
        }
        
        setTimeout(typePlaceholder, isDeleting ? 50 : 100);
    }
    
    // Start typing animation only if input is not focused
    searchInput.addEventListener('focus', () => {
        searchInput.placeholder = 'What kind of car are you looking for?';
    });
    
    searchInput.addEventListener('blur', () => {
        if (!searchInput.value) {
            typePlaceholder();
        }
    });
    
    // Start the animation
    typePlaceholder();
});

// Add some console styling for fun
console.log('%c🚗 Car Listing Agent', 'color: #667eea; font-size: 20px; font-weight: bold;');
console.log('%cWelcome to the Car Listing Agent! 🚀', 'color: #764ba2; font-size: 14px;');
console.log('%cBuilt with ❤️ using Flask, OpenAI, and modern web technologies', 'color: #6c757d; font-size: 12px;');

