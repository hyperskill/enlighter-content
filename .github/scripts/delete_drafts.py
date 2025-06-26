#!/usr/bin/env python3
import os
import re
from supabase import create_client

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Check if we're in a pull request context
IS_PULL_REQUEST = os.environ.get("GITHUB_EVENT_NAME") == "pull_request"

# Get the PR number from the GitHub environment variables
PR_NUMBER = 0
if IS_PULL_REQUEST:
    # The PR number is available in the PR_NUMBER environment variable
    pr_number_env = os.environ.get("PR_NUMBER", "")
    if pr_number_env:
        try:
            PR_NUMBER = int(pr_number_env)
        except ValueError:
            print(f"ERROR: Could not convert PR_NUMBER environment variable '{pr_number_env}' to integer")
            print("PR_NUMBER must be a valid integer when in a pull request context.")
            exit(1)
    else:
        print("ERROR: PR_NUMBER environment variable not set")
        print("PR_NUMBER must be set when in a pull request context.")
        exit(1)

# Draft project and stage IDs use the format: -<id_project><PR_NUMBER:5 digits with leading zeros>
# For example, if a project has ID 42 and PR_NUMBER is 123, its draft ID would be -42000123

def delete_stage_from_supabase(stage_id):
    """Delete a stage from Supabase by ID."""
    response = (
        supabase.table("stages")
        .delete()
        .eq("id", stage_id)
        .execute()
    )
    return response

def delete_project_from_supabase(project_id):
    """Delete a project from Supabase by ID."""
    response = (
        supabase.table("projects")
        .delete()
        .eq("id", project_id)
        .execute()
    )
    return response

def delete_draft_projects():
    """Delete draft projects created in the current pull request and their associated stages from Supabase."""
    print("\nDeleting draft projects and stages created in this pull request...")

    # Get all draft projects (negative IDs)
    response = (
        supabase.table("projects")
        .select("id, title")
        .lt("id", 0)  # Draft projects have negative IDs
        .execute()
    )

    if not response.data:
        print("No draft projects found to delete.")
        return

    draft_projects = response.data
    print(f"Found {len(draft_projects)} total draft projects.")

    deleted_projects_count = 0
    deleted_stages_count = 0

    for project in draft_projects:
        project_id = project['id']
        project_title = project['title']

        # Calculate the original project ID from the draft ID
        # Try the new format first: -<id_project><PR_NUMBER:5 digits with leading zeros>
        # For example, if draft_id=-42000123, the original ID would be 42
        project_id_str = str(-project_id)
        if len(project_id_str) >= 6:  # At least 1 digit for project ID + 5 digits for PR number
            # Extract the PR number from the draft ID (last 5 digits)
            draft_pr_number = int(project_id_str[-5:])
            # Extract the original project ID (all digits except the last 5)
            original_id = int(project_id_str[:-5])

            # If the PR number from the draft ID matches the current PR number,
            # then this draft was created in the current PR
            if draft_pr_number == PR_NUMBER:
                print(f"Draft project {project_id} was created in the current PR (PR #{PR_NUMBER})")
            else:
                print(f"Draft project {project_id} was created in PR #{draft_pr_number}, not the current PR (#{PR_NUMBER})")
        else:
            # Skip projects with invalid format
            print(f"Skipping draft project {project_id} as it doesn't use the expected format")
            continue

        # Skip this draft project if it was created in a different PR
        # We only want to delete drafts from the current PR
        if len(project_id_str) >= 6 and draft_pr_number != PR_NUMBER:
            print(f"Skipping draft project {project_id} ({project_title}) as it was created in PR #{draft_pr_number}, not the current PR (#{PR_NUMBER})")
            continue

        print(f"Processing draft project {project_id} ({project_title}) with original ID {original_id}")

        # Get all stages for this project
        stages_response = (
            supabase.table("stages")
            .select("id, title")
            .eq("project_id", project_id)
            .execute()
        )

        if stages_response.data:
            stages = stages_response.data
            print(f"Found {len(stages)} stages for draft project {project_id} ({project_title})")

            # Delete all stages for this project
            for stage in stages:
                stage_id = stage['id']
                stage_title = stage['title']
                print(f"Deleting draft stage {stage_id} ({stage_title})")
                delete_stage_from_supabase(stage_id)
                deleted_stages_count += 1

        # Delete the project
        print(f"Deleting draft project {project_id} ({project_title})")
        delete_project_from_supabase(project_id)
        deleted_projects_count += 1

    print(f"\nDeletion summary:")
    print(f"- Deleted draft projects: {deleted_projects_count}")
    print(f"- Deleted draft stages: {deleted_stages_count}")
    print(f"- Total deleted entities: {deleted_projects_count + deleted_stages_count}")

def main():
    delete_draft_projects()

if __name__ == "__main__":
    main()
