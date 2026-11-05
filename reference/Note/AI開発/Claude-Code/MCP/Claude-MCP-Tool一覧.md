---
date: 2026-08-17
description: "Claude Code で利用可能なMCP toolのサーバー別一覧（claude-in-chrome等）"
tags:
  - reference
  - claude-code
  - mcp
---

# Claude
利用可能なMCP toolを一覧化します。以下、サーバーごとにまとめます。

claude-in-chrome

ブラウザ自動操作
- tabs_context_mcp, navigate, computer, read_page, tabs_create_mcp, tabs_close_mcp
- browser_batch, file_upload, find, form_input, get_page_text, gif_creator, javascript_tool
- list_connected_browsers, read_console_messages, read_network_requests, resize_window
- select_browser, shortcuts_execute, shortcuts_list, switch_browser, upload_image

claude_ai_* (claude.ai連携サービス群)

- Bitly: authenticate, complete_authentication
- Box: authenticate, complete_authentication
- Canva: authenticate, complete_authentication
- Context7: query-docs, resolve-library-id
- Figma: add_code_connect_map, create_new_file, download_assets, export_video, generate_diagram, get_code_connect_map, get_code_connect_suggestions, get_context_for_code_connect, get_design_context, get_figjam, get_figma_skill, get_libraries, get_metadata, get_motion_context, get_screenshot, get_shader_effect, get_shader_fill, get_variable_defs, list_file_components_for_code_connect, list_shader_effects, list_shader_fills, read_skill_uri, search_design_system, send_code_connect_mappings, upload_assets, use_figma, weave_cancel_tool_run, weave_get_tool_inputs, weave_get_tool_run_output, weave_list_tools, weave_run_tool, weave_upload_asset, whoami
- GitLab: authenticate, complete_authentication
- Gmail: apply_sensitive_message_label, apply_sensitive_thread_label, create_draft, create_label, delete_label, forward, get_message, get_thread, label_message, label_thread, list_drafts, list_labels, mark_message_spam, mark_thread_spam, reply, search_threads, send_message, trash_message, trash_thread, unlabel_message, unlabel_thread, unmark_message_spam, unmark_thread_spam, untrash_message, untrash_thread, update_draft, update_label
- Google Calendar: create_event, delete_event, get_event, list_calendars, list_events, respond_to_event, search_events, suggest_time, update_event
- Google Drive: copy_file, create_file, download_file_content, get_file_metadata, get_file_permissions, list_recent_files, read_file_content, search_files, share_file, trash_file, update_file
- Hugging Face: authenticate, complete_authentication
- Mermaid Chart: authenticate, complete_authentication
- PayPal: authenticate, complete_authentication
- Slack: slack_add_reaction, slack_create_canvas, slack_create_conversation, slack_get_reactions, slack_list_channel_members, slack_read_canvas, slack_read_channel, slack_read_file, slack_read_thread, slack_read_user_profile, slack_schedule_message, slack_search_channels, slack_search_emojis, slack_search_public, slack_search_public_and_private, slack_search_users, slack_send_message, slack_send_message_draft, slack_update_canvas
- Stripe: authenticate, complete_authentication

headroom

- headroom_compress, headroom_retrieve, headroom_stats

plugin_ecc_chrome-devtools

- click, close_page, drag, emulate, evaluate_script, fill, fill_form, get_console_message, get_network_request, handle_dialog, hover, lighthouse_audit, list_console_messages, list_network_requests, list_pages, navigate_page, new_page, performance_analyze_insight, performance_start_trace, performance_stop_trace, press_key, resize_page, select_page, take_heapsnapshot, take_screenshot, take_snapshot, type_text, upload_file, wait_for

plugin_vercel_vercel

- add_toolbar_reaction, buy_addon, buy_credits, buy_domain, buy_pro, change_toolbar_thread_resolve_status, check_domain_availability_and_price, create_git_project, deploy_to_vercel, edit_toolbar_message, get_access_to_vercel_url, get_agent_run, get_agent_run_trace, get_deployment, get_deployment_build_logs, get_domain_order, get_project, get_project_deployment_protection, get_purchase_quote, get_runtime_errors, get_runtime_logs, get_toolbar_thread, get_web_analytics, import-claude-design-from-url, list_agent_run_projects, list_agent_runs, list_deployments, list_projects, list_teams, list_toolbar_threads, reply_to_toolbar_thread, search_vercel_documentation, update_project_deployment_protection, web_fetch_vercel_url

pmb (Personal Memory Bank)

- find_lessons, list_goals, mark_lesson_followed, prepare, project_overview, recall, record_batch, record_keyed_fact, session_brief, update_goal

qmd (Quick Markdown Search)

- ask, collection_add, collection_list, collection_remove, collection_rename, context_add, context_list, context_remove, db_cleanup, db_vacuum, embed, expand, get, ls, models_info, models_list, models_pull, multi_get, qsearch, query, rerank, search, status, update, vsearch

serena (コード解析/シンボル操作)

- delete_memory, edit_memory, find_declaration, find_implementations, find_referencing_symbols, find_symbol, get_diagnostics_for_file, get_symbols_overview, initial_instructions, insert_after_symbol, insert_before_symbol, list_memories, onboarding, read_memory, rename_memory, rename_symbol, replace_content, replace_in_files, replace_symbol_body, safe_delete_symbol, write_memory

---
これらは全て**deferred(遅延ロード)**状態のため、実際に呼び出す前に ToolSearch でスキーマをロードする必要があります。特定のツールを使いたい場合は教えてください。

## Related
- [[Claude-Code-記事索引]]
