#!/usr/bin/env python3
import os
import glob
from supabase import create_client
import datetime

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def extract_name_from_filename(filename):
    """Extract template name from filename."""
    # Pattern: <name>.html
    base_name = os.path.basename(filename)
    if base_name.endswith('.html'):
        return base_name[:-5] # Remove .html extension
    return None

def get_template_from_supabase(template_name):
    """Get template from Supabase by name."""
    response = (
        supabase.table("content_templates")
        .select("id, name, template")
        .eq("name", template_name)
        .execute()
    )
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def update_template_in_supabase(template_name, template_content):
    """Update template content in Supabase."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    response = (
        supabase.table("content_templates")
        .update({"template": template_content, "updated_at": now})
        .eq("name", template_name)
        .execute()
    )
    return response

def create_template_in_supabase(template_name, template_content):
    """Create a new template in Supabase."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    response = (
        supabase.table("content_templates")
        .insert({
            "name": template_name, 
            "template": template_content,
            # created_at and updated_at might be auto-set by db trigger
            # "created_at": now, 
            # "updated_at": now 
        })
        .execute()
    )
    return response

def main():
    # Find all HTML files in the templates directory
    template_files = glob.glob("templates/*.html")
    print(f"Found {len(template_files)} template files in templates/")
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for template_file in template_files:
        # Extract name from filename
        template_name = extract_name_from_filename(template_file)
        
        if not template_name:
            print(f"Skipping {template_file}: Invalid filename format")
            skipped_count += 1
            continue
        
        # Read HTML content from file
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as e:
            print(f"Error reading {template_file}: {e}")
            skipped_count += 1
            continue

        # Get existing template from Supabase
        existing_template = get_template_from_supabase(template_name)
        
        if existing_template:
            # Compare content and update if different
            if file_content != existing_template['template']:
                print(f"Updating template '{template_name}'")
                update_template_in_supabase(template_name, file_content)
                updated_count += 1
            else:
                print(f"No changes for template '{template_name}'")
        else:
            # Create new template
            print(f"Creating new template '{template_name}'")
            create_template_in_supabase(template_name, file_content)
            created_count += 1
            
    print("\nSummary:")
    print(f"- Created: {created_count}")
    print(f"- Updated: {updated_count}")
    print(f"- Skipped: {skipped_count}")
    print(f"- Total processed: {len(template_files)}")

if __name__ == "__main__":
    main() 