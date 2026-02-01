# Cybersecurity Portfolio - Phase 1: 15 Bite-Sized Security Tools

## 🛡️ Overview

This repository contains **15 security tools** demonstrating practical cybersecurity skills across **four programming languages** (Python, Go, Rust, C#). Each tool is intentionally constrained to ≤300 lines, has no external dependencies, and focuses on solving one specific security problem.

**Note:** These are **portfolio demonstration artifacts**, not production software. They exist to showcase security thinking and coding skills.

## 📊 Tool Categories

### 🔍 **Security Operations** (Python Tools)
1. **CSV Security Report Cleaner** - Parse and filter vulnerability scan outputs
2. **Password Policy Enforcer** - Validate passwords against configurable rules  
3. **Log Highlighter & Filter** - Color-code and search security logs
4. **Quick IOC Checker** - Validate indicators of compromise

### 🌐 **Network & Web Security** (Go Tools)
5. **Network Service Heartbeat Monitor** - Check service availability
6. **SSL Certificate Expiry Checker** - Monitor certificate validity
7. **File Integrity Monitor** - Detect unauthorized file changes
8. **HTTP Security Header Scanner** - Audit web server security headers

### 🔒 **Systems & Memory Safety** (Rust Tools)
9. **Safe Config Parser & Linter** - Parse configs without panics
10. **Binary String Extractor** - Safely extract strings from binaries
11. **Memory-Efficient Log Search** - Process large logs efficiently
12. **Arithmetic Safety Checker** - Detect potential overflow issues

### 🪟 **Windows Security** (C# Tools)
13. **Active Directory Audit Reporter** - Generate AD security reports
14. **Windows Event Log Summarizer** - Analyze security event logs
15. **Installed Software Inventory** - Catalog installed applications

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** (for Python tools)
- **Go 1.19+** (for Go tools)
- **Rust 1.65+** (for Rust tools)
- **.NET 6.0+** (for C# tools)

### Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/cybersecurity-tools-phase1.git
cd cybersecurity-tools-phase1

# Run setup script (optional)
./scripts/setup_environment.sh

# Test a Python tool
cd python/01_csv_security_cleaner
python csv_cleaner.py --help

# Test a Go tool  
cd ../../go/05_network_heartbeat_monitor
go run main.go --help
```

## 🧪 Testing

Each tool includes comprehensive tests:
```bash
# Run all tests across all languages
./scripts/run_all_tests.sh

# Test specific language
cd python/01_csv_security_cleaner
python -m pytest tests/
```

## 📚 Documentation Structure

- **Tool-specific**: Each tool has its own README with usage examples
- **Language-specific**: Each language directory has patterns and guidelines
- **Repository-wide**: Overall architecture and design decisions

## ⚠️ Important Disclaimers

### This Repository Contains:
- ✅ **Synthetic test data** (generated, no real information)
- ✅ **Proof-of-concept code** (demonstration only)
- ✅ **Educational examples** (learning resources)
- ✅ **Portfolio artifacts** (skill demonstration)

### This Repository Does NOT Contain:
- ❌ **Personal Identifiable Information (PII)**
- ❌ **Protected Health Information (PHI)**
- ❌ **Copyrighted or proprietary material**
- ❌ **Production-ready software**
- ❌ **Sensitive configuration data**
- ❌ **Real credentials or secrets**

### Intended Use:
These tools are for:
- **Portfolio demonstration** - Showing cybersecurity skills
- **Educational purposes** - Learning security concepts
- **Interview preparation** - Technical discussion examples
- **Code review practice** - Example implementations

**Not for:** Production deployment, real security monitoring, or operational use.

## 🔧 Technical Constraints (Intentional Design)

| Constraint | Purpose | Benefit |
|------------|---------|---------|
| ≤300 lines/tool | Forces focus and clarity | Easy code review |
| No dependencies | Ensures portability | Runs anywhere |
| CLI-only | Shows core logic | No UI distractions |
| Synthetic data | Privacy protection | Safe to share |
| Frozen state | Complete artifacts | No maintenance needed |

## 📈 What These Tools Demonstrate

### Technical Skills:
- Multi-language proficiency (Python, Go, Rust, C#)
- Security problem-solving across domains
- Testing and validation practices
- Code quality and documentation

### Security Thinking:
- Vulnerability management approaches
- Monitoring and detection concepts
- Security automation patterns
- Defensive coding practices

### Professional Practices:
- Consistent coding standards
- Comprehensive documentation
- Systematic testing approach
- Clean repository organization

## 🏗️ Architecture

```
[Security Problem] → [Tool Implementation] → [Testing] → [Documentation]
       ↓                    ↓                    ↓            ↓
  Single focus        ≤300 lines          Synthetic data    Clear examples
  Clear purpose       No dependencies     No PII/PHI        Usage instructions
```

## 🤝 Contributing

While these are portfolio artifacts, suggestions are welcome:
1. **Issues**: Report problems or suggestions
2. **Discussions**: Share ideas or ask questions
3. **Documentation**: Improve clarity or examples

**Note:** Core implementations are frozen as demonstration artifacts.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Tools use only standard libraries for portability
- All sample data is synthetically generated
- Inspired by real-world security challenges
- Designed for educational and demonstration purposes

---

**Built as part of a comprehensive cybersecurity portfolio demonstrating 10+ years of infrastructure security experience.**
