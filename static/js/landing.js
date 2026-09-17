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

  // 3. Live Interactive AI Chat on Landing Page (Powered by FinAI Engine)
  const chatInput = document.getElementById('landingChatInput');
  const chatSendBtn = document.getElementById('landingChatSend');
  const chatMessages = document.getElementById('landingChatMessages');
  const chips = document.querySelectorAll('.chat-suggestions .chip');

  const DEMO_RESPONSES = [
    {
      keywords: ['health', 'score', 'pillar', 'diagnostic', 'analyze my financial health'],
      reply: `### 📊 FinAI 6-Pillar Health Diagnostic (Demo Preview)

Here is a sample preview of how FinAI continuously analyzes your financial vitals:

• **Savings Surplus (Score: 85/100)**: Net monthly savings rate is 45.5% (₹38,650 saved from ₹85,000 income).
• **Expense Efficiency (Score: 78/100)**: Essential living expenses are well-contained under 55%.
• **Emergency Fund Runway**: 4.2 months of living costs currently buffered in liquid reserves (Target: 6 months).
• **Debt-to-Income (DTI)**: 12% — well below the risk threshold (35%).
• **Asset Allocation**: 60% Equity Index Funds, 25% Debt/FDs, 15% Gold.

**FinAI Next Best Action**:
Your safety net is solid. Redirect ₹8,000/month into low-cost Nifty 50 Index Funds to accelerate compounding.

*(💡 **Demo Preview**: When logged into your account, FinAI generates this score directly from your live income, expenses, and bank records).*`
    },
    {
      keywords: ['stressed about debt', 'debt', 'where do i start', 'credit card', 'avalanche', 'snowball', 'stressed'],
      reply: `I completely understand—carrying debt can feel overwhelming, but you're taking the right step by facing it today. Take a deep breath: debt is just math, and we can solve it systematically.

Here is FinAI's step-by-step debt elimination demo framework:

1. **Pause New Debt Immediately**: Freeze credit card swipes for non-essentials.
2. **The Avalanche Method (Recommended)**: Pay minimums on all obligations, and throw every extra rupee at the single highest-interest debt first (like credit cards at 36–42% APR). This saves maximum money in interest.
3. **Emergency Buffer**: Keep ₹15,000 to ₹25,000 in a savings account so an unexpected emergency doesn't push you back into credit debt.
4. **Snowball Roll**: Once that card is zeroed, roll its entire payment into the next debt.

*(💡 **Demo Preview**: Log in to let FinAI automatically scan your liabilities, calculate your exact debt-free date, and build your custom repayment plan).*`
    },
    {
      keywords: ['crorepati', '1 crore', 'ten million', 'millionaire', 'retire early', 'wealth'],
      reply: `### 🎯 The Crorepati Roadmap (₹1 Crore / 10 Million)

Building ₹1 Crore does not require speculative gambles or lottery picks. It is grounded in disciplined monthly compounding (assuming historical ~12% average CAGR in diversified index funds):

• **₹10,000 / month SIP**: Crosses ₹1 Crore in ~19.5 years.
• **₹20,000 / month SIP**: Crosses ₹1 Crore in ~15 years.
• **₹35,000 / month SIP**: Crosses ₹1 Crore in ~11 years.
• **10% Annual Step-Up SIP**: Start with ₹15,000/month and increase by 10% each year as your salary increases → Reach ₹1 Crore in just **12.5 years**!

**The Golden Rules**:
1. Start early to give compounding the longest possible runway.
2. Never interrupt compounding during market dips or corrections.
3. Increase your SIP whenever your income grows.

*(💡 **Demo Preview**: When you log in, FinAI calculates your exact personalized crorepati timeline based on your real monthly surplus).*`
    },
    {
      keywords: ['afford to invest', 'invest in mutual funds', 'mutual funds', 'afford', 'invest this month'],
      reply: `### 💡 Affordability & Cashflow Diagnostic (Sample Demo)

Based on a standard cashflow profile:
• **Monthly Inflow**: ₹85,000
• **Essential Bills & Living Costs**: ₹46,350
• **Discretionary Buffer**: ₹10,000
• **Net Available Surplus**: **₹28,650**

**FinAI Verdict**:
**Yes, absolutely!** You can comfortably allocate **₹15,000 to ₹20,000 per month** into diversified mutual funds (such as low-cost Nifty 50 index funds) without putting any strain on your monthly obligations or lifestyle.

*(💡 **Demo Preview**: When logged into your account, FinAI cross-references your live bank balances and upcoming bills before recommending exact investment amounts).*`
    }
  ];

  function getDemoResponse(text) {
    if (!text) return null;
    const lower = text.toLowerCase().trim();
    for (const demo of DEMO_RESPONSES) {
      if (demo.keywords.some(k => lower.includes(k))) {
        return demo.reply;
      }
    }
    return null;
  }

  function formatMarkdown(text) {
    if (!text) return '';
    let html = escapeHtml(text);
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/^###\s*(.*$)/gim, '<h5 style="font-weight: 700; color: #111827; margin: 8px 0 3px;">$1</h5>');
    html = html.replace(/^##\s*(.*$)/gim, '<h4 style="font-weight: 800; color: #111827; margin: 10px 0 4px;">$1</h4>');
    html = html.replace(/^\s*[•*-]\s*(.*$)/gim, '<div style="display: flex; gap: 6px; margin: 3px 0;"><span style="color: #D97706;">•</span><span>$1</span></div>');
    html = html.replace(/^\s*(\d+)\.\s*(.*$)/gim, '<div style="display: flex; gap: 6px; margin: 3px 0;"><span style="font-weight: 700; color: #D97706;">$1.</span><span>$2</span></div>');
    html = html.replace(/\n\n/g, '<div style="height: 8px;"></div>');
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  async function sendLandingMessage(text) {
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
        <span>FinAI is preparing response...</span>
      </div>
    `;
    chatMessages.appendChild(typingRow);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // 1. Check if the query is a demo question
    const demoReply = getDemoResponse(text);
    if (demoReply) {
      setTimeout(() => {
        const typingEl = document.getElementById('landingChatTyping');
        if (typingEl) typingEl.remove();

        const aiRow = document.createElement('div');
        aiRow.className = 'message-row ai';
        aiRow.innerHTML = `
          <div class="chat-avatar" style="width: 32px; height: 32px; font-size: 0.85rem; flex-shrink: 0;">
            <i class="fa-solid fa-robot"></i>
          </div>
          <div class="message-bubble">
            <div style="margin-bottom: 6px; font-size: 0.68rem; font-weight: 700; color: #D97706; text-transform: uppercase; display: flex; align-items: center; gap: 5px;">
              <i class="fa-solid fa-sparkles"></i> FinAI Interactive Demo
            </div>
            <div>${formatMarkdown(demoReply)}</div>
          </div>
        `;
        chatMessages.appendChild(aiRow);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        resetInputState();
      }, 600);
      return;
    }

    // 2. Any other question: Query API. If unauthenticated, show login prompt for further details.
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

      // If user is not logged in, prompt that for further details they must log in
      if (response.status === 401 || (data && data.status === 'auth_required')) {
        aiRow.innerHTML = `
          <div class="chat-avatar" style="width: 32px; height: 32px; font-size: 0.85rem; flex-shrink: 0; background: #FEF3C7; color: #D97706; display: flex; align-items: center; justify-content: center; border-radius: 50%;">
            <i class="fa-solid fa-lock"></i>
          </div>
          <div class="message-bubble" style="border-left: 3px solid #D97706; background: #FFFBEB; padding: 14px 18px;">
            <div style="font-weight: 700; color: #92400E; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; font-size: 0.88rem;">
              <i class="fa-solid fa-circle-info"></i> Interactive Demo Preview
            </div>
            <p style="margin: 0 0 10px 0; color: #78350F; font-size: 0.86rem; line-height: 1.5;">
              This homepage assistant is an interactive demonstration. Without logging into your account, FinAI cannot access your live income, expenses, debts, or investment portfolio.
            </p>
            <p style="margin: 0 0 12px 0; color: #92400E; font-size: 0.86rem; font-weight: 600; line-height: 1.5;">
              For further details, personalized analysis, and complete financial guidance, please log in or create an account.
            </p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <a href="/login" class="fa-btn-primary" style="padding: 7px 16px; font-size: 0.82rem; text-decoration: none; border-radius: 6px; display: inline-flex; align-items: center; gap: 6px;">
                <i class="fa-solid fa-right-to-bracket"></i> Log In
              </a>
              <a href="/register" class="fa-btn-secondary" style="padding: 7px 16px; font-size: 0.82rem; text-decoration: none; border-radius: 6px; display: inline-flex; align-items: center; gap: 6px; background: #FFFFFF;">
                <i class="fa-solid fa-user-plus"></i> Create Free Account
              </a>
            </div>
          </div>
        `;
        chatMessages.appendChild(aiRow);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (chatInput) {
          chatInput.placeholder = "Please log in for further details and custom analysis...";
        }
        return;
      }
      
      let replyHtml = '';
      if (data && data.reply) {
        replyHtml = formatMarkdown(data.reply);
      } else {
        replyHtml = "I encountered an issue processing that query. Please try again in a moment.";
      }

      const providerBadge = data && data.provider ? 
        `<div style="margin-bottom: 4px; font-size: 0.68rem; font-weight: 700; color: #D97706; text-transform: uppercase;">
          <i class="fa-solid fa-bolt"></i> ${escapeHtml(data.provider)}
        </div>` : '';

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
      console.error('Landing Chat Error:', err);
      const typingEl = document.getElementById('landingChatTyping');
      if (typingEl) typingEl.remove();

      const errRow = document.createElement('div');
      errRow.className = 'message-row ai';
      errRow.innerHTML = `
        <div class="chat-avatar" style="width: 32px; height: 32px; font-size: 0.85rem; flex-shrink: 0;">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div class="message-bubble" style="color: #DC2626;">
          <p>Could not connect to the FinAI assistant server. Please check your connection.</p>
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
