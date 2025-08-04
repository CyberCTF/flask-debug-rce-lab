# Flask Debug Information Disclosure Lab

A vulnerable e-commerce application that demonstrates how Flask debug mode can expose sensitive framework version information through detailed error messages.

## Quick Start

```bash
docker pull cyberctf/flask-debug-rce-lab:latest
docker run -p 3206:3206 cyberctf/flask-debug-rce-lab:latest
```

Access the application at: http://localhost:3206

## What You'll Learn

- How Flask debug mode works
- Information disclosure vulnerabilities
- Framework fingerprinting techniques
- Error message analysis

## Vulnerability Overview

This lab features a TechStore e-commerce application built with Flask. The application has debug mode enabled, which causes detailed error messages to be displayed when exceptions occur. These error messages can reveal sensitive information about the underlying framework and its version.

## Reporting Issues

If you encounter any issues, please report them on our GitHub repository.
