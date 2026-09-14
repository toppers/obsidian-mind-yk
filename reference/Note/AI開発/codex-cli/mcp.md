---
date: 2026-06-30
description: "Codex の MCP 設定メモ — Claude 側の設定ファイル（.claude.json）との対応"
tags:
  - reference
  - codex
  - mcp
---

 codex
# 1
  - Claude 側: C:\Users\ykomi\.claude.json
      - project 別 MCP は projects.*.mcpServers 配下です。

  確認コマンドはこれが最短です。

  rtk codex mcp list --json
  rtk codex mcp get <name>

  Codex 側の実体確認なら config.toml、Claude Code 側も絡むなら .claude.json も見る、という切り分けでよいです。

# hook
 hook の定義本体は通常、各プロジェクト配下のこちらです。

  <project>\.codex\hooks.json

  ただし、現在の E:\Ccur\python3\gistx にはありませんでした。

  E:\Ccur\python3\gistx\.codex\hooks.json
  => 存在しません

  今回見つかったのは、Codex 側の信頼済み hook 状態です。

  C:\Users\ykomi\.codex\config.toml

  ここには hook 本体ではなく、例えば次のような「どの hooks.json のどの hook を信頼したか」の記録が入っています。

  [hooks.state.'C:\...\0-MD-2\.codex\hooks.json:post_tool_use:0:0']
  trusted_hash = "sha256:..."

  つまり結論は、gistx では hook 定義は未設定です。定義済み hook を見たい場合は、C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-
  2\.codex\hooks.json が該当します。

• Stop hook (failed)
  error: hook exited with code 1

# 2
 MCP client for `gemini-api-docs-mcp` failed to start: MCP startup failed: handshaking with MCP server failed: Send
  message error Transport
  [rmcp::transport::worker::WorkerTransport<rmcp::transport::streamable_http_client::StreamableHttpClientWorker<codex_rm
  cp_client::http_client_adapter::StreamableHttpClientAdapter>>] error: unexpected server response: HTTP 429: <!doctype
  html><meta charset="utf-8"><meta name=viewport content="width=device-width, initial-scale=1"><title>429</title>429 Too
  Many Requests, when send initialize request

⚠ MCP startup incomplete (failed: gemini-api-docs-mcp)

/mcp

🔌  MCP Tools

  • agentmemory
    • Auth: Unsupported
    • Tools: memory_audit, memory_export, memory_governance_delete, memory_recall, memory_save, memory_sessions,
    memory_smart_search

  • cloudflare-api
    • Auth: OAuth
    • Tools: docs, execute, search

  • codex
    • Auth: Unsupported
    • Tools: codex, codex-reply

  • codex_apps
    • Auth: Bearer token
    • Tools: adobe_acrobat.document_upload, adobe_acrobat.markdown_to_pdf, adobe_acrobat.pdf_combine,
    adobe_acrobat.pdf_compress, adobe_acrobat.pdf_create, adobe_acrobat.pdf_delete_pages, adobe_acrobat.pdf_edit_ui,
    adobe_acrobat.pdf_export, adobe_acrobat.pdf_ocr, adobe_acrobat.pdf_operation_status,
    adobe_acrobat.pdf_page_organize, adobe_acrobat.pdf_properties, adobe_acrobat.pdf_redact,
    adobe_acrobat.pdf_reorder_pages, adobe_acrobat.pdf_rotate_pages, adobe_acrobat.pdf_split,
    adobe_acrobat.pdf_to_image, adobe_acrobat.pdf_to_markdown, adobe_acrobat.pdf_viewer,
    adobe_photoshop.applyAdjustments, adobe_photoshop.applyEffects, adobe_photoshop.blurBackground,
    adobe_photoshop.getOptionsForAdjustments, adobe_photoshop.instructEdit, adobe_photoshop.removeBackground,
    adobe_photoshop.selectSubject, adobe_photoshop.selectionByPrompt, adobe_photoshop.undoEdits,
    adobe_photoshop.zeroCredits, agentic_slides_by_slidesgpt.apply_theme, agentic_slides_by_slidesgpt.create_slides,
    agentic_slides_by_slidesgpt.generate_image, agentic_slides_by_slidesgpt.show_theme_picker,
    agentic_slides_by_slidesgpt.upload_files, airtable.create_base, airtable.create_field,
    airtable.create_record_comment, airtable.create_records_for_table, airtable.create_table,
    airtable.delete_records_for_table, airtable.display_records_for_table, airtable.get_record_for_page,
    airtable.get_table_schema, airtable.list_bases, airtable.list_pages_for_base, airtable.list_record_comments,
    airtable.list_records_for_page, airtable.list_records_for_table, airtable.list_tables_for_base,
    airtable.list_workspaces, airtable.ping, airtable.search_bases, airtable.search_records, airtable.update_field,
    airtable.update_records_for_table, airtable.update_table, box.add_items_to_hub, box.ai_extract_freeform,
    box.ai_extract_structured_from_fields, box.ai_extract_structured_from_fields_enhanced,
    box.ai_extract_structured_from_metadata_template, box.ai_extract_structured_from_metadata_template_enhanced,
    box.ai_qa_hub, box.ai_qa_multi_file, box.ai_qa_single_file, box.copy_file, box.copy_folder, box.copy_hub,
    box.create_docgen_batch, box.create_docgen_template, box.create_file_comment, box.create_folder, box.create_hub,
    box.create_metadata_template, box.fetch, box.get_docgen_template_by_id, box.get_download_url, box.get_file_content,
    box.get_file_details, box.get_file_preview, box.get_folder_details, box.get_hub_details, box.get_hub_items,
    box.get_metadata_template_schema, box.get_preview_page, box.get_upload_url, box.list_docgen_templates,
    box.list_file_comments, box.list_folder_content_by_folder_id, box.list_hubs, box.list_item_collaborations,
    box.list_metadata_templates, box.list_tasks, box.move_file, box.move_folder, box.search, box.search_files_keyword,
    box.search_files_metadata, box.search_folders_by_name, box.set_file_metadata, box.set_folder_metadata,
    box.update_file_properties, box.update_folder_properties, box.update_hub, box.update_metadata_template,
    box.upload_file, box.upload_file_version, box.who_am_i, canva.autofill-design, canva.cancel-editing-transaction,
    canva.commit-editing-transaction, canva.copy-design, canva.create-design-from-brand-template, canva.create-design-
    from-candidate, canva.create-folder, canva.fetch, canva.generate-design, canva.generate-design-structured,
    canva.get-assets, canva.get-brand-template-dataset, canva.get-design, canva.get-design-content, canva.get-design-
    pages, canva.get-design-thumbnail, canva.get-presenter-notes, canva.help, canva.image-to-design, canva.import-
    design-from-url, canva.list-brand-kits, canva.list-comments, canva.list-folder-items, canva.move-item-to-folder,
    canva.perform-editing-operations, canva.prepare-design-generation, canva.request-outline-review, canva.resize-
    design, canva.resolve-shortlink, canva.search, canva.search-brand-templates, canva.search-designs, canva.search-
    folders, canva.start-editing-transaction, canva.upload-asset-from-url, context7.query-docs, context7.resolve-
    library-id, coursera.play_lecture_video, datacamp.code-along.get_by_id, datacamp.content.search,
    datacamp.course.get_by_id, datacamp.exercise.get_by_id, datacamp.tutorial.get_by_id, datacamp.webinar.get_by_id,
    dropbox.check_job_status, dropbox.copy, dropbox.create_file, dropbox.create_file_request, dropbox.create_folder,
    dropbox.create_shared_link, dropbox.delete, dropbox.download_link, dropbox.fetch, dropbox.file_preview,
    dropbox.get_file_metadata, dropbox.get_file_request, dropbox.get_shared_link_metadata, dropbox.list_file_requests,
    dropbox.list_file_revisions, dropbox.list_folder, dropbox.list_restore_events, dropbox.list_shared_links,
    dropbox.move, dropbox.restore_file_revision, dropbox.restore_folder, dropbox.search, dropbox.who_am_i,
    figma.add_code_connect_map, figma.create_new_file, figma.generate_deck, figma.generate_diagram,
    figma.generate_figma_design, figma.get_code_connect_map, figma.get_code_connect_suggestions,
    figma.get_context_for_code_connect, figma.get_design_context, figma.get_figjam, figma.get_libraries,
    figma.get_metadata, figma.get_screenshot, figma.get_variable_defs, figma.search_design_system,
    figma.send_code_connect_mappings, figma.upload_assets, figma.use_figma, figma.whoami,
    genspark_ai_slides.create_slide, github.add_comment_to_issue, github.add_issue_assignees, github.add_issue_labels,
    github.add_reaction_to_issue_comment, github.add_reaction_to_pr, github.add_reaction_to_pr_review_comment,
    github.add_review_to_pr, github.compare_commits, github.convert_pull_request_to_draft, github.create_blob,
    github.create_branch, github.create_commit, github.create_file, github.create_issue, github.create_pull_request,
    github.create_tree, github.delete_file, github.dismiss_pull_request_review, github.download_user_content,
    github.download_workflow_artifact, github.enable_auto_merge, github.fetch, github.fetch_blob, github.fetch_commit,
    github.fetch_commit_workflow_runs, github.fetch_file, github.fetch_issue, github.fetch_issue_comments,
    github.fetch_pr, github.fetch_pr_comments, github.fetch_pr_file_patch, github.fetch_pr_patch,
    github.fetch_workflow_job_logs, github.fetch_workflow_job_steps, github.fetch_workflow_run_artifacts,
    github.fetch_workflow_run_jobs, github.get_commit_combined_status, github.get_issue_comment_reactions,
    github.get_pr_diff, github.get_pr_info, github.get_pr_reactions, github.get_pr_review_comment_reactions,
    github.get_profile, github.get_repo, github.get_repo_collaborator_permission, github.get_user_login,
    github.get_users_recent_prs_in_repo, github.label_pr, github.list_installations, github.list_installed_accounts,
    github.list_pr_changed_filenames, github.list_pull_request_review_threads, github.list_pull_request_reviews,
    github.list_recent_issues, github.list_repositories, github.list_repositories_by_affiliation,
    github.list_repositories_by_installation, github.list_user_org_memberships, github.list_user_orgs,
    github.lock_issue_conversation, github.mark_pull_request_ready_for_review, github.merge_pull_request,
    github.remove_issue_assignees, github.remove_issue_label, github.remove_pull_request_reviewers,
    github.remove_reaction_from_issue_comment, github.remove_reaction_from_pr,
    github.remove_reaction_from_pr_review_comment, github.reply_to_review_comment,
    github.request_pull_request_reviewers, github.rerun_failed_workflow_run_jobs, github.rerun_workflow_job,
    github.resolve_review_thread, github.search, github.search_branches, github.search_commits,
    github.search_installed_repositories_streaming, github.search_installed_repositories_v2, github.search_issues,
    github.search_prs, github.search_repositories, github.unlock_issue_conversation, github.unresolve_review_thread,
    github.update_file, github.update_issue, github.update_issue_comment, github.update_pull_request, github.update_ref,
    github.update_review_comment, gmail.apply_labels_to_emails, gmail.archive_emails, gmail.batch_modify_email,
    gmail.batch_read_email, gmail.batch_read_email_threads, gmail.bulk_label_matching_emails, gmail.create_draft,
    gmail.create_label, gmail.delete_emails, gmail.forward_emails, gmail.get_profile, gmail.list_drafts,
    gmail.list_labels, gmail.read_attachment, gmail.read_email, gmail.read_email_thread, gmail.search_email_ids,
    gmail.search_emails, gmail.send_draft, gmail.send_email, gmail.update_draft, google_calendar.batch_read_event,
    google_calendar.create_event, google_calendar.delete_event, google_calendar.fetch, google_calendar.get_availability,
    google_calendar.get_colors, google_calendar.get_profile, google_calendar.read_event, google_calendar.respond_event,
    google_calendar.search, google_calendar.search_events, google_calendar.update_event, google_contacts.get_profile,
    google_contacts.read_contact, google_contacts.search_contacts, google_drive.batch_update_document,
    google_drive.batch_update_presentation, google_drive.batch_update_spreadsheet,
    google_drive.bulk_update_file_comments, google_drive.copy_file, google_drive.create_file,
    google_drive.create_folder, google_drive.create_presentation_from_template, google_drive.delete_file,
    google_drive.duplicate_sheet_in_new_spreadsheet, google_drive.export_file, google_drive.fetch,
    google_drive.fetch_file_revision, google_drive.find_document_text_range, google_drive.get_document,
    google_drive.get_document_comments, google_drive.get_document_paragraph_range, google_drive.get_document_tables,
    google_drive.get_document_text, google_drive.get_file_comments, google_drive.get_file_metadata,
    google_drive.get_presentation, google_drive.get_presentation_comments, google_drive.get_presentation_outline,
    google_drive.get_presentation_tables, google_drive.get_presentation_text, google_drive.get_profile,
    google_drive.get_slide, google_drive.get_slide_thumbnail, google_drive.get_spreadsheet_cells,
    google_drive.get_spreadsheet_comments, google_drive.get_spreadsheet_metadata, google_drive.get_spreadsheet_range,
    google_drive.import_document, google_drive.import_presentation, google_drive.import_spreadsheet,
    google_drive.list_drives, google_drive.list_file_revisions, google_drive.list_folder, google_drive.recent_documents,
    google_drive.search, google_drive.search_spreadsheet_rows, google_drive.share_file, google_drive.update_file,
    google_drive.upload_file, jotform.analyze_submissions, jotform.create_form, jotform.create_submission,
    jotform.display_form, jotform.edit_form, jotform.fetch, jotform.list_submissions, jotform.search,
    lovable.create_project, lovable.get_project, lovable.initiate_project, lovable.open_project_for_editing,
    mermaid_chart.display_mermaid, mermaid_chart.list_personal_diagrams, notion.fetch, notion.notion-create-comment,
    notion.notion-create-database, notion.notion-create-pages, notion.notion-create-view, notion.notion-duplicate-page,
    notion.notion-get-comments, notion.notion-get-teams, notion.notion-get-users, notion.notion-move-pages,
    notion.notion-query-data-sources, notion.notion-query-meeting-notes, notion.notion-update-data-source,
    notion.notion-update-page, notion.notion-update-view, notion.search, outliner.outline_generator,
    paypal.create_invoice, paypal.send_invoice, vercel.add_toolbar_reaction,
    vercel.change_toolbar_thread_resolve_status, vercel.check_domain_availability_and_price, vercel.deploy_to_vercel,
    vercel.edit_toolbar_message, vercel.get_access_to_vercel_url, vercel.get_agent_run, vercel.get_agent_run_trace,
    vercel.get_deployment, vercel.get_deployment_build_logs, vercel.get_project, vercel.get_runtime_errors,
    vercel.get_runtime_logs, vercel.get_toolbar_thread, vercel.import-claude-design-from-url,
    vercel.list_agent_run_projects, vercel.list_agent_runs, vercel.list_deployments, vercel.list_projects,
    vercel.list_teams, vercel.list_toolbar_threads, vercel.reply_to_toolbar_thread, vercel.search_vercel_documentation,
    vercel.web_fetch_vercel_url, wix.BrowseWixRESTDocsMenu, wix.CallWixSiteAPI, wix.CreateWixBusinessGuide,
    wix.ListWixSites, wix.ManageWixSite, wix.ReadFullDocsArticle, wix.ReadFullDocsMethodSchema,
    wix.SearchWixRESTDocumentation, wix.UploadImageToWixSite, wix.WixREADME, wix.WixSiteBuilder, wix.pullSiteCreationJob

  • context7
    • Auth: Not logged in
    • Tools: query-docs, resolve-library-id

  • gemini-api-docs-mcp
    • Auth: Unsupported
    • Tools: (none)

  • headroom
    • Auth: Unsupported
    • Tools: headroom_compress, headroom_retrieve, headroom_stats

  • node_repl
    • Auth: Unsupported
    • Tools: js, js_add_node_module_dir, js_reset

  • serena
    • Auth: Unsupported
    • Tools: activate_project, delete_memory, edit_memory, find_declaration, find_implementations,
    find_referencing_symbols, find_symbol, get_current_config, get_diagnostics_for_file, get_symbols_overview,
    initial_instructions, insert_after_symbol, insert_before_symbol, list_memories, onboarding, read_memory,
    rename_memory, rename_symbol, replace_symbol_body, safe_delete_symbol, search_for_pattern, write_memory
