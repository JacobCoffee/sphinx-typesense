/**
 * Pagefind UI initialization for sphinx-typesense
 *
 * This script initializes the Pagefind search UI with configuration
 * from window.PAGEFIND_CONFIG (set by PagefindBackend).
 *
 * Pagefind documentation: https://pagefind.app/docs/ui/
 */

(function() {
  'use strict';

  // Get configuration from backend
  var config = window.PAGEFIND_CONFIG || {};
  var container = config.container || '#typesense-search';
  var basePath = config.basePath || '/_pagefind/';
  var placeholder = config.placeholder || 'Search documentation...';

  /**
   * Initialize Pagefind UI once the page is ready.
   */
  function initPagefind() {
    var containerEl = document.querySelector(container);
    if (!containerEl) {
      console.warn('[sphinx-typesense] Search container not found:', container);
      return;
    }

    // Check if PagefindUI is loaded
    if (typeof PagefindUI === 'undefined') {
      console.warn('[sphinx-typesense] PagefindUI not loaded. Attempting to load from', basePath);
      loadPagefindUI();
      return;
    }

    // Initialize the UI
    try {
      new PagefindUI({
        element: container,
        showSubResults: true,
        showImages: false,
        excerptLength: 15,
        resetStyles: false,
        bundlePath: basePath,
        translations: {
          placeholder: placeholder,
          zero_results: 'No results found for "[SEARCH_TERM]"',
          clear_search: 'Clear',
          load_more: 'Load more results'
        },
        // Process results to fix relative URLs if needed
        processResult: function(result) {
          // Ensure URLs work correctly in Sphinx docs
          if (result.url && !result.url.startsWith('http') && !result.url.startsWith('/')) {
            result.url = '/' + result.url;
          }
          return result;
        }
      });

      console.debug('[sphinx-typesense] Pagefind UI initialized');
    } catch (err) {
      console.error('[sphinx-typesense] Failed to initialize PagefindUI:', err);
    }
  }

  /**
   * Dynamically load Pagefind UI script and CSS.
   */
  function loadPagefindUI() {
    // Load CSS
    var cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = basePath + 'pagefind-ui.css';
    document.head.appendChild(cssLink);

    // Load JS
    var script = document.createElement('script');
    script.src = basePath + 'pagefind-ui.js';
    script.onload = function() {
      // Wait a tick for script to execute
      setTimeout(initPagefind, 0);
    };
    script.onerror = function() {
      console.error('[sphinx-typesense] Failed to load Pagefind UI from', basePath);
    };
    document.head.appendChild(script);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPagefind);
  } else {
    initPagefind();
  }

})();
