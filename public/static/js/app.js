/* =========================================================
   Social Media Caption Assistant — JavaScript
   ========================================================= */

// ── Theme Management ─────────────────────────────────────
const Theme = {
  LIGHT: 'light',
  DARK: 'dark',

  get() { return localStorage.getItem('theme') || 'light'; },

  set(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    document.querySelectorAll('.theme-toggle i').forEach(icon => {
      icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    });
  },

  toggle() {
    const current = this.get();
    this.set(current === 'dark' ? 'light' : 'dark');
  },

  init() {
    this.set(this.get());
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.addEventListener('click', () => this.toggle());
    });
  }
};

// ── Toast Notifications ───────────────────────────────────
const Toast = {
  container: null,

  init() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'info', duration = 3500) {
    const icons = { success: '✅', danger: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
      <span class="toast-msg">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('hiding');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  success(msg, dur) { this.show(msg, 'success', dur); },
  error(msg, dur) { this.show(msg, 'danger', dur); },
  warning(msg, dur) { this.show(msg, 'warning', dur); },
  info(msg, dur) { this.show(msg, 'info', dur); }
};

// ── Clipboard ─────────────────────────────────────────────
const Clipboard = {
  async copy(text) {
    try {
      await navigator.clipboard.writeText(text);
      Toast.success('Copied to clipboard!');
      return true;
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand('copy');
      document.body.removeChild(ta);
      if (ok) Toast.success('Copied to clipboard!');
      return ok;
    }
  }
};

// ── API Helper ────────────────────────────────────────────
const API = {
  async request(url, method = 'GET', body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  },

  get(url) { return this.request(url, 'GET'); },
  post(url, body) { return this.request(url, 'POST', body); },
  put(url, body) { return this.request(url, 'PUT', body); },
  delete(url) { return this.request(url, 'DELETE'); }
};

// ── Sidebar ───────────────────────────────────────────────
const Sidebar = {
  sidebar: null,
  overlay: null,

  init() {
    this.sidebar = document.getElementById('sidebar');
    this.overlay = document.getElementById('sidebar-overlay');

    document.querySelectorAll('.mobile-menu-btn').forEach(btn => {
      btn.addEventListener('click', () => this.toggle());
    });

    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.close());
    }

    // Set active nav item
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item[data-path]').forEach(item => {
      if (path === item.dataset.path || (item.dataset.path !== '/' && path.startsWith(item.dataset.path))) {
        item.classList.add('active');
      }
    });
  },

  toggle() {
    this.sidebar?.classList.toggle('mobile-open');
    this.overlay?.classList.toggle('active');
  },

  close() {
    this.sidebar?.classList.remove('mobile-open');
    this.overlay?.classList.remove('active');
  }
};

// ── Platform character limits ──────────────────────────────
const PLATFORM_LIMITS = {
  'Instagram': 2200,
  'Facebook': 63206,
  'LinkedIn': 3000,
  'X (Twitter)': 280,
  'YouTube': 5000
};

// ── Caption Generator ─────────────────────────────────────
const CaptionGenerator = {
  form: null,
  resultsContainer: null,
  generateBtn: null,

  init() {
    this.form = document.getElementById('caption-form');
    this.resultsContainer = document.getElementById('captions-results');
    this.generateBtn = document.getElementById('generate-btn');

    if (!this.form) return;

    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.generate();
    });

    // Live char count on topic textarea
    const topicEl = document.getElementById('topic');
    if (topicEl) {
      topicEl.addEventListener('input', () => this.updateTopicCount(topicEl));
    }
  },

  updateTopicCount(el) {
    let counter = document.getElementById('topic-char-count');
    if (!counter) {
      counter = document.createElement('div');
      counter.id = 'topic-char-count';
      counter.style.cssText = 'font-size:0.72rem;color:var(--text-muted);text-align:right;margin-top:4px;';
      el.parentNode.appendChild(counter);
    }
    counter.textContent = el.value.length + ' characters';
  },

  async generate() {
    const topic = document.getElementById('topic')?.value.trim();
    if (!topic) { Toast.warning('Please enter a topic or description.'); return; }

    const platform = document.getElementById('platform')?.value;
    const payload = {
      topic,
      platform,
      category: document.getElementById('category')?.value,
      tone: document.getElementById('tone')?.value,
      length: document.getElementById('length')?.value,
      keywords: document.getElementById('keywords')?.value?.trim() || ''
    };

    // Show loading
    this.setLoading(true);
    const emptyEl = document.getElementById('generate-empty');
    if (emptyEl) emptyEl.style.display = 'none';
    this.resultsContainer.style.display = 'flex';
    this.resultsContainer.innerHTML = this.getLoadingHTML();

    try {
      const data = await API.post('/api/generate', payload);

      if (data.is_demo) {
        this.showDemoBanner();
      } else {
        const existing = document.getElementById('demo-banner');
        if (existing) existing.remove();
      }

      this.renderCaptions(data.captions, payload);
      this.resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (err) {
      Toast.error('Failed to generate captions: ' + err.message);
      this.resultsContainer.innerHTML = `
        <div class="card card-body text-center text-muted">
          <p>❌ Generation failed. Please try again.</p>
        </div>`;
    } finally {
      this.setLoading(false);
    }
  },

  setLoading(loading) {
    if (!this.generateBtn) return;
    if (loading) {
      this.generateBtn.disabled = true;
      this.generateBtn.innerHTML = '<span class="spinner"></span> Generating...';
    } else {
      this.generateBtn.disabled = false;
      this.generateBtn.innerHTML = '<i class="bi bi-stars"></i> Generate Captions';
    }
  },

  getLoadingHTML() {
    return `
      <div class="loading-overlay">
        <div class="spinner spinner-primary spinner-lg"></div>
        <p style="color:var(--text-secondary);font-size:0.9rem;margin-top:14px;">AI is crafting your captions...</p>
        <div style="display:flex;gap:6px;margin-top:8px;">
          <div class="pulse-dot" style="animation-delay:0s"></div>
          <div class="pulse-dot" style="animation-delay:0.3s"></div>
          <div class="pulse-dot" style="animation-delay:0.6s"></div>
        </div>
      </div>`;
  },

  showDemoBanner() {
    const existing = document.getElementById('demo-banner');
    if (existing) return;
    const banner = document.createElement('div');
    banner.id = 'demo-banner';
    banner.className = 'demo-banner animate-fadeIn';
    banner.innerHTML = `
      <span>⚠️</span>
      <span><strong>Demo Mode:</strong> These are sample captions, not AI-generated. Configure your Gemini API key in <code>.env</code> to enable real AI generation.</span>
    `;
    this.resultsContainer.before(banner);
  },

  getPlatformBadgeClass(platform) {
    const map = {
      'Instagram': 'badge-instagram',
      'Facebook': 'badge-facebook',
      'LinkedIn': 'badge-linkedin',
      'X (Twitter)': 'badge-twitter',
      'YouTube': 'badge-youtube'
    };
    return map[platform] || 'badge-default';
  },

  renderCaptions(captions, params) {
    const limit = PLATFORM_LIMITS[params.platform] || 2200;
    const html = captions.map((cap, i) => {
      const charCount = cap.char_count || cap.text.length;
      const pct = Math.min(100, Math.round((charCount / limit) * 100));
      const barColor = pct > 90 ? '#ef4444' : pct > 70 ? '#f59e0b' : '#10b981';
      return `
      <div class="caption-card animate-fadeInUp stagger-${i + 1}" id="caption-card-${cap.id}">
        <div class="caption-number">✨ Caption ${i + 1}</div>
        <p class="caption-text" id="caption-text-${cap.id}">${escapeHtml(cap.text)}</p>
        <div class="caption-hashtags">${escapeHtml(cap.hashtags)}</div>

        <!-- char bar -->
        <div style="margin:10px 0 4px;">
          <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:var(--text-muted);margin-bottom:4px;">
            <span>${charCount} / ${limit} chars (${params.platform})</span>
            <span style="color:${barColor}">${pct}%</span>
          </div>
          <div style="height:4px;background:var(--border);border-radius:2px;overflow:hidden;">
            <div style="width:${pct}%;height:100%;background:${barColor};border-radius:2px;transition:width 0.6s ease;"></div>
          </div>
        </div>

        <div class="caption-meta">
          <span class="badge-platform ${this.getPlatformBadgeClass(params.platform)}">${params.platform}</span>
          <span class="badge-platform badge-default" style="font-size:0.68rem;padding:3px 8px;">${params.tone}</span>
          <span class="char-count">${charCount} chars</span>
        </div>
        <div class="caption-actions">
          <button class="btn btn-ghost btn-sm" onclick="Clipboard.copy(document.getElementById('caption-text-${cap.id}').textContent + '\\n\\n' + '${cap.hashtags.replace(/'/g, "\\'")}')">
            <i class="bi bi-clipboard"></i> Copy
          </button>
          <button class="btn btn-ghost btn-sm" onclick="CaptionGenerator.saveCaption(${cap.id}, this)" id="save-btn-${cap.id}">
            <i class="bi bi-bookmark"></i> Save
          </button>
          <button class="btn btn-ghost btn-sm" onclick="CaptionGenerator.toggleFavorite(${cap.id}, this)" id="fav-btn-${cap.id}">
            <i class="bi bi-heart"></i> Favorite
          </button>
          <button class="btn btn-ghost btn-sm" onclick="CaptionGenerator.generate()">
            <i class="bi bi-arrow-clockwise"></i> Regenerate
          </button>
          <button class="btn btn-ghost btn-sm" onclick="CaptionGenerator.exportSingle(${cap.id}, '${escapeHtml(params.platform)}', '${escapeHtml(params.tone)}')">
            <i class="bi bi-download"></i> Export
          </button>
        </div>
      </div>
    `}).join('');

    this.resultsContainer.innerHTML = html;
  },

  async saveCaption(captionId, btn) {
    try {
      await API.put(`/api/captions/${captionId}`, { is_saved: 1 });
      btn.innerHTML = '<i class="bi bi-bookmark-fill"></i> Saved';
      btn.disabled = true;
      Toast.success('Caption saved to My Captions!');
    } catch (err) {
      Toast.error('Could not save caption.');
    }
  },

  async toggleFavorite(captionId, btn) {
    try {
      const data = await API.post('/api/favorites', { caption_id: captionId });
      if (data.added) {
        btn.innerHTML = '<i class="bi bi-heart-fill" style="color:#ef4444"></i> Favorited';
        Toast.success('Added to favorites!');
      } else {
        btn.innerHTML = '<i class="bi bi-heart"></i> Favorite';
        Toast.info('Removed from favorites.');
      }
    } catch (err) {
      Toast.error('Could not update favorites.');
    }
  },

  exportSingle(captionId, platform, tone) {
    const textEl = document.getElementById(`caption-text-${captionId}`);
    if (!textEl) return;
    const text = textEl.textContent;
    const content = `Social Media Caption Assistant — Export\n${'='.repeat(45)}\nPlatform: ${platform}\nTone: ${tone}\nDate: ${new Date().toLocaleString()}\n${'='.repeat(45)}\n\n${text}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `caption-${captionId}.txt`;
    a.click();
    Toast.success('Caption exported!');
  }
};

// ── My Captions Page ──────────────────────────────────────
const CaptionsPage = {
  captions: [],
  filters: { search: '', platform: '', category: '', saved: 1 },

  init() {
    if (!document.getElementById('captions-grid')) return;
    this.load();

    document.getElementById('search-input')?.addEventListener('input', debounce((e) => {
      this.filters.search = e.target.value;
      this.load();
    }, 400));

    document.getElementById('platform-filter')?.addEventListener('change', (e) => {
      this.filters.platform = e.target.value;
      this.load();
    });

    document.getElementById('category-filter')?.addEventListener('change', (e) => {
      this.filters.category = e.target.value;
      this.load();
    });
  },

  async load() {
    const grid = document.getElementById('captions-grid');
    grid.innerHTML = '<div class="loading-overlay"><div class="spinner spinner-primary"></div></div>';

    const params = new URLSearchParams();
    if (this.filters.saved !== null && this.filters.saved !== undefined) params.set('saved', this.filters.saved);
    if (this.filters.platform) params.set('platform', this.filters.platform);
    if (this.filters.category) params.set('category', this.filters.category);
    if (this.filters.search) params.set('search', this.filters.search);

    try {
      const data = await API.get('/api/captions?' + params.toString());
      this.captions = data.captions;
      this.render();
    } catch (err) {
      grid.innerHTML = `<div class="empty-state"><p>Failed to load captions.</p></div>`;
    }
  },

  render() {
    const grid = document.getElementById('captions-grid');
    if (!this.captions.length) {
      const isSavedTab = this.filters.saved === 1;
      grid.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">${isSavedTab ? '📌' : '📝'}</div>
          <h3>${isSavedTab ? 'No saved captions' : 'No captions yet'}</h3>
          <p>${isSavedTab ? 'Save captions from the generator to find them here.' : 'Generate captions to build your history.'}</p>
          <a href="/generate" class="btn btn-primary mt-16">Generate Captions</a>
        </div>`;
      return;
    }

    grid.innerHTML = this.captions.map(cap => this.renderCard(cap)).join('');
  },

  renderCard(cap) {
    const favClass = cap.is_favorite ? 'bi-heart-fill" style="color:#ef4444' : 'bi-heart';
    const savedBadge = cap.is_saved ? '<span style="font-size:0.65rem;background:rgba(124,58,237,0.1);color:var(--primary);padding:2px 7px;border-radius:4px;font-weight:600;">SAVED</span>' : '';
    return `
      <div class="caption-card" id="cap-${cap.id}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
            <span style="font-size:0.72rem;color:var(--text-muted);">${formatDate(cap.created_at)}</span>
            ${savedBadge}
          </div>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-icon btn-ghost" onclick="CaptionsPage.toggleFav(${cap.id}, this)" title="Favorite">
              <i class="bi ${favClass}"></i>
            </button>
            <button class="btn btn-icon btn-ghost" style="color:var(--danger)" onclick="CaptionsPage.deleteCap(${cap.id})" title="Delete">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
        <p class="caption-text" id="ct-${cap.id}">${escapeHtml(cap.caption_text)}</p>
        <div class="caption-hashtags">${escapeHtml(cap.hashtags || '')}</div>
        <div class="caption-meta">
          <span class="badge-platform ${getPlatformClass(cap.platform)}">${cap.platform}</span>
          <span style="font-size:0.72rem;color:var(--text-muted);">${cap.category} · ${cap.tone}</span>
        </div>
        <div class="caption-actions">
          <button class="btn btn-ghost btn-sm" onclick="Clipboard.copy(document.getElementById('ct-${cap.id}').textContent)">
            <i class="bi bi-clipboard"></i> Copy
          </button>
          <button class="btn btn-ghost btn-sm" onclick="CaptionsPage.editCap(${cap.id})">
            <i class="bi bi-pencil"></i> Edit
          </button>
          <button class="btn btn-ghost btn-sm" onclick="CaptionsPage.exportCap(${cap.id})">
            <i class="bi bi-download"></i> Export
          </button>
        </div>
      </div>`;
  },

  async deleteCap(id) {
    if (!confirm('Delete this caption?')) return;
    try {
      await API.delete(`/api/captions/${id}`);
      document.getElementById(`cap-${id}`)?.remove();
      Toast.success('Caption deleted.');
      if (!document.querySelector('.caption-card')) this.render();
    } catch (err) {
      Toast.error('Could not delete caption.');
    }
  },

  async toggleFav(id, btn) {
    try {
      const data = await API.post('/api/favorites', { caption_id: id });
      btn.querySelector('i').className = data.added
        ? 'bi bi-heart-fill" style="color:#ef4444'
        : 'bi bi-heart';
      Toast.success(data.added ? 'Added to favorites!' : 'Removed from favorites.');
    } catch (err) {
      Toast.error('Could not update favorites.');
    }
  },

  editCap(id) {
    const el = document.getElementById(`ct-${id}`);
    const original = el.textContent;
    el.contentEditable = 'true';
    el.style.border = '1.5px solid var(--primary)';
    el.style.borderRadius = '8px';
    el.style.padding = '8px';
    el.focus();

    const save = async () => {
      el.contentEditable = 'false';
      el.style.border = '';
      el.style.padding = '';
      const newText = el.textContent.trim();
      if (newText !== original) {
        try {
          await API.put(`/api/captions/${id}`, { caption_text: newText });
          Toast.success('Caption updated!');
        } catch { Toast.error('Could not update caption.'); }
      }
    };

    el.addEventListener('blur', save, { once: true });
    el.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); el.blur(); } });
  },

  exportCap(id) {
    const el = document.getElementById(`ct-${id}`);
    if (!el) return;
    const blob = new Blob([el.textContent], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `caption-${id}.txt`;
    a.click();
    Toast.success('Exported!');
  }
};

// ── History Page ──────────────────────────────────────────
const HistoryPage = {
  init() {
    if (!document.getElementById('history-table-body')) return;
    this.load();

    document.getElementById('search-input')?.addEventListener('input', debounce(() => this.load(), 400));
    document.getElementById('platform-filter')?.addEventListener('change', () => this.load());
  },

  async load() {
    const tbody = document.getElementById('history-table-body');
    tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding:30px;color:var(--text-muted)">Loading...</td></tr>';

    const search = document.getElementById('search-input')?.value || '';
    const platform = document.getElementById('platform-filter')?.value || '';
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (platform) params.set('platform', platform);

    try {
      const data = await API.get('/api/captions?' + params.toString());
      this.render(data.captions);
      // Update count badge
      const badge = document.getElementById('history-count');
      if (badge) badge.textContent = data.captions.length + ' entries';
    } catch {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">Failed to load.</td></tr>';
    }
  },

  render(captions) {
    const tbody = document.getElementById('history-table-body');
    if (!captions.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding:40px;color:var(--text-muted)">No history found.</td></tr>';
      return;
    }
    tbody.innerHTML = captions.map(cap => `
      <tr>
        <td style="font-size:0.8rem;color:var(--text-muted)">${formatDate(cap.created_at)}</td>
        <td><span class="badge-platform ${getPlatformClass(cap.platform)}" style="font-size:0.72rem;padding:3px 8px;">${cap.platform}</span></td>
        <td style="font-size:0.8rem;color:var(--text-secondary)">${cap.category}</td>
        <td style="font-size:0.85rem;max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(cap.caption_text)}">${escapeHtml(cap.caption_text)}</td>
        <td>
          <button class="btn btn-ghost btn-sm" onclick="Clipboard.copy('${cap.caption_text.replace(/'/g, "\\'")}')">
            <i class="bi bi-clipboard"></i>
          </button>
        </td>
        <td>
          <button class="btn btn-icon" style="background:rgba(239,68,68,0.1);color:var(--danger)" onclick="HistoryPage.deleteCap(${cap.id}, this)">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
  },

  async deleteCap(id, btn) {
    if (!confirm('Delete this entry?')) return;
    try {
      await API.delete(`/api/captions/${id}`);
      btn.closest('tr').remove();
      Toast.success('Deleted!');
    } catch { Toast.error('Delete failed.'); }
  },

  exportAll() {
    const rows = document.querySelectorAll('#history-table-body tr');
    if (!rows.length) { Toast.warning('No history to export.'); return; }
    let content = 'Social Media Caption Assistant — History Export\n' + '='.repeat(50) + '\n\n';
    rows.forEach((row, i) => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 4) {
        content += `[${i + 1}] ${cells[0]?.textContent?.trim()}\n`;
        content += `Platform: ${cells[1]?.textContent?.trim()} | Category: ${cells[2]?.textContent?.trim()}\n`;
        content += `Caption: ${cells[3]?.textContent?.trim()}\n\n`;
      }
    });
    const blob = new Blob([content], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'caption-history.txt';
    a.click();
    Toast.success('History exported!');
  }
};

// ── Hashtag Generator ─────────────────────────────────────
const HashtagGenerator = {
  selected: new Set(),

  init() {
    if (!document.getElementById('hashtag-form')) return;
    document.getElementById('hashtag-form').addEventListener('submit', (e) => {
      e.preventDefault();
      this.generate();
    });
  },

  async generate() {
    const topic = document.getElementById('htopic')?.value.trim();
    const category = document.getElementById('hcategory')?.value || 'General';
    if (!topic) { Toast.warning('Please enter a topic.'); return; }

    const btn = document.getElementById('hashtag-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Generating...';

    try {
      const data = await API.post('/api/hashtags', { topic, category });
      if (data.is_demo) Toast.info('Demo mode: showing sample hashtags.');
      this.render(data.hashtags);
    } catch (err) {
      Toast.error('Failed: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-hash"></i> Generate Hashtags';
    }
  },

  render(hashtags) {
    const container = document.getElementById('hashtag-results');
    container.classList.remove('d-none');
    this.selected.clear();

    let totalCount = 0;
    ['popular', 'niche', 'general'].forEach(type => {
      const wrap = document.getElementById(`tags-${type}`);
      if (!wrap) return;
      const tags = hashtags[type] || [];
      totalCount += tags.length;
      wrap.innerHTML = tags.map(tag => `
        <span class="hashtag-tag hashtag-${type}" onclick="HashtagGenerator.toggle(this, '${escapeHtml(tag)}')">${escapeHtml(tag)}</span>
      `).join('');
    });

    document.getElementById('selected-count').textContent = '0';
    const totalEl = document.getElementById('total-hashtag-count');
    if (totalEl) totalEl.textContent = totalCount + ' hashtags generated';
  },

  toggle(el, tag) {
    if (this.selected.has(tag)) {
      this.selected.delete(tag);
      el.classList.remove('selected');
    } else {
      this.selected.add(tag);
      el.classList.add('selected');
    }
    document.getElementById('selected-count').textContent = this.selected.size;
  },

  selectAll() {
    document.querySelectorAll('.hashtag-tag').forEach(el => {
      const tag = el.textContent;
      this.selected.add(tag);
      el.classList.add('selected');
    });
    document.getElementById('selected-count').textContent = this.selected.size;
    Toast.info(this.selected.size + ' hashtags selected.');
  },

  clearSelection() {
    document.querySelectorAll('.hashtag-tag').forEach(el => el.classList.remove('selected'));
    this.selected.clear();
    document.getElementById('selected-count').textContent = '0';
  },

  copySelected() {
    if (!this.selected.size) { Toast.warning('No hashtags selected. Click tags to select them.'); return; }
    Clipboard.copy([...this.selected].join(' '));
  },

  copyAll() {
    const all = [];
    document.querySelectorAll('.hashtag-tag').forEach(el => all.push(el.textContent));
    if (!all.length) { Toast.warning('No hashtags to copy.'); return; }
    Clipboard.copy(all.join(' '));
  },

  exportHashtags() {
    const all = [];
    document.querySelectorAll('.hashtag-tag').forEach(el => all.push(el.textContent));
    if (!all.length) { Toast.warning('Nothing to export.'); return; }
    const topic = document.getElementById('htopic')?.value || 'hashtags';
    const content = `Social Media Caption Assistant — Hashtag Export\n${'='.repeat(45)}\nTopic: ${topic}\nDate: ${new Date().toLocaleString()}\n${'='.repeat(45)}\n\n${all.join(' ')}\n\nTotal: ${all.length} hashtags`;
    const blob = new Blob([content], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `hashtags-${topic.replace(/\s+/g,'-')}.txt`;
    a.click();
    Toast.success('Hashtags exported!');
  }
};

// ── Favorites Page ────────────────────────────────────────
const FavoritesPage = {
  init() {
    if (!document.getElementById('favorites-grid')) return;
    this.load();
  },

  async load() {
    const grid = document.getElementById('favorites-grid');
    grid.innerHTML = '<div class="loading-overlay"><div class="spinner spinner-primary"></div></div>';
    try {
      const data = await API.get('/api/favorites');
      if (!data.captions.length) {
        grid.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">❤️</div>
            <h3>No favorites yet</h3>
            <p>Heart any caption to save it here.</p>
            <a href="/generate" class="btn btn-primary mt-16">Generate Captions</a>
          </div>`;
        return;
      }
      // Update count
      const countEl = document.getElementById('fav-count');
      if (countEl) countEl.textContent = data.captions.length + ' saved';

      grid.innerHTML = data.captions.map(cap => `
        <div class="caption-card" id="fav-${cap.id}">
          <p class="caption-text" id="fav-text-${cap.id}">${escapeHtml(cap.caption_text)}</p>
          <div class="caption-hashtags">${escapeHtml(cap.hashtags || '')}</div>
          <div class="caption-meta">
            <span class="badge-platform ${getPlatformClass(cap.platform)}">${cap.platform}</span>
            <span style="font-size:0.72rem;color:var(--text-muted)">${cap.category} · ${cap.tone}</span>
          </div>
          <div style="font-size:0.72rem;color:var(--text-muted);margin-top:6px;">${formatDate(cap.created_at)}</div>
          <div class="caption-actions">
            <button class="btn btn-ghost btn-sm" onclick="Clipboard.copy(document.getElementById('fav-text-${cap.id}').textContent)">
              <i class="bi bi-clipboard"></i> Copy
            </button>
            <button class="btn btn-ghost btn-sm" onclick="FavoritesPage.exportFav(${cap.id})">
              <i class="bi bi-download"></i> Export
            </button>
            <button class="btn btn-ghost btn-sm" style="color:var(--danger)" onclick="FavoritesPage.removeFav(${cap.id})">
              <i class="bi bi-heart-fill" style="color:#ef4444"></i> Remove
            </button>
          </div>
        </div>`).join('');
    } catch {
      grid.innerHTML = `<div class="empty-state"><p>Failed to load favorites.</p></div>`;
    }
  },

  async removeFav(id) {
    try {
      await API.post('/api/favorites', { caption_id: id });
      document.getElementById(`fav-${id}`)?.remove();
      Toast.info('Removed from favorites.');
    } catch { Toast.error('Could not remove favorite.'); }
  },

  exportFav(id) {
    const el = document.getElementById(`fav-text-${id}`);
    if (!el) return;
    const blob = new Blob([el.textContent], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `favorite-${id}.txt`;
    a.click();
    Toast.success('Exported!');
  }
};

// ── Profile Page ──────────────────────────────────────────
const ProfilePage = {
  init() {
    const form = document.getElementById('profile-form');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Saving...';
      try {
        const data = {
          username: document.getElementById('username')?.value,
          bio: document.getElementById('bio')?.value,
          current_password: document.getElementById('current_password')?.value,
          new_password: document.getElementById('new_password')?.value
        };
        await API.post('/api/profile', data);
        Toast.success('Profile updated successfully!');
      } catch (err) {
        Toast.error(err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check-circle"></i> Save Changes';
      }
    });
  }
};

// ── Dashboard Chart ───────────────────────────────────────
const DashboardChart = {
  init() {
    const canvas = document.getElementById('platform-chart');
    if (!canvas || typeof Chart === 'undefined') return;

    const stats = window.dashboardStats?.platform_stats || [];
    if (!stats.length) return;

    const labels = stats.map(s => s.platform);
    const values = stats.map(s => s.count);
    const colors = ['#7c3aed', '#2563eb', '#10b981', '#f59e0b', '#ef4444'];

    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors.slice(0, labels.length),
          borderWidth: 0,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#666',
              padding: 16,
              font: { family: 'Inter', size: 12 }
            }
          }
        },
        cutout: '70%'
      }
    });
  }
};

// ── Animated Counter for Dashboard Stats ─────────────────
const AnimatedCounters = {
  init() {
    document.querySelectorAll('.stat-value[data-target]').forEach(el => {
      const target = parseInt(el.dataset.target, 10);
      if (isNaN(target)) return;
      let start = 0;
      const duration = 1200;
      const steps = 40;
      const increment = target / steps;
      const interval = duration / steps;
      const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
          el.textContent = target;
          clearInterval(timer);
        } else {
          el.textContent = Math.floor(start);
        }
      }, interval);
    });
  }
};

// ── Landing Page Navbar scroll effect ────────────────────
function initLandingNav() {
  const nav = document.querySelector('.landing-nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  });
}

// ── Smooth scroll for anchor links ───────────────────────
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// ── Helpers ───────────────────────────────────────────────
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

function formatDate(str) {
  if (!str) return '';
  const d = new Date(str);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function getPlatformClass(platform) {
  const map = {
    'Instagram': 'badge-instagram',
    'Facebook': 'badge-facebook',
    'LinkedIn': 'badge-linkedin',
    'X (Twitter)': 'badge-twitter',
    'YouTube': 'badge-youtube'
  };
  return map[platform] || 'badge-default';
}

function debounce(fn, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Theme.init();
  Toast.init();
  Sidebar.init();
  CaptionGenerator.init();
  CaptionsPage.init();
  HistoryPage.init();
  HashtagGenerator.init();
  FavoritesPage.init();
  ProfilePage.init();
  DashboardChart.init();
  AnimatedCounters.init();
  initLandingNav();
  initSmoothScroll();

  // Flash messages from Flask → auto-show as toasts
  document.querySelectorAll('.flask-flash').forEach(el => {
    Toast.show(el.dataset.message, el.dataset.category || 'info');
    el.remove();
  });

  // Animate elements on scroll (IntersectionObserver)
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-fadeInUp');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.feature-card, .step-card, .testimonial-card').forEach(el => {
    el.style.opacity = '0';
    observer.observe(el);
  });
});
