# Flask Debug Information Disclosure

A vulnerable e-commerce application running Flask with debug mode enabled that exposes sensitive framework version information through detailed error messages.

## Quick Start

```bash
docker pull cyberctf/flask-debug-rce-lab:latest
docker run -p 3206:3206 cyberctf/flask-debug-rce-lab:latest
```

Access the application at: http://localhost:3206

## Vulnerability Details

This lab demonstrates how Flask applications with debug mode enabled can leak sensitive information including framework versions through detailed error messages. The application contains several endpoints that can trigger errors, exposing Flask version information in the debug output.

## Reporting Issues

If you encounter any issues, please report them on our GitHub repository.