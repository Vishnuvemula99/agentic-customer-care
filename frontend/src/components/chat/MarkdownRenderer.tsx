"use client";

import { useMemo } from "react";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * Zero-dependency markdown renderer for chat messages.
 * Supports: bold, italic, inline code, code blocks, headings,
 * unordered/ordered lists, links, horizontal rules, and blockquotes.
 */
export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  const rendered = useMemo(() => parseMarkdown(content), [content]);

  return (
    <div
      className={`markdown-content ${className}`}
      dangerouslySetInnerHTML={{ __html: rendered }}
    />
  );
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function parseInline(text: string): string {
  let result = escapeHtml(text);

  // Code (inline) — must come first to prevent other formatting inside code
  result = result.replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>');

  // Bold + Italic
  result = result.replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>");
  result = result.replace(/___(.+?)___/g, "<strong><em>$1</em></strong>");

  // Bold
  result = result.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  result = result.replace(/__(.+?)__/g, "<strong>$1</strong>");

  // Italic
  result = result.replace(/\*(.+?)\*/g, "<em>$1</em>");
  result = result.replace(/_(.+?)_/g, "<em>$1</em>");

  // Strikethrough
  result = result.replace(/~~(.+?)~~/g, "<del>$1</del>");

  // Links
  result = result.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer" class="md-link">$1</a>'
  );

  return result;
}

function parseMarkdown(raw: string): string {
  const lines = raw.split("\n");
  const html: string[] = [];
  let i = 0;
  let inCodeBlock = false;
  let codeBlockContent: string[] = [];
  let codeBlockLang = "";

  while (i < lines.length) {
    const line = lines[i];

    // --- Fenced code blocks ---
    if (line.trimStart().startsWith("```")) {
      if (!inCodeBlock) {
        inCodeBlock = true;
        codeBlockLang = line.trimStart().slice(3).trim();
        codeBlockContent = [];
        i++;
        continue;
      } else {
        inCodeBlock = false;
        const langClass = codeBlockLang ? ` data-lang="${escapeHtml(codeBlockLang)}"` : "";
        html.push(
          `<div class="md-code-block">${codeBlockLang ? `<div class="md-code-lang">${escapeHtml(codeBlockLang)}</div>` : ""}<pre${langClass}><code>${escapeHtml(codeBlockContent.join("\n"))}</code></pre></div>`
        );
        i++;
        continue;
      }
    }

    if (inCodeBlock) {
      codeBlockContent.push(line);
      i++;
      continue;
    }

    // --- Blank lines ---
    if (line.trim() === "") {
      i++;
      continue;
    }

    // --- Headings ---
    const headingMatch = line.match(/^(#{1,6})\s+(.+)/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      html.push(`<h${level} class="md-h${level}">${parseInline(headingMatch[2])}</h${level}>`);
      i++;
      continue;
    }

    // --- Horizontal rule ---
    if (/^[-*_]{3,}\s*$/.test(line.trim())) {
      html.push('<hr class="md-hr" />');
      i++;
      continue;
    }

    // --- Blockquote ---
    if (line.trimStart().startsWith("> ")) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trimStart().startsWith("> ")) {
        quoteLines.push(lines[i].trimStart().slice(2));
        i++;
      }
      html.push(`<blockquote class="md-blockquote">${parseInline(quoteLines.join(" "))}</blockquote>`);
      continue;
    }

    // --- Unordered list ---
    if (/^[\s]*[-*+]\s+/.test(line)) {
      const listItems: string[] = [];
      while (i < lines.length && /^[\s]*[-*+]\s+/.test(lines[i])) {
        listItems.push(lines[i].replace(/^[\s]*[-*+]\s+/, ""));
        i++;
      }
      const items = listItems.map((item) => `<li>${parseInline(item)}</li>`).join("");
      html.push(`<ul class="md-ul">${items}</ul>`);
      continue;
    }

    // --- Ordered list ---
    if (/^[\s]*\d+[.)]\s+/.test(line)) {
      const listItems: string[] = [];
      while (i < lines.length && /^[\s]*\d+[.)]\s+/.test(lines[i])) {
        listItems.push(lines[i].replace(/^[\s]*\d+[.)]\s+/, ""));
        i++;
      }
      const items = listItems.map((item) => `<li>${parseInline(item)}</li>`).join("");
      html.push(`<ol class="md-ol">${items}</ol>`);
      continue;
    }

    // --- Regular paragraph ---
    const paraLines: string[] = [line];
    i++;
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !lines[i].trimStart().startsWith("```") &&
      !lines[i].match(/^#{1,6}\s/) &&
      !/^[\s]*[-*+]\s+/.test(lines[i]) &&
      !/^[\s]*\d+[.)]\s+/.test(lines[i]) &&
      !lines[i].trimStart().startsWith("> ") &&
      !/^[-*_]{3,}\s*$/.test(lines[i].trim())
    ) {
      paraLines.push(lines[i]);
      i++;
    }
    html.push(`<p class="md-p">${parseInline(paraLines.join(" "))}</p>`);
  }

  // Handle unclosed code block
  if (inCodeBlock) {
    html.push(
      `<div class="md-code-block"><pre><code>${escapeHtml(codeBlockContent.join("\n"))}</code></pre></div>`
    );
  }

  return html.join("");
}
