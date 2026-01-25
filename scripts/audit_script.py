#!/usr/bin/env python3
"""
Content Audit Script for Enlighter Projects
Checks content freshness, link validity, code accuracy, and version references
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from html.parser import HTMLParser


class ContentAuditor:
    """Audits HTML content for outdated information"""
    
    VERSION_PATTERNS = {
        'cursor': r'cursor\s+(?:version\s+)?(\d+\.\d+(?:\.\d+)?)',
        'python': r'python\s+(\d+\.\d+(?:\.\d+)?)',
        'node': r'node(?:\.js)?\s+(?:v)?(\d+\.\d+(?:\.\d+)?)',
        'mcp': r'mcp[- ](?:server|protocol)?[- ]?(?:v)?(\d+\.\d+(?:\.\d+)?)',
    }
    
    KNOWN_OUTDATED_VERSIONS = {
        'cursor': {'1.0', '1.1', '1.2'},  # Anything below 2.x is likely outdated
        'python': {'3.7', '3.8'},  # EOL versions
        'node': {'14', '16'},  # EOL versions
    }
    
    URL_PATTERN = re.compile(r'https?://[^\s<>"\']+')
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.project_name = project_path.name
        self.findings: List[Dict[str, Any]] = []
        self.files_checked: List[str] = []
        
    def audit_project(self) -> Dict[str, Any]:
        """Run full audit on project"""
        html_files = sorted(self.project_path.glob('*.html'))
        
        for html_file in html_files:
            self.audit_file(html_file)
            
        # Check project.json if exists
        project_json = self.project_path / 'project.json'
        if project_json.exists():
            self.audit_project_json(project_json)
            
        return self.generate_report()
    
    def audit_file(self, file_path: Path):
        """Audit individual HTML file"""
        self.files_checked.append(file_path.name)
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.add_finding(
                file=file_path.name,
                severity='high',
                issue=f'Cannot read file: {str(e)}',
                line=0
            )
            return
        
        lines = content.split('\n')
        
        # Check for outdated versions
        self.check_versions(file_path.name, content, lines)
        
        # Check for broken or potentially outdated URLs
        self.check_urls(file_path.name, content, lines)
        
        # Check for common issues
        self.check_common_issues(file_path.name, content, lines)
        
    def check_versions(self, filename: str, content: str, lines: List[str]):
        """Check for outdated version references"""
        content_lower = content.lower()
        
        for tool, pattern in self.VERSION_PATTERNS.items():
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                version = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                # Check if version is known to be outdated
                if tool in self.KNOWN_OUTDATED_VERSIONS:
                    major_minor = '.'.join(version.split('.')[:2])
                    if major_minor in self.KNOWN_OUTDATED_VERSIONS[tool]:
                        self.add_finding(
                            file=filename,
                            severity='high',
                            issue=f'Outdated {tool.title()} version: {version}',
                            line=line_num,
                            context=lines[line_num-1].strip()[:100] if line_num <= len(lines) else '',
                            suggested_fix=f'Update to latest stable {tool} version'
                        )
    
    def check_urls(self, filename: str, content: str, lines: List[str]):
        """Check for URLs that might be outdated"""
        urls = self.URL_PATTERN.findall(content)
        
        # Check for specific patterns that are likely outdated
        outdated_patterns = [
            (r'docs\.cursor\.sh/v1', 'Cursor v1 docs likely outdated'),
            (r'github\.com/[^/]+/[^/]+/tree/[a-f0-9]{40}', 'Specific commit hash - may be outdated'),
        ]
        
        for url in urls:
            line_num = content[:content.find(url)].count('\n') + 1
            
            for pattern, issue in outdated_patterns:
                if re.search(pattern, url):
                    self.add_finding(
                        file=filename,
                        severity='medium',
                        issue=issue,
                        line=line_num,
                        context=url,
                        suggested_fix='Verify URL is still valid and points to current version'
                    )
    
    def check_common_issues(self, filename: str, content: str, lines: List[str]):
        """Check for common content issues"""
        content_lower = content.lower()
        
        # Check for references to specific dates that might be outdated
        if '2024' in content or '2023' in content:
            matches = re.finditer(r'\b(202[34])\b', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                context = lines[line_num-1].strip()[:100] if line_num <= len(lines) else ''
                
                # Avoid false positives (copyright, version numbers)
                if 'copyright' not in context.lower() and 'version' not in context.lower():
                    self.add_finding(
                        file=filename,
                        severity='low',
                        issue=f'Reference to year {match.group(1)} - may be outdated',
                        line=line_num,
                        context=context,
                        suggested_fix='Review if this date reference is still relevant'
                    )
        
        # Check for "coming soon" or "beta" mentions
        if 'coming soon' in content_lower or 'beta' in content_lower:
            for i, line in enumerate(lines):
                if 'coming soon' in line.lower() or 'beta' in line.lower():
                    self.add_finding(
                        file=filename,
                        severity='medium',
                        issue='Contains "coming soon" or "beta" - verify if still accurate',
                        line=i + 1,
                        context=line.strip()[:100],
                        suggested_fix='Check if feature is now released'
                    )
    
    def audit_project_json(self, file_path: Path):
        """Audit project.json metadata"""
        self.files_checked.append(file_path.name)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check for metadata completeness
            required_fields = ['title', 'stages']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                self.add_finding(
                    file=file_path.name,
                    severity='medium',
                    issue=f'Missing required fields: {", ".join(missing_fields)}',
                    line=0
                )
                
        except json.JSONDecodeError as e:
            self.add_finding(
                file=file_path.name,
                severity='high',
                issue=f'Invalid JSON: {str(e)}',
                line=0
            )
        except Exception as e:
            self.add_finding(
                file=file_path.name,
                severity='high',
                issue=f'Error reading project.json: {str(e)}',
                line=0
            )
    
    def add_finding(self, file: str, severity: str, issue: str, line: int, 
                    context: str = '', suggested_fix: str = ''):
        """Add a finding to the report"""
        self.findings.append({
            'file': file,
            'severity': severity,
            'issue': issue,
            'line': line,
            'context': context,
            'suggested_fix': suggested_fix
        })
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate audit report"""
        high_priority = [f for f in self.findings if f['severity'] == 'high']
        medium_priority = [f for f in self.findings if f['severity'] == 'medium']
        low_priority = [f for f in self.findings if f['severity'] == 'low']
        
        status = 'ok'
        if high_priority:
            status = 'needs_urgent_updates'
        elif medium_priority:
            status = 'needs_updates'
        elif low_priority:
            status = 'minor_issues'
        
        return {
            'project': self.project_name,
            'audit_date': datetime.now().isoformat(),
            'files_checked': self.files_checked,
            'total_files': len(self.files_checked),
            'status': status,
            'findings_summary': {
                'total': len(self.findings),
                'high': len(high_priority),
                'medium': len(medium_priority),
                'low': len(low_priority)
            },
            'findings': self.findings
        }


def audit_projects(project_dirs: List[Path], output_dir: Path):
    """Audit multiple projects"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_reports = []
    
    for project_dir in project_dirs:
        print(f"\n{'='*70}")
        print(f"🔍 Auditing: {project_dir.name}")
        print('='*70)
        
        auditor = ContentAuditor(project_dir)
        report = auditor.audit_project()
        
        # Save individual report
        report_file = output_dir / f'{project_dir.name}_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Files checked: {report['total_files']}")
        print(f"✓ Total findings: {report['findings_summary']['total']}")
        print(f"  - High priority: {report['findings_summary']['high']}")
        print(f"  - Medium priority: {report['findings_summary']['medium']}")
        print(f"  - Low priority: {report['findings_summary']['low']}")
        print(f"✓ Report saved: {report_file.name}")
        
        all_reports.append(report)
    
    # Create summary report
    summary_file = output_dir / 'audit_summary.json'
    summary = {
        'audit_date': datetime.now().isoformat(),
        'projects_audited': len(all_reports),
        'projects': all_reports
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"📊 Summary report saved: {summary_file}")
    print('='*70)
    
    return all_reports


def main():
    """Main entry point"""
    # Get script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Find all project directories
    all_projects = sorted([d for d in project_root.iterdir() 
                          if d.is_dir() and d.name.startswith('project_')])
    
    print(f"📁 Found {len(all_projects)} projects")
    print(f"📍 Working directory: {project_root}")
    
    # For initial run, audit first 2 projects
    projects_to_audit = all_projects[:2]
    
    print(f"\n🎯 Will audit {len(projects_to_audit)} projects:")
    for p in projects_to_audit:
        print(f"  - {p.name}")
    
    # Create reports directory
    reports_dir = project_root / 'reports'
    
    # Run audit
    reports = audit_projects(projects_to_audit, reports_dir)
    
    print("\n✅ Audit complete!")
    

if __name__ == '__main__':
    main()
