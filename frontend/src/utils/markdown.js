import React from 'react';

export function renderMarkdown(text) {
  if (!text) return null;
  
  // Convert standard markdown tokens to HTML
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  
  // Headers
  html = html.replace(/^### (.*$)/gim, '<h4 class="text-base font-bold text-surface-950 dark:text-surface-50 mt-4 mb-2">$1</h4>');
  html = html.replace(/^## (.*$)/gim, '<h3 class="text-lg font-bold text-surface-950 dark:text-surface-50 mt-5 mb-2">$1</h3>');
  html = html.replace(/^# (.*$)/gim, '<h2 class="text-xl font-extrabold text-surface-950 dark:text-surface-50 mt-6 mb-3">$1</h2>');
  
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-surface-950 dark:text-surface-50">$1</strong>');
  
  // Bullet points
  html = html.replace(/^\s*-\s+(.*$)/gim, '<li class="ml-4 list-disc text-sm text-surface-600 dark:text-surface-300 my-1">$1</li>');
  
  // Line breaks
  html = html.replace(/\n/g, '<br />');
  
  return React.createElement('div', {
    dangerouslySetInnerHTML: { __html: html },
    className: 'prose dark:prose-invert max-w-none text-sm leading-relaxed'
  });
}
