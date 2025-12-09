# Content Security Policy (CSP) Best Practices Guide

**Reference:** [web.dev CSP Documentation](https://web.dev/articles/csp?utm_source=devtools&utm_campaign=stable#eval_too)

## Table of Contents
1. [Overview](#overview)
2. [Why CSP Matters](#why-csp-matters)
3. [CSP Directives Explained](#csp-directives-explained)
4. [Common Patterns & Best Practices](#common-patterns--best-practices)
5. [Removing `unsafe-eval` Safely](#removing-unsafe-eval-safely)
6. [Implementation Strategies](#implementation-strategies)
7. [Real-World Examples](#real-world-examples)
8. [Troubleshooting](#troubleshooting)
9. [Migration Checklist](#migration-checklist)

---

## Overview

Content Security Policy (CSP) is a security mechanism that helps prevent Cross-Site Scripting (XSS) attacks by allowing you to create an allowlist of trusted content sources. The browser will only execute or render resources from those sources.

### Key Benefits
- **Prevents XSS attacks** by blocking unauthorized script execution
- **Reduces attack surface** by restricting resource loading
- **Provides violation reporting** for security monitoring
- **Enforces secure coding practices** by blocking dangerous patterns

---

## Why CSP Matters

### The Problem: XSS Attacks

The web's security model is based on a **same-origin policy**. However, attackers can bypass this by injecting malicious code into your pages through:

- **Stored XSS**: Malicious scripts stored in your database
- **Reflected XSS**: Scripts injected via URL parameters
- **DOM-based XSS**: Client-side code manipulation

### How CSP Helps

CSP creates an **allowlist** of trusted sources. Even if an attacker injects code, the browser will:
1. Check if the source matches the allowlist
2. Block execution if it doesn't match
3. Report violations (if configured)

**Example:**
```
Content-Security-Policy: script-src 'self' https://apis.google.com
```

This allows scripts only from:
- Your own domain (`'self'`)
- `https://apis.google.com`

Any other script source will be blocked.

---

## CSP Directives Explained

### Core Directives

#### `default-src`
Sets the default policy for all resource types. Acts as a fallback for unspecified directives.

```http
Content-Security-Policy: default-src 'self'
```

#### `script-src`
Controls JavaScript execution. **Most critical for preventing XSS.**

```http
Content-Security-Policy: script-src 'self' https://cdn.example.com
```

**Keywords:**
- `'self'` - Same origin
- `'unsafe-inline'` - Allows inline `<script>` tags (⚠️ **NOT RECOMMENDED**)
- `'unsafe-eval'` - Allows `eval()`, `new Function()`, etc. (⚠️ **NOT RECOMMENDED**)
- `'nonce-{value}'` - Allows scripts with matching nonce
- `'strict-dynamic'` - Allows scripts loaded by trusted scripts

#### `style-src`
Controls stylesheet loading.

```http
Content-Security-Policy: style-src 'self' 'unsafe-inline' https://fonts.googleapis.com
```

#### `img-src`
Controls image loading.

```http
Content-Security-Policy: img-src 'self' data: https:
```

#### `connect-src`
Controls XHR, WebSocket, and EventSource connections.

```http
Content-Security-Policy: connect-src 'self' https://api.example.com
```

#### `font-src`
Controls web font loading.

```http
Content-Security-Policy: font-src 'self' https://fonts.gstatic.com
```

### Additional Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `base-uri` | Restricts `<base>` URLs | `base-uri 'self'` |
| `child-src` | Controls workers and frames | `child-src https://youtube.com` |
| `form-action` | Restricts form submissions | `form-action 'self'` |
| `frame-ancestors` | Prevents clickjacking | `frame-ancestors 'none'` |
| `media-src` | Controls video/audio | `media-src 'self'` |
| `object-src` | Controls plugins (Flash, etc.) | `object-src 'none'` |
| `report-uri` | Violation reporting endpoint | `report-uri /csp-report` |

---

## Common Patterns & Best Practices

### 1. **Avoid `unsafe-inline` and `unsafe-eval`**

These keywords disable CSP's primary protection mechanism.

#### ❌ Bad:
```http
Content-Security-Policy: script-src 'self' 'unsafe-inline' 'unsafe-eval'
```

#### ✅ Good:
```http
Content-Security-Policy: script-src 'self' https://cdn.example.com
```

### 2. **Use Nonces for Inline Scripts**

Instead of `'unsafe-inline'`, use nonces:

**Server-side (Python/FastAPI):**
```python
import secrets

nonce = secrets.token_urlsafe(16)
response.headers["Content-Security-Policy"] = f"script-src 'self' 'nonce-{nonce}'"
```

**HTML:**
```html
<script nonce="{{ nonce }}">
    // This script will execute
</script>
```

### 3. **Use External Scripts**

Move inline scripts to external `.js` files:

**❌ Bad:**
```html
<script>
    function doSomething() { ... }
</script>
```

**✅ Good:**
```html
<script src="/static/js/app.js"></script>
```

### 4. **Avoid String-Based `eval()`**

CSP blocks `eval()` and similar functions. Use alternatives:

**❌ Bad:**
```javascript
setTimeout("document.querySelector('a').style.display = 'none';", 10);
eval("var x = 5;");
new Function("return 5")();
```

**✅ Good:**
```javascript
setTimeout(function() {
    document.querySelector('a').style.display = 'none';
}, 10);

// Use JSON.parse instead of eval for JSON
const data = JSON.parse(jsonString);

// Use function declarations instead of new Function
function calculate() {
    return 5;
}
```

### 5. **Use `report-uri` for Monitoring**

Monitor CSP violations during development:

```http
Content-Security-Policy: default-src 'self'; report-uri /csp-report
```

### 6. **Start with Report-Only Mode**

Test your CSP before enforcing it:

```http
Content-Security-Policy-Report-Only: default-src 'self'; report-uri /csp-report
```

This reports violations without blocking resources.

---

## Removing `unsafe-eval` Safely

### Step 1: Identify Usage

Search your codebase for:
- `eval()`
- `new Function()`
- `setTimeout(string, ...)`
- `setInterval(string, ...)`
- `Function()`
- Template engines that use `eval`

### Step 2: Replace with Safe Alternatives

#### Replace `eval()` with `JSON.parse()`

**❌ Before:**
```javascript
const data = eval('(' + jsonString + ')');
```

**✅ After:**
```javascript
const data = JSON.parse(jsonString);
```

#### Replace String-Based `setTimeout`/`setInterval`

**❌ Before:**
```javascript
setTimeout("doSomething()", 1000);
```

**✅ After:**
```javascript
setTimeout(function() {
    doSomething();
}, 1000);

// Or with arrow functions:
setTimeout(() => doSomething(), 1000);
```

#### Replace `new Function()` with Regular Functions

**❌ Before:**
```javascript
const fn = new Function('a', 'b', 'return a + b');
```

**✅ After:**
```javascript
const fn = function(a, b) {
    return a + b;
};

// Or arrow function:
const fn = (a, b) => a + b;
```

### Step 3: Update Template Engines

If you use templating libraries that rely on `eval()`:

**Options:**
1. **Use precompiled templates** (Handlebars, Mustache)
2. **Use CSP-compatible frameworks** (React, Vue, Angular with `ng-csp`)
3. **Server-side rendering** instead of client-side templating

### Step 4: Test Thoroughly

1. Enable CSP in report-only mode
2. Monitor violation reports
3. Fix all violations
4. Switch to enforcing mode

---

## Implementation Strategies

### Strategy 1: Lockdown (Maximum Security)

For banking/financial applications:

```http
Content-Security-Policy: 
    default-src 'none';
    script-src https://cdn.mybank.net;
    style-src https://cdn.mybank.net;
    img-src https://cdn.mybank.net;
    connect-src https://api.mybank.com;
    child-src 'self';
    font-src 'self';
    form-action 'self';
    frame-ancestors 'none';
```

### Strategy 2: Progressive Enhancement

Start restrictive, then add sources as needed:

```http
# Phase 1: Report-only
Content-Security-Policy-Report-Only: default-src 'self'

# Phase 2: Add CDN
Content-Security-Policy: default-src 'self' https://cdn.example.com

# Phase 3: Add APIs
Content-Security-Policy: 
    default-src 'self' https://cdn.example.com;
    connect-src 'self' https://api.example.com
```

### Strategy 3: Nonce-Based (Recommended)

Use nonces for inline scripts/styles:

**Backend:**
```python
from fastapi import FastAPI, Request
import secrets

app = FastAPI()

@app.middleware("http")
async def add_csp_nonce(request: Request, call_next):
    nonce = secrets.token_urlsafe(16)
    request.state.nonce = nonce
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' 'nonce-{nonce}' 'unsafe-inline';"
    )
    return response
```

**Frontend:**
```html
<script nonce="{{ request.state.nonce }}">
    // Inline script with nonce
</script>
```

---

## Real-World Examples

### Example 1: Social Media Widgets

**Facebook Like Button:**
```http
Content-Security-Policy: child-src https://facebook.com
```

**Twitter Tweet Button:**
```http
Content-Security-Policy: 
    script-src https://platform.twitter.com;
    child-src https://platform.twitter.com
```

**Multiple Widgets:**
```http
Content-Security-Policy: 
    script-src https://apis.google.com https://platform.twitter.com;
    child-src https://plusone.google.com https://facebook.com https://platform.twitter.com
```

### Example 2: SSL-Only Site

```http
Content-Security-Policy: 
    default-src https:;
    script-src https: 'unsafe-inline';
    style-src https: 'unsafe-inline'
```

**Note:** `'unsafe-inline'` is used here only if you can't refactor legacy code immediately.

### Example 3: Modern SPA (Single Page Application)

```http
Content-Security-Policy: 
    default-src 'self';
    script-src 'self' 'strict-dynamic' https://cdn.example.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    img-src 'self' data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://api.example.com;
    frame-ancestors 'none';
```

---

## Troubleshooting

### Common Issues

#### Issue: "Refused to execute inline script"

**Cause:** Inline `<script>` tags are blocked.

**Solutions:**
1. Move script to external file
2. Use nonces
3. Use `'unsafe-inline'` (temporary, not recommended)

#### Issue: "Refused to evaluate a string as JavaScript"

**Cause:** `eval()` or `new Function()` is being used.

**Solutions:**
1. Replace `eval()` with `JSON.parse()`
2. Replace `new Function()` with regular functions
3. Use `'unsafe-eval'` (temporary, not recommended)

#### Issue: "Refused to load the script"

**Cause:** Script source not in allowlist.

**Solutions:**
1. Add source to `script-src` directive
2. Check for typos in URLs
3. Verify HTTPS vs HTTP

#### Issue: Styles not loading

**Cause:** Stylesheet source not allowed.

**Solutions:**
1. Add source to `style-src` directive
2. Use nonces for inline styles
3. Move styles to external CSS files

### Debugging Tips

1. **Check browser console** for CSP violation messages
2. **Use report-uri** to collect violation reports
3. **Start with report-only mode** to test without breaking functionality
4. **Use CSP evaluator tools** online to validate your policy

---

## Migration Checklist

### Phase 1: Assessment
- [ ] Audit codebase for `eval()`, `new Function()`, string-based `setTimeout`/`setInterval`
- [ ] Identify all external script/styles/font sources
- [ ] List all API endpoints used
- [ ] Document inline scripts/styles

### Phase 2: Preparation
- [ ] Move inline scripts to external files
- [ ] Replace `eval()` with `JSON.parse()`
- [ ] Replace string-based timers with function-based
- [ ] Update template engines if needed
- [ ] Set up CSP violation reporting endpoint

### Phase 3: Testing
- [ ] Enable CSP in report-only mode
- [ ] Monitor violation reports for 1-2 weeks
- [ ] Fix all violations
- [ ] Test all functionality thoroughly

### Phase 4: Deployment
- [ ] Switch from report-only to enforcing mode
- [ ] Monitor for new violations
- [ ] Have rollback plan ready
- [ ] Document CSP policy for team

### Phase 5: Optimization
- [ ] Remove unnecessary sources from allowlist
- [ ] Implement nonces for remaining inline code
- [ ] Consider `strict-dynamic` for modern apps
- [ ] Regular security audits

---

## Current Implementation Analysis

### Current CSP (in `backend/main.py`)

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' http://localhost:* https://*;"
)
```

### Issues Identified

1. **`'unsafe-eval'`** - Allows `eval()`, `new Function()`, etc. (Security risk)
2. **`'unsafe-inline'`** - Allows inline scripts/styles (Reduces CSP effectiveness)
3. **`http://localhost:*`** - Allows HTTP connections (Should use HTTPS in production)

### Recommended Improvements

#### Option 1: Remove `unsafe-eval` (Immediate)

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "  # Removed 'unsafe-eval'
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' https://*;"  # Removed http://localhost:*
)
```

#### Option 2: Use Nonces (Best Practice)

```python
import secrets

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        nonce = secrets.token_urlsafe(16)
        request.state.nonce = nonce
        
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self' 'nonce-{nonce}' 'unsafe-inline'; "
            f"img-src 'self' data: https:; "
            f"font-src 'self' data:; "
            f"connect-src 'self' https://*;"
        )
        return response
```

Then update HTML to use nonces:
```html
<script nonce="{{ request.state.nonce }}">
    // Your inline script
</script>
```

#### Option 3: External Scripts Only (Most Secure)

Move all JavaScript to external files:

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self'; "  # No 'unsafe-inline'
    "style-src 'self' 'unsafe-inline'; "  # Keep for CSS
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' https://*;"
)
```

---

## Additional Resources

- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Evaluator](https://csp-evaluator.withgoogle.com/) - Online CSP validator
- [CSP Quick Reference](https://content-security-policy.com/)
- [OWASP: Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

---

## Summary

**Key Takeaways:**

1. ✅ **Never use `'unsafe-eval'`** unless absolutely necessary
2. ✅ **Avoid `'unsafe-inline'`** - use nonces or external files instead
3. ✅ **Start with report-only mode** to test your policy
4. ✅ **Use `report-uri`** to monitor violations
5. ✅ **Replace `eval()` with `JSON.parse()`**
6. ✅ **Use function-based timers** instead of string-based
7. ✅ **Move inline scripts to external files** when possible
8. ✅ **Regularly audit and tighten** your CSP policy

**Remember:** CSP is a defense-in-depth security mechanism. It's not a silver bullet, but it significantly reduces the risk and impact of XSS attacks.

---

*Last Updated: December 2025*
*Based on: [web.dev CSP Documentation](https://web.dev/articles/csp?utm_source=devtools&utm_campaign=stable#eval_too)*

