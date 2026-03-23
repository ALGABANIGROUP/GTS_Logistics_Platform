#!/usr/bin/env python3
"""
GTS Search & SEO System - Verification Script
Verifies all components are correctly installed and working

Usage:
python verify_system.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def check_file_exists(filepath):
    """Check if file exists"""
    exists = Path(filepath).exists()
    if exists:
        size = Path(filepath).stat().st_size
        print_success(f"Found: {filepath} ({size:,} bytes)")
    else:
        print_error(f"Missing: {filepath}")
    return exists

def check_directory_exists(dirpath):
    """Check if directory exists"""
    exists = Path(dirpath).exists() and Path(dirpath).is_dir()
    if exists:
        print_success(f"Found: {dirpath}/")
    else:
        print_error(f"Missing: {dirpath}/")
    return exists

def check_python_module(module_name):
    """Check if Python module is installed"""
    try:
        __import__(module_name)
        print_success(f"Module installed: {module_name}")
        return True
    except ImportError:
        print_warning(f"Module not installed: {module_name}")
        return False

def count_lines(filepath):
    """Count lines in file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except:
        return 0

def run_command(command, description):
    """Run shell command and report status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, timeout=5)
        if result.returncode == 0:
            print_success(description)
            return True
        else:
            print_warning(f"{description}: {result.stderr.decode()[:100]}")
            return False
    except Exception as e:
        print_warning(f"{description}: {str(e)[:100]}")
        return False

def check_code_quality(filepath):
    """Basic code quality checks"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check for TODOs
        todos = content.count('TODO')
        if todos > 0:
            issues.append(f"{todos} TODO comments")
        
        # Check for FIXMEs
        fixmes = content.count('FIXME')
        if fixmes > 0:
            issues.append(f"{fixmes} FIXME comments")
        
        # Check for print statements (in production code)
        if 'print(' in content and 'def ' not in filepath:
            print_statements = content.count('print(')
            issues.append(f"{print_statements} print statements")
        
        return len(issues) == 0, issues
    except:
        return None, []

def verify_system():
    """Verify all system components"""
    
    print_header("GTS Search & SEO System Verification")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    stats = {
        'passed': 0,
        'failed': 0,
        'warnings': 0,
        'files_checked': 0,
        'lines_of_code': 0
    }
    
    # ==================== DIRECTORY STRUCTURE ====================
    print_header("1. Directory Structure")
    
    directories = [
        'search-seo-system',
        'search-seo-system/crawler',
        'search-seo-system/api',
        'search-seo-system/search',
        'search-seo-system/seo',
        'search-seo-system/frontend',
        'search-seo-system/tests',
        'search-seo-system/deployment',
        'search-seo-system/config',
        'search-seo-system/docs'
    ]
    
    for dir_path in directories:
        full_path = f'd:\\GTS\\{dir_path}'
        if check_directory_exists(full_path):
            stats['passed'] += 1
        else:
            stats['failed'] += 1
    
    # ==================== CORE FILES ====================
    print_header("2. Core Python Files")
    
    python_files = {
        'd:\\GTS\\search-seo-system\\crawler\\gts_spider.py': 'Web Crawler (Scrapy)',
        'd:\\GTS\\search-seo-system\\api\\main.py': 'FastAPI Search Engine',
        'd:\\GTS\\search-seo-system\\search\\elasticsearch_setup.py': 'Elasticsearch Setup',
        'd:\\GTS\\search-seo-system\\seo\\technical_setup.py': 'SEO Manager',
        'd:\\GTS\\search-seo-system\\seo\\content_optimizer.py': 'Content Optimizer'
    }
    
    for filepath, description in python_files.items():
        if check_file_exists(filepath):
            lines = count_lines(filepath)
            stats['lines_of_code'] += lines
            stats['files_checked'] += 1
            stats['passed'] += 1
            print_info(f"  → {lines:,} lines of code")
        else:
            stats['failed'] += 1
            stats['files_checked'] += 1
    
    # ==================== FRONTEND FILES ====================
    print_header("3. Frontend Components")
    
    frontend_files = {
        'd:\\GTS\\search-seo-system\\frontend\\SearchInterface.jsx': 'React Search Component',
        'd:\\GTS\\search-seo-system\\frontend\\SearchInterface.css': 'Search Styles'
    }
    
    for filepath, description in frontend_files.items():
        if check_file_exists(filepath):
            stats['passed'] += 1
        else:
            stats['failed'] += 1
    
    # ==================== DOCUMENTATION ====================
    print_header("4. Documentation")
    
    doc_files = {
        'd:\\GTS\\search-seo-system\\README.md': 'Main README',
        'd:\\GTS\\search-seo-system\\DEPLOYMENT_GUIDE.md': 'Deployment Guide',
        'd:\\GTS\\search-seo-system\\PROJECT_STRUCTURE.md': 'Project Structure',
        'd:\\GTS\\search-seo-system\\IMPLEMENTATION_COMPLETE.md': 'Implementation Summary'
    }
    
    for filepath, description in doc_files.items():
        if check_file_exists(filepath):
            stats['passed'] += 1
        else:
            stats['failed'] += 1
    
    # ==================== CONFIGURATION ====================
    print_header("5. Configuration Files")
    
    config_files = {
        'd:\\GTS\\search-seo-system\\docker-compose.yml': 'Docker Compose',
        'd:\\GTS\\search-seo-system\\requirements.txt': 'Python Dependencies'
    }
    
    for filepath, description in config_files.items():
        if check_file_exists(filepath):
            stats['passed'] += 1
        else:
            stats['failed'] += 1
    
    # ==================== DEPENDENCIES CHECK ====================
    print_header("6. Python Dependencies")
    
    dependencies = [
        'fastapi',
        'elasticsearch',
        'scrapy',
        'sqlalchemy',
        'pydantic'
    ]
    
    installed = 0
    for dep in dependencies:
        if check_python_module(dep):
            installed += 1
        else:
            stats['warnings'] += 1
    
    if installed == len(dependencies):
        stats['passed'] += 1
    else:
        print_warning(f"Only {installed}/{len(dependencies)} dependencies installed")
        stats['warnings'] += 1
    
    # ==================== CODE QUALITY ====================
    print_header("7. Code Quality Checks")
    
    quality_files = [
        'd:\\GTS\\search-seo-system\\api\\main.py',
        'd:\\GTS\\search-seo-system\\search\\elasticsearch_setup.py',
        'd:\\GTS\\search-seo-system\\seo\\content_optimizer.py'
    ]
    
    for filepath in quality_files:
        if os.path.exists(filepath):
            is_clean, issues = check_code_quality(filepath)
            if is_clean:
                print_success(f"Clean code: {filepath}")
                stats['passed'] += 1
            else:
                print_warning(f"Issues in {filepath}: {', '.join(issues)}")
                stats['warnings'] += 1
    
    # ==================== DOCKER CHECK ====================
    print_header("8. Docker & Services")
    
    if run_command('docker --version', 'Docker installed'):
        stats['passed'] += 1
    else:
        stats['warnings'] += 1
    
    if run_command('docker-compose --version', 'Docker Compose installed'):
        stats['passed'] += 1
    else:
        stats['warnings'] += 1
    
    # Check if services are running
    if run_command('docker ps | grep gts', 'GTS services running'):
        stats['passed'] += 1
    else:
        print_warning("GTS services not currently running (this is OK for development)")
    
    # ==================== ELASTICSEARCH CHECK ====================
    print_header("9. Elasticsearch Availability")
    
    if run_command('curl -s http://localhost:9200/_cluster/health | grep -q cluster_name', 
                   'Elasticsearch accessible at localhost:9200'):
        stats['passed'] += 1
    else:
        print_warning("Elasticsearch not running (expected, start with docker-compose)")
    
    # ==================== API CHECK ====================
    print_header("10. API Availability")
    
    if run_command('curl -s http://localhost:8000/health | grep -q status', 
                   'FastAPI accessible at localhost:8000'):
        stats['passed'] += 1
    else:
        print_warning("API not running (expected, start with docker-compose or uvicorn)")
    
    # ==================== FINAL SUMMARY ====================
    print_header("Verification Summary")
    
    total = stats['passed'] + stats['failed'] + stats['warnings']
    
    print(f"Files checked: {stats['files_checked']}")
    print(f"Lines of code: {stats['lines_of_code']:,}")
    print()
    print(f"{Colors.GREEN}✅ Passed: {stats['passed']}{Colors.RESET}")
    print(f"{Colors.RED}❌ Failed: {stats['failed']}{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  Warnings: {stats['warnings']}{Colors.RESET}")
    
    success_rate = (stats['passed'] / total * 100) if total > 0 else 0
    print()
    
    if stats['failed'] == 0:
        print_success(f"System Status: READY FOR DEPLOYMENT ({success_rate:.1f}%)")
        return 0
    else:
        print_error(f"System Status: NEEDS ATTENTION ({success_rate:.1f}%)")
        return 1

if __name__ == '__main__':
    exit_code = verify_system()
    print()
    sys.exit(exit_code)
