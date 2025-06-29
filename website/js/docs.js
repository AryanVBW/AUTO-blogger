// Documentation-specific JavaScript functionality

// Initialize documentation features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeCodeCopy();
    initializeSmoothScrolling();
    initializeTableOfContents();
    initializeSearchHighlight();
    initializeProgressIndicator();
});

// Tab functionality for installation instructions
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('onclick')?.match(/showTab\('(.+)'\)/)?.[1];
            if (targetTab) {
                showTab(targetTab);
            }
        });
    });
}

// Show specific tab content
function showTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show target tab content
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.add('active');
    }
    
    // Add active class to clicked button
    const targetButton = document.querySelector(`[onclick*="showTab('${tabId}')"]`);
    if (targetButton) {
        targetButton.classList.add('active');
    }
}

// Code copying functionality
function initializeCodeCopy() {
    // Add copy functionality to all copy buttons
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', function() {
            copyCode(this);
        });
    });
}

// Copy code to clipboard
function copyCode(button) {
    const codeBlock = button.closest('.code-block');
    const code = codeBlock.querySelector('code');
    
    if (code) {
        const text = code.textContent || code.innerText;
        
        // Use modern clipboard API if available
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                showCopyFeedback(button, 'Copied!');
            }).catch(err => {
                console.error('Failed to copy: ', err);
                fallbackCopyTextToClipboard(text, button);
            });
        } else {
            fallbackCopyTextToClipboard(text, button);
        }
    }
}

// Fallback copy method for older browsers
function fallbackCopyTextToClipboard(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopyFeedback(button, 'Copied!');
        } else {
            showCopyFeedback(button, 'Copy failed');
        }
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
        showCopyFeedback(button, 'Copy failed');
    }
    
    document.body.removeChild(textArea);
}

// Show copy feedback
function showCopyFeedback(button, message) {
    const originalText = button.textContent;
    button.textContent = message;
    button.style.background = message === 'Copied!' ? '#4caf50' : '#f44336';
    
    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '';
    }, 2000);
}

// Special copy function for installation code
function copyInstallCode() {
    const code = document.getElementById('quick-install-code');
    if (code) {
        const text = code.textContent || code.innerText;
        
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                // Find the copy button and show feedback
                const button = document.querySelector('#quick-install-code').closest('.code-block').querySelector('.copy-btn');
                if (button) {
                    showCopyFeedback(button, 'Copied!');
                }
            });
        } else {
            fallbackCopyTextToClipboard(text, null);
        }
    }
}

// Smooth scrolling for navigation links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                const headerOffset = 100;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL without triggering scroll
                history.pushState(null, null, href);
                
                // Highlight the target section briefly
                highlightSection(target);
            }
        });
    });
}

// Highlight section when navigated to
function highlightSection(element) {
    element.style.background = 'rgba(var(--primary-rgb), 0.1)';
    element.style.transition = 'background 0.3s ease';
    
    setTimeout(() => {
        element.style.background = '';
    }, 2000);
}

// Generate table of contents dynamically
function initializeTableOfContents() {
    const sidebar = document.querySelector('.docs-nav ul');
    const sections = document.querySelectorAll('.docs-section');
    
    if (!sidebar || sections.length === 0) return;
    
    // Clear existing navigation if needed
    const existingLinks = sidebar.querySelectorAll('a');
    const hasCustomNav = Array.from(existingLinks).some(link => 
        link.getAttribute('href')?.startsWith('#')
    );
    
    if (!hasCustomNav) {
        sidebar.innerHTML = '';
        
        sections.forEach(section => {
            const heading = section.querySelector('h2');
            if (heading) {
                const id = section.id || heading.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-');
                section.id = id;
                
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = `#${id}`;
                a.textContent = heading.textContent;
                li.appendChild(a);
                sidebar.appendChild(li);
            }
        });
    }
}

// Search and highlight functionality
function initializeSearchHighlight() {
    // Check if there's a search query in URL
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search');
    
    if (searchQuery) {
        highlightSearchTerms(searchQuery);
    }
}

// Highlight search terms in content
function highlightSearchTerms(query) {
    const content = document.querySelector('.docs-content');
    if (!content) return;
    
    const walker = document.createTreeWalker(
        content,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    const textNodes = [];
    let node;
    
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    
    const regex = new RegExp(`(${query})`, 'gi');
    
    textNodes.forEach(textNode => {
        const parent = textNode.parentNode;
        if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') return;
        
        const text = textNode.textContent;
        if (regex.test(text)) {
            const highlightedHTML = text.replace(regex, '<mark class="search-highlight">$1</mark>');
            const wrapper = document.createElement('span');
            wrapper.innerHTML = highlightedHTML;
            parent.replaceChild(wrapper, textNode);
        }
    });
    
    // Add CSS for search highlights
    if (!document.querySelector('#search-highlight-styles')) {
        const style = document.createElement('style');
        style.id = 'search-highlight-styles';
        style.textContent = `
            .search-highlight {
                background: #ffeb3b;
                color: #000;
                padding: 0.1em 0.2em;
                border-radius: 2px;
                font-weight: bold;
            }
        `;
        document.head.appendChild(style);
    }
}

// Reading progress indicator
function initializeProgressIndicator() {
    const progressBar = createProgressBar();
    
    window.addEventListener('scroll', () => {
        updateProgressBar(progressBar);
        updateActiveNavItem();
    });
}

// Create progress bar element
function createProgressBar() {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.innerHTML = '<div class="reading-progress-fill"></div>';
    
    // Add CSS for progress bar
    if (!document.querySelector('#progress-bar-styles')) {
        const style = document.createElement('style');
        style.id = 'progress-bar-styles';
        style.textContent = `
            .reading-progress {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: rgba(0, 0, 0, 0.1);
                z-index: 1000;
            }
            .reading-progress-fill {
                height: 100%;
                background: var(--primary-color);
                width: 0%;
                transition: width 0.1s ease;
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(progressBar);
    return progressBar;
}

// Update progress bar based on scroll position
function updateProgressBar(progressBar) {
    const content = document.querySelector('.docs-content');
    if (!content) return;
    
    const contentRect = content.getBoundingClientRect();
    const contentHeight = content.offsetHeight;
    const viewportHeight = window.innerHeight;
    const scrolled = Math.max(0, -contentRect.top);
    const maxScroll = contentHeight - viewportHeight;
    
    if (maxScroll > 0) {
        const progress = Math.min(100, (scrolled / maxScroll) * 100);
        const fill = progressBar.querySelector('.reading-progress-fill');
        if (fill) {
            fill.style.width = `${progress}%`;
        }
    }
}

// Update active navigation item based on scroll position
function updateActiveNavItem() {
    const sections = document.querySelectorAll('.docs-section');
    const navLinks = document.querySelectorAll('.docs-nav a');
    
    let currentSection = '';
    
    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top <= 150 && rect.bottom >= 150) {
            currentSection = section.id;
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search (if implemented)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Implement search functionality here
        console.log('Search shortcut triggered');
    }
    
    // Arrow keys for navigation between sections
    if (e.altKey) {
        const currentSection = document.querySelector('.docs-section:target') || 
                              document.querySelector('.docs-section');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            const nextSection = currentSection?.nextElementSibling;
            if (nextSection && nextSection.classList.contains('docs-section')) {
                nextSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            const prevSection = currentSection?.previousElementSibling;
            if (prevSection && prevSection.classList.contains('docs-section')) {
                prevSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }
});

// Print functionality
function printDocumentation() {
    window.print();
}

// Export functionality (if needed)
function exportDocumentation(format = 'html') {
    const content = document.querySelector('.docs-content');
    if (!content) return;
    
    switch (format) {
        case 'html':
            const htmlContent = content.outerHTML;
            downloadFile('documentation.html', htmlContent, 'text/html');
            break;
        case 'text':
            const textContent = content.innerText;
            downloadFile('documentation.txt', textContent, 'text/plain');
            break;
        default:
            console.warn('Unsupported export format:', format);
    }
}

// Download file helper
function downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Utility function to debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize responsive behavior
function initializeResponsiveBehavior() {
    const sidebar = document.querySelector('.docs-sidebar');
    const content = document.querySelector('.docs-content');
    
    if (!sidebar || !content) return;
    
    function handleResize() {
        if (window.innerWidth <= 1024) {
            // Mobile behavior
            sidebar.style.position = 'static';
        } else {
            // Desktop behavior
            sidebar.style.position = 'sticky';
        }
    }
    
    window.addEventListener('resize', debounce(handleResize, 250));
    handleResize(); // Initial call
}

// Initialize all responsive behaviors
document.addEventListener('DOMContentLoaded', function() {
    initializeResponsiveBehavior();
});

// Error handling for missing elements
function handleMissingElements() {
    const requiredElements = ['.docs-content', '.docs-nav'];
    
    requiredElements.forEach(selector => {
        if (!document.querySelector(selector)) {
            console.warn(`Required element not found: ${selector}`);
        }
    });
}

// Initialize error handling
document.addEventListener('DOMContentLoaded', handleMissingElements);

// Global functions for inline event handlers
window.showTab = showTab;
window.copyCode = copyCode;
window.copyInstallCode = copyInstallCode;
window.printDocumentation = printDocumentation;
window.exportDocumentation = exportDocumentation;