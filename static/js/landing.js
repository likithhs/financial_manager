/**
 * FinAI Landing Page Micro-Interactions & UI Controls
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

  // 3. Interactive AI Chat Mockup Demo on Landing Page
  const chatInput = document.getElementById('landingChatInput');
  const chatSendBtn = document.getElementById('landingChatSend');
  const chatMessages = document.getElementById('landingChatMessages');
  const chips = document.querySelectorAll('.chat-suggestions .chip');

  const botResponses = {
    "Analyze my financial health": "Your current financial health score is 78/100 (Good). Your savings rate is healthy at 45.4%, but your emergency fund has only 2.1 months of expenses. I suggest prioritizing ₹10,000 to your emergency reserve before high-risk equity.",
    "Show my expenses": "This month your total expenses are ₹46,350 across: Rent (₹20,000), Food & Dining (₹12,450), Transport (₹4,500), Utilities (₹5,400), and Entertainment (₹4,000). Food is 14% higher than last month.",
    "How much can I save?": "With ₹85,000 income and ₹46,350 projected expenses, your investable cash surplus this month is ₹38,650.",
    "Can I afford to invest?": "Based on your current income (₹85,000), expenses (₹46,350), and emergency reserves, you can safely invest up to ₹15,000 in low-to-moderate risk Index Funds/ETFs this month without risking cash liquidity.",
    "Show my goals": "You have 2 active goals: 1) 'Buy a Laptop' (₹45,000 / ₹80,000 - 56% complete, On Track) and 2) 'Emergency Fund' (₹1,00,000 / ₹3,00,000 - 33% complete).",
    "What's happening in the market?": "NIFTY 50 is trading at 24,850.30 (+0.58%) and SENSEX is at 81,420.75 (+0.59%). Large-cap IT and Banking sectors are showing positive momentum today.",
    "Explain mutual funds": "A Mutual Fund pools money from many investors to purchase a diversified basket of stocks, bonds, or money market instruments managed by professional portfolio managers."
  };

  function sendLandingDemoMessage(text) {
    if (!text || !chatMessages) return;

    // Add User Message
    const userRow = document.createElement('div');
    userRow.className = 'message-row user';
    userRow.innerHTML = `
      <div class="message-bubble">
        <p>${escapeHtml(text)}</p>
      </div>
    `;
    chatMessages.appendChild(userRow);

    if (chatInput) chatInput.value = '';

    // Scroll chat to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Simulate typing delay
    setTimeout(() => {
      const responseText = botResponses[text] || `FinAI Assistant: Analyzing your query "${text}" against current cashflow and risk metrics... In full mode, I calculate personalized recommendations directly from your database.`;
      
      const aiRow = document.createElement('div');
      aiRow.className = 'message-row ai';
      aiRow.innerHTML = `
        <div class="chat-avatar" style="width: 32px; height: 32px; font-size: 0.85rem; flex-shrink: 0;">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div class="message-bubble">
          <p>${responseText}</p>
        </div>
      `;
      chatMessages.appendChild(aiRow);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 600);
  }

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const promptText = chip.innerText.replace(/^[✨🔍💰📊🛡️📈\s]+/, '').trim();
      sendLandingDemoMessage(promptText);
    });
  });

  if (chatSendBtn && chatInput) {
    chatSendBtn.addEventListener('click', () => {
      const val = chatInput.value.trim();
      if (val) sendLandingDemoMessage(val);
    });

    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const val = chatInput.value.trim();
        if (val) sendLandingDemoMessage(val);
      }
    });
  }

  function escapeHtml(string) {
    const div = document.createElement('div');
    div.innerText = string;
    return div.innerHTML;
  }

  // 4. Live ScrollSpy: Section Tracking in Top Navbar with Electric Blue Glow
  const navSections = [
    document.getElementById('home'),
    document.getElementById('features'),
    document.getElementById('how-it-works'),
    document.getElementById('ai'),
    document.getElementById('security')
  ].filter(Boolean);

  const headerNavItems = document.querySelectorAll('.nav-links .nav-link-item[href^="#"]');

  function updateActiveNavSection() {
    if (!navSections.length || !headerNavItems.length) return;

    const scrollPos = window.scrollY + 140; // Offset for fixed navbar

    let currentSectionId = '';
    navSections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      if (scrollPos >= top && scrollPos < top + height) {
        currentSectionId = section.getAttribute('id');
      }
    });

    // Special check if reached very bottom of page
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 50) {
      currentSectionId = navSections[navSections.length - 1].getAttribute('id');
    }

    if (currentSectionId) {
      headerNavItems.forEach(link => {
        if (link.getAttribute('href') === `#${currentSectionId}`) {
          link.classList.add('active');
        } else {
          link.classList.remove('active');
        }
      });
    }
  }

  window.addEventListener('scroll', updateActiveNavSection, { passive: true });
  updateActiveNavSection(); // Initial check on load

  // Smooth in-page scrolling with navbar offset
  headerNavItems.forEach(link => {
    link.addEventListener('click', function(e) {
      const targetHash = this.getAttribute('href');
      if (targetHash && targetHash.startsWith('#')) {
        const targetElement = document.querySelector(targetHash);
        if (targetElement) {
          e.preventDefault();
          const navOffset = 80;
          const targetTop = Math.max(0, targetElement.offsetTop - navOffset);
          window.scrollTo({
            top: targetTop,
            behavior: 'smooth'
          });
        }
      }
    });
  });
});
