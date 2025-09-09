# DominateAI (DomAI) - Autonomous AI Automation Assistant

## 🤖 Overview
DominateAI is a fully autonomous AI automation assistant that combines multiple AI systems with powerful automation capabilities. It uses natural language understanding to execute complex tasks without rigid command structures.

## ⚡ Core AI Systems
- **AI Gateway**: Access to 100+ models via Vercel (GPT-4, Claude, Gemini, etc.)
- **Gemini 2.0 Flash**: Google's advanced AI via Vertex AI SDK
- **Self-Fixer**: Autonomous error detection and resolution

## 🚀 Key Capabilities
- **Natural Language Understanding**: No rigid commands - speak naturally
- **Autonomous Code Generation**: Generates and executes Python code based on requests
- **Comprehensive API Testing**: Designs its own test suites for performance, functionality, security
- **Website Building & Deployment**: Creates and deploys complete websites
- **Browser Automation**: Controls web browsers with Selenium
- **Mac System Control**: Automates macOS applications and system functions
- **Project Analysis**: Intelligently analyzes and completes coding projects
- **Self-Healing**: Automatically detects and fixes its own errors

## 📋 Core Files

### Main Executable
- `domai` - Main CLI interface with full autonomous capabilities

### AI Systems
- `ai_gateway_manager.py` - Vercel AI Gateway with 100+ models
- `working_gemini_integration.py` - Vertex AI Gemini integration
- `self_fixer.py` - Autonomous error detection and fixing

### Superpowers (Automation Modules)
- `superpower_manager.py` - Manages all automation capabilities
- `intelligent_executor.py` - Autonomous project implementation
- `project_analyzer.py` - Code analysis and completion planning
- `vercel_deployer.py` - Website deployment to Vercel
- `gcp_deployer.py` - Google Cloud Platform deployment

### Individual Superpowers
- `mac_control.py` - macOS system automation
- `browser_control.py` - Selenium web automation
- `website_builder.py` - HTML/CSS/JS generation
- `github_extender.py` - GitHub repository integration
- `n8n_controller.py` - Workflow automation

## 🛠️ Setup Requirements

### Required API Keys
1. **Vercel AI Gateway**: `vck_3iKW9qXMeku6PNU6IvrnjcrQWnyCTpR74DoE95edEdaHYhcSbR3uVLpH` (provided)
2. **Google Cloud/Vertex AI**: Set up Google Cloud credentials for Gemini access
3. **Vercel CLI**: For deployment capabilities

### Python Dependencies
```bash
pip install openai google-cloud-aiplatform selenium beautifulsoup4 requests gitpython
```

### System Requirements
- macOS (for Mac control features)
- Chrome browser (for Selenium automation)
- Vercel CLI (for deployment)

## 🎯 Usage Examples

### Natural Language Commands
```bash
./domai test your APIs
./domai build me a portfolio website  
./domai find my FlipAI project and finish it
./domai deploy this website to the cloud
./domai fix your errors
./domai what can you do?
```

## 🧠 How It Works

1. **Natural Language Processing**: DomAI uses Claude Sonnet 4 or Gemini to understand your request
2. **Autonomous Planning**: AI creates a comprehensive plan using available capabilities  
3. **Code Generation**: Generates Python code to execute the plan
4. **Autonomous Execution**: Runs the generated code with access to all superpowers
5. **Self-Correction**: If errors occur, automatically analyzes and fixes them

## 🔄 Key Innovation
Unlike traditional automation tools with rigid commands, DomAI uses its AI intelligence to:
- Understand requests in natural language
- Design its own comprehensive approaches (like API testing suites)
- Generate and execute code autonomously
- Self-diagnose and fix issues

## 🌟 Autonomous Features
- **Self-Designing**: Creates its own test suites, deployment strategies, etc.
- **Self-Executing**: Writes and runs Python code based on analysis
- **Self-Healing**: Detects errors and applies fixes automatically
- **Self-Improving**: Uses AI to optimize its own performance

This represents a new paradigm in automation - an AI that truly thinks and acts autonomously rather than following pre-programmed scripts.

---
*Built with Claude Code assistance*