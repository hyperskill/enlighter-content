#!/usr/bin/env python3
import os
import re
import glob
from supabase import create_client

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def extract_info_from_filename(filename):
    """Extract stage ID, order number, and title from filename."""
    # Pattern: <order_num>_<id>_<title>.html
    pattern = r'(\d+)_(\d+)_(.+)\.html$'
    match = re.match(pattern, os.path.basename(filename))
    
    if not match:
        return None
    
    order_num, stage_id, title = match.groups()
    return {
        'order_num': int(order_num),
        'id': int(stage_id),
        'title': title.replace('_', ' ')
    }

def get_stage_from_supabase(stage_id):
    """Get stage from Supabase by ID."""
    response = (
        supabase.table("stages")
        .select("id, title, description")
        .eq("id", stage_id)
        .execute()
    )
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def update_stage_in_supabase(stage_id, description):
    """Update stage description in Supabase."""
    response = (
        supabase.table("stages")
        .update({"description": description})
        .eq("id", stage_id)
        .execute()
    )
    return response

def main():
    # Find all HTML files in the project directories
    html_files = glob.glob("project_*/*.html")
    print(f"Found {len(html_files)} HTML files")
    
    updated_count = 0
    skipped_count = 0
    not_found_count = 0
    
    for html_file in html_files:
        # Extract information from filename
        file_info = extract_info_from_filename(os.path.basename(html_file))
        
        if not file_info:
            print(f"Skipping {html_file}: Filename doesn't match expected pattern")
            skipped_count += 1
            continue
        
        # Get stage from Supabase
        stage_id = file_info['id']
        stage = get_stage_from_supabase(stage_id)
        
        if not stage:
            print(f"Skipping {html_file}: Stage with ID {stage_id} not found in Supabase")
            not_found_count += 1
            continue
        
        # Read HTML content from file
        with open(html_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Compare content
        if file_content != stage['description']:
            print(f"Updating stage {stage_id} ({stage['title']})")
            update_stage_in_supabase(stage_id, file_content)
            updated_count += 1
        else:
            print(f"No changes for stage {stage_id} ({stage['title']})")
    
    print("\nSummary:")
    print(f"- Updated: {updated_count}")
    print(f"- Skipped (invalid filename): {skipped_count}")
    print(f"- Not found in Supabase: {not_found_count}")
    print(f"- Total processed: {len(html_files)}")

if __name__ == "__main__":
    main()
