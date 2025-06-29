// Terminal-style code block enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize terminal-style code blocks
    initializeTerminalBlocks();
    
    // Initialize copy functionality
    initializeCopyButtons();
    
    // Initialize syntax highlighting for terminal commands
    initializeTerminalSyntax();
});

function initializeTerminalBlocks() {
    // Convert bash/shell code blocks to terminal style
    const codeBlocks = document.querySelectorAll('pre code.language-bash, pre code.language-shell, pre code.language-terminal');
    
    codeBlocks.forEach(block => {
        const pre = block.parentElement;
        const container = pre.parentElement;
        
        // Add terminal class if not already present
        if (!container.classList.contains('terminal-block')) {
            container.classList.add('terminal-block');
        }
        
        // Process terminal content
        processTerminalContent(block);
    });
}

function processTerminalContent(codeElement) {
    const content = codeElement.textContent;
    const lines = content.split('\n');
    let processedContent = '';
    
    lines.forEach(line => {
        if (line.trim() === '') {
            processedContent += '\n';
            return;
        }
        
        // Handle different line types
        if (line.startsWith('$') || line.startsWith('#')) {
            // Command prompt
            const prompt = line.charAt(0);
            const command = line.substring(1).trim();
            processedContent += `<span class="terminal-prompt">${prompt}</span> <span class="terminal-command">${command}</span>\n`;
        } else if (line.startsWith('//') || line.startsWith('#')) {
            // Comments
            processedContent += `<span class="terminal-comment">${line}</span>\n`;
        } else if (line.includes('"') || line.includes("'")) {
            // Lines with strings
            processedContent += highlightStrings(line) + '\n';
        } else {
            // Regular output
            processedContent += `<span class="terminal-output">${line}</span>\n`;
        }
    });
    
    codeElement.innerHTML = processedContent;
}

function highlightStrings(line) {
    // Simple string highlighting
    return line.replace(/(["'])((?:\\.|(?!\1)[^\\])*)\1/g, '<span class="terminal-string">$1$2$1</span>');
}

function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const codeBlock = this.closest('.code-block, .terminal-block');
            const code = codeBlock.querySelector('code');
            
            // Get clean text content (without HTML tags)
            const textContent = getCleanTextContent(code);
            
            // Copy to clipboard
            navigator.clipboard.writeText(textContent).then(() => {
                // Visual feedback
                const originalText = this.textContent;
                this.textContent = '✓ Copied!';
                this.style.background = 'var(--success-color)';
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = 'var(--primary-color)';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy: ', err);
                // Fallback for older browsers
                fallbackCopyTextToClipboard(textContent, this);
            });
        });
    });
}

function getCleanTextContent(element) {
    // Create a temporary element to get clean text
    const temp = document.createElement('div');
    temp.innerHTML = element.innerHTML;
    
    // Remove terminal styling spans but keep the content
    const spans = temp.querySelectorAll('span');
    spans.forEach(span => {
        span.replaceWith(span.textContent);
    });
    
    return temp.textContent || temp.innerText || '';
}

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
            const originalText = button.textContent;
            button.textContent = '✓ Copied!';
            button.style.background = 'var(--success-color)';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = 'var(--primary-color)';
            }, 2000);
        }
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }
    
    document.body.removeChild(textArea);
}

function initializeTerminalSyntax() {
    // Add syntax highlighting for common terminal commands
    const terminalBlocks = document.querySelectorAll('.terminal-block code');
    
    terminalBlocks.forEach(block => {
        highlightTerminalSyntax(block);
    });
}

function highlightTerminalSyntax(element) {
    let content = element.innerHTML;
    
    // Highlight common commands
    const commands = ['npm', 'yarn', 'git', 'cd', 'ls', 'mkdir', 'rm', 'cp', 'mv', 'chmod', 'sudo', 'pip', 'python', 'node', 'curl', 'wget'];
    
    commands.forEach(cmd => {
        const regex = new RegExp(`\\b${cmd}\\b`, 'g');
        content = content.replace(regex, `<span class="terminal-keyword">${cmd}</span>`);
    });
    
    // Highlight flags (starting with -)
    content = content.replace(/\s(-{1,2}[a-zA-Z0-9-]+)/g, ' <span class="terminal-flag">$1</span>');
    
    element.innerHTML = content;
}

// Add CSS for terminal flags
const style = document.createElement('style');
style.textContent = `
.terminal-flag {
    color: var(--terminal-string);
    font-weight: 500;
}

.terminal-output {
    color: var(--text-secondary);
}

/* Smooth transitions for copy button */
.copy-btn {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Terminal cursor animation */
@keyframes terminal-cursor {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}

.terminal-cursor::after {
    content: '▋';
    animation: terminal-cursor 1s infinite;
    color: var(--terminal-prompt);
}
`;
document.head.appendChild(style);