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
