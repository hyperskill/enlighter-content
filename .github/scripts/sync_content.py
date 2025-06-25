#!/usr/bin/env python3
import os
import re
import glob
import json
import subprocess
from supabase import create_client

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# GitHub repository information
# Default to 'enlighter-content' repository if not specified
GITHUB_REPO_OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "hyperskill")
GITHUB_REPO_NAME = os.environ.get("GITHUB_REPOSITORY", "enlighter-content").split("/")[-1]
GITHUB_BRANCH = os.environ.get("GITHUB_REF_NAME", "main")

# Check if we're in a pull request context
# This is used to determine if we need to generate draft IDs for projects and stages
IS_PULL_REQUEST = os.environ.get("GITHUB_EVENT_NAME") == "pull_request"

# Prefix for draft project and stage IDs to avoid overlap with real projects and stages
# Using a large negative number as a prefix to ensure no overlap with real IDs
# For example, if a project has ID 42, its draft ID would be -1000042
# This ensures that draft projects and stages have unique IDs in the database
# and don't conflict with real projects and stages
DRAFT_ID_PREFIX = -1000000

# IMPORTANT: Draft projects are only created for projects that have been modified in the pull request.
# This is determined by checking if any files in the project directory have been modified.
# If a project has not been modified, it will use its original ID, not a draft ID.
# This ensures that we only create draft projects for projects that are actually being changed,
# which reduces database clutter and makes it easier to track changes.

def get_modified_projects():
    """
    Get the list of project directories that have been modified in the pull request.
    Returns a set of project directory names (e.g., 'project_10_rag_based_support_agent').
    """
    if not IS_PULL_REQUEST:
        # If not in a pull request, return an empty set
        return set()

    try:
        # Get the base branch (usually 'main')
        base_branch = os.environ.get("GITHUB_BASE_REF", "main")

        # Get the list of modified files between the base branch and the current branch
        # Using git diff to get the list of modified files
        cmd = ["git", "diff", "--name-only", f"origin/{base_branch}...HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: Git command failed with exit status {result.returncode}")
            print(f"Error output: {result.stderr}")
            # Exit with error code 1
            exit(1)
        modified_files = result.stdout.strip().split('\n')

        # Extract project directories from modified files
        # Project directories follow the pattern 'project_*'
        modified_projects = set()
        for file_path in modified_files:
            # Skip empty lines
            if not file_path:
                continue

            # Extract project directory from file path
            # Example: 'project_10_rag_based_support_agent/file.html' -> 'project_10_rag_based_support_agent'
            match = re.match(r'(project_[^/]+)/', file_path)
            if match:
                modified_projects.add(match.group(1))

        print(f"Modified projects in this PR: {', '.join(modified_projects) if modified_projects else 'None'}")
        return modified_projects
    except Exception as e:
        print(f"Error getting modified projects: {e}")
        # Exit with error code 1
        exit(1)

def read_project_json(project_dir):
    """Read project information from project.json file."""
    project_json_path = os.path.join(project_dir, "project.json")
    if os.path.exists(project_json_path):
        try:
            with open(project_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading project.json for {project_dir}: {e}")
    return None

def extract_project_info_from_dirname(dirname):
    """Extract project ID and title from project.json."""
    # Read from project.json - it's mandatory
    project_json = read_project_json(dirname)

    # Exit with error if project.json is not found
    if project_json is None:
        print(f"ERROR: project.json is missing in directory {dirname}")
        print("project.json is mandatory, its absence is fatal.")
        exit(1)

    # Exit with error if required fields are missing
    if 'id' not in project_json or 'title' not in project_json:
        print(f"ERROR: project.json in {dirname} is missing required fields (id and/or title)")
        print("project.json must contain 'id' and 'title' fields.")
        exit(1)

    # Get the project ID
    project_id = int(project_json['id'])

    # Get the list of modified projects in the pull request
    modified_projects = get_modified_projects()

    # If we're in a pull request context and the project ID is positive,
    # and the project directory is in the list of modified projects,
    # generate a draft ID to avoid overlap with real projects
    if IS_PULL_REQUEST and project_id > 0 and os.path.basename(dirname) in modified_projects:
        # Use the draft ID prefix plus the original ID to ensure uniqueness
        project_id = DRAFT_ID_PREFIX + project_id
        print(f"Draft project detected in pull request. Original ID: {project_json['id']}, Draft ID: {project_id}")
    elif IS_PULL_REQUEST and project_id > 0:
        print(f"Project {dirname} not modified in this PR, using original ID: {project_id}")

    return {
        'id': project_id,
        'title': project_json['title'],
        'description': project_json.get('description', ''),
        'short_description': project_json.get('short_description', ''),
        'categories': project_json.get('categories', ''),
        'cover_url': project_json.get('cover_url', ''),
        'readme': project_json.get('readme', ''),
        'ides': project_json.get('ides', 'cursor')
    }

def get_project_from_supabase(project_id):
    """Get project from Supabase by ID."""
    response = (
        supabase.table("projects")
        .select("id, title, description, short_description, categories, cover_url, readme, ides")
        .eq("id", project_id)
        .execute()
    )

    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def create_project_in_supabase(project_info):
    """Create a new project in Supabase using project.json data."""
    project_id = project_info['id']
    title = project_info['title']

    # Prepare project data
    project_data = {
        "id": project_id,
        "title": title,
        "enabled": False,  # Default value in schema
        "visible": False,  # Default value in schema
        "available_in_web": False,  # Default value in schema
        "is_draft": project_id < 0,  # Set is_draft=true for draft projects (negative IDs)
    }

    # Add additional fields from project.json
    project_data.update({
        "description": project_info.get('description', title),
        "short_description": project_info.get('short_description', ''),
        "categories": project_info.get('categories', ''),
        "cover_url": project_info.get('cover_url', ''),
        "readme": project_info.get('readme', ''),
        "ides": project_info.get('ides', 'cursor')
    })

    response = (
        supabase.table("projects")
        .insert(project_data)
        .execute()
    )
    return response

def update_project_in_supabase(project_id, update_data):
    """Update project in Supabase with data from project.json."""
    response = (
        supabase.table("projects")
        .update(update_data)
        .eq("id", project_id)
        .execute()
    )
    return response

def extract_info_from_filename(filename):
    """Extract stage ID, order number, and title from filename."""
    # Pattern: <order_num>_<id>_<title>.html
    pattern = r'(\d+)_(\d+)_(.+)\.html$'
    match = re.match(pattern, os.path.basename(filename))

    if not match:
        return None

    order_num, stage_id, title = match.groups()

    # Convert to integers
    order_num_int = int(order_num)
    stage_id_int = int(stage_id)

    # Get the project directory from the filename
    # Example: 'project_10_rag_based_support_agent/1_37_go_ahead_and_sign_up_for_a_zendesk_mock.html'
    # -> 'project_10_rag_based_support_agent'
    project_dir = os.path.dirname(filename)

    # Get the list of modified projects in the pull request
    modified_projects = get_modified_projects()

    # If we're in a pull request context and the stage ID is positive,
    # and the project directory is in the list of modified projects,
    # generate a draft ID to avoid overlap with real stages
    if IS_PULL_REQUEST and stage_id_int > 0 and os.path.basename(project_dir) in modified_projects:
        # Use the draft ID prefix plus the original ID to ensure uniqueness
        stage_id_int = DRAFT_ID_PREFIX + stage_id_int
        print(f"Draft stage detected in pull request. Original ID: {stage_id}, Draft ID: {stage_id_int}")
    elif IS_PULL_REQUEST and stage_id_int > 0:
        print(f"Stage {filename} not in modified project, using original ID: {stage_id_int}")

    return {
        'order_num': order_num_int,
        'id': stage_id_int,
        'title': title.replace('_', ' ')
    }

def get_stage_from_supabase(stage_id):
    """Get stage from Supabase by ID."""
    response = (
        supabase.table("stages")
        .select("id, title, description, github_file_url, next_button_title")
        .eq("id", stage_id)
        .execute()
    )

    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def get_github_file_url(file_path):
    """Construct GitHub URL for a file."""
    return f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/blob/main/{file_path}"

def update_stage_in_supabase(stage_id, description, github_file_url, title, next_button_title):
    """Update stage description and GitHub URL in Supabase."""
    response = (
        supabase.table("stages")
        .update({
            "description": description,
            "github_file_url": github_file_url,
            "title": title,
            "next_button_title": next_button_title
        })
        .eq("id", stage_id)
        .execute()
    )
    return response

def extract_metadata_from_html(file_content):
    """Extract metadata from HTML file content."""
    metadata_pattern = r'<!-- Enlighter Metainfo\s*(\{.*?\})\s*-->'
    match = re.search(metadata_pattern, file_content, re.DOTALL)

    if match:
        try:
            metadata_json = match.group(1)
            metadata = json.loads(metadata_json)
            return metadata
        except Exception as e:
            print(f"Error parsing metadata: {e}")

    return None

def create_stage_in_supabase(stage_id, title, description, github_file_url, project_id, order_num, next_button_title=None):
    """Create a new stage in Supabase."""
    response = (
        supabase.table("stages")
        .insert({
            "id": stage_id,
            "title": title,
            "description": description,
            "github_file_url": github_file_url,
            "project_id": project_id,
            "order_num": order_num,
            "next_button_title": next_button_title
        })
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
    created_count = 0
    created_projects_count = 0
    updated_projects_count = 0

    # Track created draft projects for PR comments
    created_draft_projects = []

    # Keep track of processed projects to avoid duplicate checks
    processed_projects = set()

    for html_file in html_files:
        # Extract project information from directory name
        project_dir = os.path.dirname(html_file)
        project_info = extract_project_info_from_dirname(project_dir)

        if project_info and project_info['id'] not in processed_projects:
            # Check if project exists in Supabase
            project_id = project_info['id']
            project = get_project_from_supabase(project_id)

            if not project:
                # Create new project if it doesn't exist
                is_draft = project_id < 0
                print(f"Creating new project with ID {project_id} ({project_info['title']}), is_draft={is_draft}")
                create_project_in_supabase(project_info)
                created_projects_count += 1

                # If this is a draft project in a PR, track it for PR comment
                if IS_PULL_REQUEST and project_id < 0:
                    original_id = -project_id - DRAFT_ID_PREFIX
                    created_draft_projects.append({
                        "draft_id": project_id,
                        "original_id": original_id,
                        "title": project_info['title']
                    })
            else:
                # Check if project data in Supabase differs from project.json
                update_data = {}

                # Only include fields that are in project_info
                if 'title' in project_info and project_info['title'] != project.get('title', ''):
                    update_data["title"] = project_info['title']
                if 'description' in project_info and project_info['description'] != project.get('description', ''):
                    update_data["description"] = project_info['description']
                if 'short_description' in project_info and project_info['short_description'] != project.get('short_description', ''):
                    update_data["short_description"] = project_info['short_description']
                if 'categories' in project_info and project_info['categories'] != project.get('categories', ''):
                    update_data["categories"] = project_info['categories']
                if 'cover_url' in project_info and project_info['cover_url'] != project.get('cover_url', ''):
                    update_data["cover_url"] = project_info['cover_url']
                if 'readme' in project_info and project_info['readme'] != project.get('readme', ''):
                    update_data["readme"] = project_info['readme']
                if 'ides' in project_info and project_info['ides'] != project.get('ides', ''):
                    update_data["ides"] = project_info['ides']

                if update_data:
                    # Create a list of changed fields for detailed logging
                    changed_fields = list(update_data.keys())
                    print(f"Updating project with ID {project_id} ({project_info['title']}) - Changed fields: {', '.join(changed_fields)}")
                    update_project_in_supabase(project_id, update_data)
                    updated_projects_count += 1

            processed_projects.add(project_id)

        # Extract information from filename
        file_info = extract_info_from_filename(os.path.basename(html_file))

        if not file_info:
            print(f"Skipping {html_file}: Filename doesn't match expected pattern")
            skipped_count += 1
            continue

        # Get stage from Supabase
        stage_id = file_info['id']
        stage = get_stage_from_supabase(stage_id)

        # Read HTML content from file
        with open(html_file, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Extract metadata from HTML content
        metadata = extract_metadata_from_html(file_content)

        # Metadata is mandatory, exit with error if missing
        if metadata is None:
            print(f"ERROR: Metadata is missing in file {html_file}")
            print("Metadata is mandatory, its absence is fatal.")
            exit(1)

        # Get title and next_button_title from metadata
        title = metadata.get('title', file_info['title'])
        next_button_title = metadata.get('next_button_title')

        # Get GitHub URL for this file
        github_file_url = get_github_file_url(html_file)

        if not stage:
            # Create new stage if it doesn't exist
            if project_info:
                print(f"Creating new stage with ID {stage_id} ({title})")
                create_stage_in_supabase(stage_id, title, file_content, github_file_url, project_info['id'], file_info['order_num'], next_button_title)
                created_count += 1
            else:
                print(f"Error: Could not determine project ID for stage {stage_id}, skipping stage creation")
                skipped_count += 1
            continue

        # Compare content or metadata
        content_changed = file_content != stage['description']
        title_changed = metadata and title != stage.get('title', '')
        # Always check if next_button_title has changed, even if metadata is None
        # This ensures we can update next_button_title to null if needed
        next_button_changed = next_button_title != stage.get('next_button_title')
        # Check if github_file_url has changed
        github_url_changed = github_file_url != stage.get('github_file_url')

        if content_changed or title_changed or next_button_changed or github_url_changed:
            # Create a list of changed fields for detailed logging
            changes = []
            if content_changed:
                changes.append("content")
            if title_changed:
                changes.append("title")
            if next_button_changed:
                changes.append("next_button_title")
            if github_url_changed:
                changes.append("github_file_url")

            print(f"Updating stage {stage_id} ({title}) - Changed fields: {', '.join(changes)}")

            update_stage_in_supabase(stage_id, file_content, github_file_url, title, next_button_title)

            updated_count += 1
        else:
            print(f"No changes for stage {stage_id} ({stage.get('title', '')})")

    print("\nSummary:")
    print(f"- Updated content: {updated_count}")
    print(f"- Created new stages: {created_count}")
    print(f"- Created new projects: {created_projects_count}")
    print(f"- Updated existing projects: {updated_projects_count}")
    print(f"- Skipped (invalid filename): {skipped_count}")
    print(f"- Not found in Supabase: {not_found_count}")
    print(f"- Total processed: {len(html_files)}")

    # Output created draft projects for GitHub Actions
    if IS_PULL_REQUEST and created_draft_projects:
        print("\nCreated draft projects:")
        for project in created_draft_projects:
            # Format: DRAFT_PROJECT:<draft_id>:<original_id>:<title>
            print(f"DRAFT_PROJECT:{project['draft_id']}:{project['original_id']}:{project['title']}")

if __name__ == "__main__":
    main()
