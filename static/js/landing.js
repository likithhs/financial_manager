/**
 * Finora Landing Page Micro-Interactions & UI Controls
 * Infosys-Style Interactive Solution Filter & Chat Demo
 */
document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const menuToggle = document.getElementById('mobileMenuToggle');
  const navLinks = document.getElementById('navLinks');

  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
      if (navLinks.style.display === 'flex') {
        navLinks.style.display = 'none';
      } else {
        navLinks.style.display = 'flex';
        navLinks.style.flexDirection = 'column';
        navLinks.style.position = 'absolute';
        navLinks.style.top = '100%';
        navLinks.style.left = '0';
        navLinks.style.background = '#FAF7F0';
        navLinks.style.padding = '20px';
        navLinks.style.borderBottom = '1px solid #E5E7EB';
        navLinks.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.06)';
        navLinks.style.gap = '16px';
      }
    });
  }

  // 2. Infosys-Style Solution Category Filter Pills
  const filterPills = document.querySelectorAll('.corp-pill');
  const solutionCards = document.querySelectorAll('.corp-module-card');

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      // Set active pill
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      const filter = pill.getAttribute('data-filter');

      solutionCards.forEach(card => {
        const category = card.getAttribute('data-category');
        if (filter === 'all' || category === filter) {
          card.style.display = 'flex';
          card.style.animation = 'fadeInDown 0.3s ease-out';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // 3. Live Interactive Finora Demo Assistant on Public Dashboard
  const chatInput = document.getElementById('landingChatInput');
  const chatSendBtn = document.getElementById('landingChatSend');
  const chatMessages = document.getElementById('landingChatMessages');
  const chips = document.querySelectorAll('.chat-suggestions .chip');

  function formatMarkdown(text) {
    if (!text) return '';
    let html = escapeHtml(text);
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/^###\s*(.*$)/gim, '<h5 style="font-weight: 700; color: #111827; margin: 10px 0 4px; font-size: 0.95rem;">$1</h5>');
    html = html.replace(/^##\s*(.*$)/gim, '<h4 style="font-weight: 800; color: #111827; margin: 12px 0 6px; font-size: 1rem;">$1</h4>');
    html = html.replace(/^\s*[•*-]\s*(.*$)/gim, '<div style="display: flex; gap: 8px; margin: 4px 0;"><span style="color: #D97706; font-weight: bold;">•</span><span>$1</span></div>');
    html = html.replace(/^\s*(\d+)\.\s*(.*$)/gim, '<div style="display: flex; gap: 8px; margin: 4px 0;"><span style="font-weight: 700; color: #D97706;">$1.</span><span>$2</span></div>');
    html = html.replace(/\n\n/g, '<div style="height: 8px;"></div>');
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  async function sendLandingMessage(text) {
    if (!text || !chatMessages) return;

    // Add User Message bubble
    const userRow = document.createElement('div');
    userRow.className = 'message-row user';
    userRow.innerHTML = `
      <div class="message-bubble">
        <p>${escapeHtml(text)}</p>
      </div>
    `;
    chatMessages.appendChild(userRow);

    if (chatInput) {
      chatInput.value = '';
      chatInput.disabled = true;
    }
    if (chatSendBtn) {
      chatSendBtn.disabled = true;
      chatSendBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Show Typing Indicator
    const typingRow = document.createElement('div');
    typingRow.className = 'message-row ai';
    typingRow.id = 'landingChatTyping';
    typingRow.innerHTML = `
      <div class="chat-avatar" style="width: 32px; height: 32px; font-size: 0.85rem; flex-shrink: 0;">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="message-bubble" style="color: #6B7280; display: flex; align-items: center; gap: 8px;">
        <i class="fa-solid fa-spinner fa-spin" style="color: #D97706;"></i>
        <span>Finora Demo Assistant is preparing guidance...</span>
      </div>
    `;
    chatMessages.appendChild(typingRow);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    try {
      const response = await fetch('/ai-assistant/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ message: text })
      });

      const data = await response.json();

      const typingEl = document.getElementById('landingChatTyping');
      if (typingEl) typingEl.remove();

      const aiRow = document.createElement('div');
      aiRow.className = 'message-row ai';

      // If user is already authenticated, the endpoint returns 403 Forbidden
      if (response.status === 403 || (data && data.status === 'forbidden')) {
        aiRow.innerHTML = `
          <div class="chat-avatar" style="width: 32px; height: 32px; font-size: 0.85rem; flex-shrink: 0; background: #FEF3C7; color: #D97706; display: flex; align-items: center; justify-content: center; border-radius: 50%;">
            <i class="fa-solid fa-lock"></i>
          </div>
          <div class="message-bubble" style="border-left: 3px solid #D97706; background: #FFFBEB; padding: 14px 18px;">
            <div style="font-weight: 700; color: #92400E; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; font-size: 0.88rem;">
              <i class="fa-solid fa-circle-info"></i> Public Demo Only
            </div>
            <p style="margin: 0; color: #78350F; font-size: 0.86rem; line-height: 1.5;">
              The Finora Demo Assistant is strictly available on the public landing page for visitors exploring the application.
            </p>
          </div>
        `;
        chatMessages.appendChild(aiRow);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return;
      }

      let replyHtml = '';
      if (data && data.reply) {
        replyHtml = formatMarkdown(data.reply);
      } else {
        replyHtml = "I'm Finora's Demo Assistant. I can help you understand how to use Finora's features, such as expense tracking, budgeting, financial goals, investment tools, and financial reports. Please ask me how to use a feature within Finora.";
      }

      const providerBadge = `<div style="margin-bottom: 5px; font-size: 0.68rem; font-weight: 700; color: #D97706; text-transform: uppercase; display: flex; align-items: center; gap: 5px;">
        <i class="fa-solid fa-compass"></i> Finora Demo Assistant
      </div>`;

      aiRow.innerHTML = `
        <div class="chat-avatar" style="width: 32px; height: 32px; font-size: 0.85rem; flex-shrink: 0;">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div class="message-bubble">
          ${providerBadge}
          <div>${replyHtml}</div>
        </div>
      `;
      chatMessages.appendChild(aiRow);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (err) {
      console.error('Finora Demo Assistant Error:', err);
      const typingEl = document.getElementById('landingChatTyping');
      if (typingEl) typingEl.remove();

      const errRow = document.createElement('div');
      errRow.className = 'message-row ai';
      errRow.innerHTML = `
        <div class="chat-avatar" style="width: 32px; height: 32px; font-size: 0.85rem; flex-shrink: 0;">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div class="message-bubble" style="color: #DC2626;">
          <p>Could not connect to the Finora assistant server. Please check your connection.</p>
        </div>
      `;
      chatMessages.appendChild(errRow);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } finally {
      resetInputState();
    }
  }

  function resetInputState() {
    if (chatInput) {
      chatInput.disabled = false;
      chatInput.focus();
    }
    if (chatSendBtn) {
      chatSendBtn.disabled = false;
      chatSendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i>';
    }
  }

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const promptText = chip.innerText.replace(/^[✨🔍💰📊🛡️📈\s]+/, '').trim();
      sendLandingMessage(promptText);
    });
  });

  if (chatSendBtn && chatInput) {
    chatSendBtn.addEventListener('click', () => {
      const val = chatInput.value.trim();
      if (val) sendLandingMessage(val);
    });

    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const val = chatInput.value.trim();
        if (val) sendLandingMessage(val);
      }
    });
  }

  function escapeHtml(string) {
    const div = document.createElement('div');
    div.innerText = string;
    return div.innerHTML;
  }

  // 4. Live ScrollSpy: Section Tracking in Top Navbar with Active Indicator
  const navSectionIds = ['home', 'features', 'how-it-works', 'ai', 'security'];
  const navSections = navSectionIds
    .map(id => document.getElementById(id))
    .filter(Boolean);

  const headerNavItems = document.querySelectorAll('.fa-nav-menu .fa-nav-link[href^="#"], .nav-links .nav-link-item[href^="#"]');

  function setActiveLink(sectionId) {
    if (!sectionId || !headerNavItems.length) return;
    headerNavItems.forEach(link => {
      if (link.getAttribute('href') === `#${sectionId}`) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  function updateActiveNavSection() {
    if (!navSections.length || !headerNavItems.length) return;

    // Special check if reached bottom of page
    const isAtBottom = (window.innerHeight + window.scrollY) >= (document.documentElement.scrollHeight - 60);
    if (isAtBottom) {
      const lastId = navSections[navSections.length - 1].getAttribute('id');
      setActiveLink(lastId);
      return;
    }

    const scrollPos = window.scrollY + 160; // Offset for sticky navbar
    let currentSectionId = navSections[0].getAttribute('id');

    navSections.forEach(section => {
      const top = section.getBoundingClientRect().top + window.scrollY;
      if (scrollPos >= top) {
        currentSectionId = section.getAttribute('id');
      }
    });

    setActiveLink(currentSectionId);
  }

  window.addEventListener('scroll', updateActiveNavSection, { passive: true });
  updateActiveNavSection(); // Initial check on load

  // Smooth in-page scrolling with navbar offset
  document.querySelectorAll('.fa-nav-link[href^="#"], .fa-btn-demo[href^="#"], .nav-links .nav-link-item[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
      const targetHash = this.getAttribute('href');
      if (targetHash && targetHash.startsWith('#')) {
        const targetElement = document.querySelector(targetHash);
        if (targetElement) {
          e.preventDefault();
          const navOffset = document.querySelector('.fa-nav-wrapper')?.offsetHeight || 75;
          const targetTop = Math.max(0, targetElement.getBoundingClientRect().top + window.scrollY - navOffset);
          window.scrollTo({
            top: targetTop,
            behavior: 'smooth'
          });
          setActiveLink(targetElement.getAttribute('id'));

          // Close mobile menu if open
          if (navLinks && window.innerWidth <= 1024 && navLinks.style.display === 'flex') {
            navLinks.style.display = 'none';
          }
        }
      }
    });
  });
});
