# Chrome DevTools MCP Server Guide

## Overview

The Chrome DevTools MCP (Model Context Protocol) server enables AI coding assistants like Claude Code to control and inspect a live Chrome browser. This provides powerful capabilities for debugging web applications, analyzing performance, and automating browser interactions.

## Installation Status

✅ **Installed and Connected**
- Server: `chrome-devtools`
- Command: `npx chrome-devtools-mcp@latest`
- Status: Connected
- Node.js: v20.19.5 (compatible despite v22+ recommendation)

## Requirements

- **Node.js**: 22+ (recommended), 20+ (working)
- **Chrome**: Current stable version
- **Claude Code**: Latest version with MCP support

## Installation

The Chrome DevTools MCP server was installed using:

```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

This adds the server to your local Claude Code configuration at `~/.claude.json`.

## Capabilities

### 1. Performance Analysis
- Record performance traces
- Extract actionable performance insights
- Identify bottlenecks and optimization opportunities
- Analyze Core Web Vitals (LCP, FID, CLS)

### 2. Advanced Browser Debugging
- Analyze network requests
- Inspect API calls and responses
- Check browser console logs and errors
- Take screenshots for visual validation
- Debug JavaScript runtime issues

### 3. Reliable Browser Automation
- Uses Puppeteer for automation
- Automatically waits for action results
- Simulates user behaviors
- Navigate through web applications
- Fill forms and click elements

### 4. Real-time Inspection
- Inspect DOM structure
- Debug CSS styling and layout issues
- Analyze browser state
- Monitor real-time changes

## Usage Examples

### Example 1: Debug Network Issues
```
User: "A few images on localhost:8080 are not loading. What's happening?"

Claude will:
1. Launch Chrome via MCP server
2. Navigate to localhost:8080
3. Inspect network requests
4. Identify failed image loads
5. Analyze error responses
6. Provide diagnosis and fix recommendations
```

### Example 2: Performance Audit
```
User: "Run a performance audit on my dashboard page"

Claude will:
1. Start Chrome with DevTools
2. Use performance_start_trace tool
3. Navigate to dashboard
4. Record performance metrics
5. Analyze trace results
6. Provide optimization recommendations
```

### Example 3: Form Validation Issues
```
User: "Why does submitting the form fail after entering an email address?"

Claude will:
1. Open page in Chrome
2. Simulate entering email
3. Monitor console errors
4. Check network requests
5. Inspect form validation logic
6. Identify root cause
```

### Example 4: Visual Regression Testing
```
User: "Verify the new UI changes look correct across different screen sizes"

Claude will:
1. Launch Chrome
2. Navigate to updated pages
3. Take screenshots at various viewport sizes
4. Compare with expected layouts
5. Report visual inconsistencies
```

## Key MCP Tools

Based on the Chrome DevTools Protocol, the server provides tools for:

- **performance_start_trace**: Start recording performance trace
- **performance_stop_trace**: Stop recording and analyze trace
- **navigate**: Navigate to URLs
- **screenshot**: Capture visual state
- **console**: Access console logs and errors
- **network**: Inspect network activity
- **dom**: Inspect and manipulate DOM
- **evaluate**: Execute JavaScript in browser context

## Configuration

The MCP server is configured in `~/.claude.json`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]
    }
  }
}
```

### Advanced Configuration Options

You can customize the server with additional arguments:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--port=9222",
        "--headless=false"
      ]
    }
  }
}
```

## Verification

Check server status:

```bash
claude mcp list
```

Expected output:
```
chrome-devtools: npx chrome-devtools-mcp@latest - ✓ Connected
```

## Best Practices

### 1. Performance Testing
- Always close other Chrome instances before performance testing
- Use Incognito mode to avoid extension interference
- Test on realistic network conditions
- Capture multiple traces for consistency

### 2. Debugging Workflow
- Start with console errors
- Check network tab for failed requests
- Use screenshots to capture visual state
- Analyze performance for slow operations

### 3. Browser Automation
- Let Puppeteer handle waits automatically
- Use semantic selectors (data-testid, aria-labels)
- Handle loading states properly
- Test across different viewport sizes

### 4. Security Considerations
- Only use on local development environments
- Don't expose DevTools port to external networks
- Be cautious with credential-related debugging
- Clean up traces that may contain sensitive data

## Integration with Claude Code Workflows

### UI Testing with Chrome DevTools MCP

When combined with the `ui-bar-raiser` agent:

```
coordination-meta-agent
  ↓
ui-bar-raiser (uses Chrome DevTools MCP)
  • Navigate with Playwright
  • Take screenshots
  • Check accessibility
  • Monitor console errors
  ↓
If errors detected:
  root-cause-finder (analyzes DevTools data)
  ↓
  code-implementor (fixes issues)
  ↓
  ui-bar-raiser (re-validates)
```

### Full-Stack Debugging

```
User: "The API is slow and users are complaining"
  ↓
root-cause-finder agent
  • Use Chrome DevTools MCP for frontend analysis
  • Analyze network timing
  • Check console errors
  • Measure Core Web Vitals
  ↓
Coordinated fix:
  • Backend optimization
  • Frontend caching
  • Asset optimization
```

## Troubleshooting

### Issue: MCP Server Not Connecting

**Solution:**
1. Check Node.js version: `node --version`
2. Verify Chrome is installed and updated
3. Restart Claude Code
4. Clear npm cache: `npm cache clean --force`
5. Reinstall: `claude mcp remove chrome-devtools && claude mcp add chrome-devtools npx chrome-devtools-mcp@latest`

### Issue: Chrome Not Launching

**Solution:**
1. Check if Chrome is already running
2. Close all Chrome instances
3. Verify Chrome path in system
4. Check for port conflicts (default 9222)

### Issue: Performance Traces Failing

**Solution:**
1. Ensure sufficient disk space
2. Close resource-intensive applications
3. Use shorter trace durations
4. Check Chrome memory usage

### Issue: Timeout Errors

**Solution:**
1. Increase timeout in MCP configuration
2. Check network conditions
3. Verify target URL is accessible
4. Simplify test scenarios

## Resources

- **Official Documentation**: https://developer.chrome.com/blog/chrome-devtools-mcp
- **GitHub Repository**: https://github.com/ChromeDevTools/chrome-devtools-mcp
- **Tool Reference**: https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md
- **MCP Protocol**: https://modelcontextprotocol.io/docs/getting-started/intro
- **npm Package**: https://www.npmjs.com/package/chrome-devtools-mcp

## Alternative MCP Servers for Other IDEs

### VS Code / GitHub Copilot
```bash
code --add-mcp '{"name":"chrome-devtools","command":"npx","args":["chrome-devtools-mcp@latest"]}'
```

### Cursor
Settings > Tools & MCP > New MCP Server:
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]
    }
  }
}
```

### Gemini CLI
```bash
# Project-wide
gemini mcp add chrome-devtools npx chrome-devtools-mcp@latest

# Global
gemini mcp add -s user chrome-devtools npx chrome-devtools-mcp@latest
```

## Example Prompts for AI Assistants

### Performance Analysis
- "Run a performance audit on localhost:3000/dashboard"
- "Why is the homepage loading slowly?"
- "Analyze Core Web Vitals for my app"
- "What's causing the layout shift on mobile?"

### Debugging
- "Debug why the login form isn't submitting"
- "Check console errors on the checkout page"
- "Analyze failed network requests"
- "Why are images not loading?"

### Visual Testing
- "Take screenshots of all pages at mobile, tablet, and desktop sizes"
- "Verify the UI changes work correctly"
- "Check if the modal displays properly"
- "Compare current design with mockups"

### Automation
- "Navigate through the user registration flow and report any issues"
- "Test form validation by entering invalid data"
- "Verify all links work correctly"
- "Simulate a complete user journey from landing to checkout"

## Release Information

- **Release Date**: September 22, 2025 (Public Preview)
- **Status**: Public Preview
- **Maintainer**: Google Chrome DevTools Team
- **Community**: Active feedback and improvements ongoing

## Feedback and Issues

To report issues or suggest improvements:
- GitHub Issues: https://github.com/ChromeDevTools/chrome-devtools-mcp/issues
- Chrome DevTools Feedback: https://developer.chrome.com/docs/devtools/

---

**Status**: ✅ Installed and operational in this project
**Last Updated**: 2025-10-14
**Installed By**: Claude Code Assistant
