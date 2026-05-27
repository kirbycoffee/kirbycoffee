const views = {
  landing: document.getElementById('landing'),
  login: document.getElementById('login'),
  signup: document.getElementById('signup'),
  'forgot-password': document.getElementById('forgot-password'),
  dashboard: document.getElementById('dashboard'),
};

const toast = document.getElementById('toast');
const welcomeName = document.getElementById('welcomeName');
const signupValidation = document.getElementById('signupValidation');
const resetValidation = document.getElementById('resetValidation');
const passwordResetFields = document.getElementById('passwordResetFields');
const sendCodeBtn = document.getElementById('sendCodeBtn');
const resetPasswordBtn = document.getElementById('resetPasswordBtn');

let currentSession = {
  username: null,
  email: null,
  resetEmail: null,
};

function showView(viewKey) {
  Object.values(views).forEach((section) => {
    section.classList.remove('active');
  });
  const target = views[viewKey];
  if (target) {
    target.classList.add('active');
  }
}

function showToast(message, duration = 3200) {
  toast.textContent = message;
  toast.classList.remove('hidden');
  clearTimeout(showToast.timeout);
  showToast.timeout = setTimeout(() => {
    toast.classList.add('hidden');
  }, duration);
}

async function postJSON(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return response.json();
}

function bindNavigation() {
  document.body.addEventListener('click', (event) => {
    const button = event.target.closest('[data-action="go"]');
    if (!button) return;
    event.preventDefault();
    const target = button.dataset.target;
    if (target) showView(target);
  });
}

function bindFeatureCards() {
  document.querySelectorAll('.feature-card, .nav-link').forEach((element) => {
    element.addEventListener('click', () => {
      const card = element.dataset.card;
      if (!card) return;
      const descriptions = {
        'dream-room': 'Opening the Canvas & AI Dream Room...',
        'data-chart': 'Loading your subconscious data trends...',
        'time-capsule': 'Sealing your memory vault...',
      };
      showToast(descriptions[card] || 'Entering the feature...');
    });
  });
}

function bindAuthForms() {
  const loginForm = document.getElementById('loginForm');
  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(loginForm);
    const payload = {
      email: formData.get('email').trim(),
      password: formData.get('password').trim(),
    };
    const result = await postJSON('/api/login', payload);
    if (result.success) {
      currentSession.username = result.username;
      currentSession.email = result.email;
      welcomeName.textContent = result.username || 'Observer';
      showToast('Login successful. Welcome back.');
      showView('dashboard');
    } else {
      showToast(result.message || 'Unable to log in.');
    }
  });

  const signupForm = document.getElementById('signupForm');
  signupForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(signupForm);
    const username = formData.get('username').trim();
    const email = formData.get('email').trim();
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    if (password !== confirmPassword) {
      signupValidation.textContent = 'Passwords do not match.';
      return;
    }
    signupValidation.textContent = '';

    const result = await postJSON('/api/signup', { username, email, password });
    if (result.success) {
      showToast('Account created. Proceed to log in.');
      signupForm.reset();
      showView('login');
    } else {
      signupValidation.textContent = result.message || 'Unable to create account.';
    }
  });

  signupForm.querySelector('input[name="confirmPassword"]').addEventListener('input', () => {
    const password = signupForm.querySelector('input[name="password"]').value;
    const confirm = signupForm.querySelector('input[name="confirmPassword"]').value;
    signupValidation.textContent = password && confirm && password !== confirm ? 'Passwords do not match.' : '';
  });
}

function bindForgotPassword() {
  sendCodeBtn.addEventListener('click', async () => {
    const email = document.querySelector('#passwordInitial input[name="email"]').value.trim();
    if (!email) {
      showToast('Please enter your email to receive a verification code.');
      return;
    }
    sendCodeBtn.disabled = true;
    sendCodeBtn.textContent = 'Sending...';
    const result = await postJSON('/api/password/send-code', { email });
    sendCodeBtn.disabled = false;
    sendCodeBtn.textContent = 'Send Verification Code';
    if (result.success) {
      currentSession.resetEmail = email;
      passwordResetFields.classList.remove('hidden');
      showToast('Verification code sent. Check your inbox.');
    } else {
      showToast(result.message || 'Unable to send code.');
    }
  });

  resetPasswordBtn.addEventListener('click', async () => {
    const code = document.querySelector('#passwordResetFields input[name="code"]').value.trim();
    const newPassword = document.querySelector('#passwordResetFields input[name="newPassword"]').value;
    const confirmNewPassword = document.querySelector('#passwordResetFields input[name="confirmNewPassword"]').value;
    if (!code || !newPassword || !confirmNewPassword) {
      resetValidation.textContent = 'Complete all fields to reset your password.';
      return;
    }
    if (newPassword !== confirmNewPassword) {
      resetValidation.textContent = 'New passwords do not match.';
      return;
    }
    resetValidation.textContent = '';
    const result = await postJSON('/api/password/reset', {
      email: currentSession.resetEmail,
      code,
      newPassword,
    });
    if (result.success) {
      showToast('Password reset complete. You can log in now.');
      document.getElementById('passwordForm').reset();
      passwordResetFields.classList.add('hidden');
      showView('login');
    } else {
      resetValidation.textContent = result.message || 'Unable to reset password.';
    }
  });
}

function bindLogout() {
  document.getElementById('logoutBtn').addEventListener('click', async () => {
    await postJSON('/api/logout', {});
    currentSession = { username: null, email: null, resetEmail: null };
    showView('landing');
    showToast('Logged out successfully.');
  });
}

function init() {
  bindNavigation();
  bindFeatureCards();
  bindAuthForms();
  bindForgotPassword();
  bindLogout();
  showView('landing');
}

init();
