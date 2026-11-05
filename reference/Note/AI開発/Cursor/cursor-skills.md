---
date: 2026-08-16
description: "Cursor スキル一覧 — cursor-app-control（プロジェクト作成・ユーザールール操作・ワークスペース移動）等の利用可能スキル控え"
tags:
  - reference
  - cursor
---

利用可能（ready）
cursor-app-control
Cursor 本体の操作。

create_project — 新規プロジェクト作成
cursor_dialog — ユーザールールの list/add/update/remove
move_agent_to_cloned_root — クローン済みワークスペースへ移動
move_agent_to_root — ワークスペースルート変更
open_automation — Automations UI を開く
open_resource — ファイル/ターミナル/URL を開く
rename_chat — チャット名変更
plugin-aws-serverless-aws-serverless-mcp
AWS Serverless / SAM。

configure_domain / deploy_webapp / update_webapp_frontend / webapp_deployment_help / deploy_serverless_app_help
sam_init / sam_build / sam_deploy / sam_local_invoke / sam_logs
get_iac_guidance / get_lambda_guidance / get_lambda_event_schemas / get_serverless_templates / get_metrics
list_registries / search_schema / describe_schema
esm_guidance / esm_optimize / esm_kafka_troubleshoot
secure_esm_dynamodb_policy / secure_esm_kinesis_policy / secure_esm_msk_policy / secure_esm_sqs_policy
plugin-azure-azure
Azure 操作用の階層ルーターが多いです。

リソース: subscription_list / group_list / group_resource_list / arm / compute / storage / storagesync / keyvault / role / policy / quota / pricing
アプリ: appservice / functionapp / functions / containerapps / aks / acr / azd / deploy
データ: cosmos / sql / mysql / postgres / redis / kusto / search
監視: monitor / applicationinsights / applens / insights / advisor / resourcehealth / grafana / workbooks / datadog
AI: foundry / foundryextensions / speech / sreagent
その他: documentation / get_azure_bestpractices / wellarchitectedframework / cloudarchitect / azureterraform / azureterraformbestpractices / bicepschema / azuremigrate / azurebackup / appconfig / communication / confidentialledger / deviceregistry / eventgrid / eventhubs / servicebus / servicefabric / signalr / iothub / fileshares / loadtesting / managedlustre / marketplace / resilience / virtualdesktop / extension_azqr / extension_cli_generate / extension_cli_install
plugin-cloudflare-cloudflare-docs
search_cloudflare_documentation
migrate_pages_to_workers_guide
plugin-context7-plugin-context7
ライブラリ公式ドキュメント。

resolve-library-id
query-docs
plugin-databases-on-aws-aurora-dsql
readonly_query / transact / get_schema
dsql_search_documentation / dsql_read_documentation / dsql_recommend / dsql_lint
plugin-deploy-on-aws-awsiac
validate_cloudformation_template / check_cloudformation_template_compliance
get_cloudformation_pre_deploy_validation_instructions / troubleshoot_cloudformation_deployment
search_cdk_documentation / search_cdk_samples_and_constructs / search_cloudformation_documentation
read_iac_documentation_page / cdk_best_practices
plugin-deploy-on-aws-awsknowledge
aws___search_documentation / aws___read_documentation
aws___list_regions / aws___get_regional_availability / aws___retrieve_skill
plugin-deploy-on-aws-awspricing
get_pricing_service_codes / get_pricing_service_attributes / get_pricing_attribute_values / get_pricing / get_price_list_urls
analyze_cdk_project / analyze_terraform_project / get_bedrock_patterns / generate_cost_report
plugin-ecc-chrome-devtools
Chrome DevTools 操作。

ページ: list_pages / select_page / new_page / close_page / navigate_page / resize_page
操作: click / hover / drag / fill / fill_form / type_text / press_key / upload_file / handle_dialog / emulate / wait_for
観察: take_snapshot / take_screenshot / evaluate_script / list_console_messages / get_console_message / list_network_requests / get_network_request
性能: lighthouse_audit / performance_start_trace / performance_stop_trace / performance_analyze_insight / take_heapsnapshot
plugin-firebase-firebase
認証/環境: firebase_login / firebase_logout / firebase_get_environment / firebase_update_environment
プロジェクト: firebase_list_projects / firebase_create_project / firebase_get_project / firebase_list_apps / firebase_create_app / firebase_create_android_sha / firebase_get_sdk_config
開発: firebase_init / firebase_deploy / firebase_deploy_status / firebase_get_security_rules / firebase_read_resources
ドキュメント: developerknowledge_search_documents / developerknowledge_get_documents / developerknowledge_answer_query
user-agentmemory
長期メモリ。

memory_recall / memory_save / memory_sessions / memory_smart_search
memory_export / memory_audit / memory_governance_delete
user-openaiDeveloperDocs
search_openai_docs / list_openai_docs / fetch_openai_doc
list_api_endpoints / get_openapi_spec
user-serena
コード知能 / シンボル編集。

開始: initial_instructions / activate_project / get_current_config / onboarding
検索: get_symbols_overview / find_symbol / find_declaration / find_implementations / find_referencing_symbols / get_diagnostics_for_file
編集: replace_content / replace_in_files / replace_symbol_body / insert_before_symbol / insert_after_symbol / rename_symbol / safe_delete_symbol
メモリ: write_memory / read_memory / list_memories / edit_memory / rename_memory / delete_memory
user-weather
get-alerts — 州の気象警報（米2文字コード）
get-forecast — 緯度経度の予報
認証が必要（needsAuth）
ツールは今のところ mcp_auth のみです。認証後に本体ツールが出ます。

サーバー	用途
plugin-cloudflare-cloudflare-bindings
Cloudflare Bindings
plugin-cloudflare-cloudflare-builds
Cloudflare Builds
plugin-cloudflare-cloudflare-observability
Cloudflare Observability
plugin-figma-figma
Figma
plugin-miro-miro
Miro
plugin-slack-slack
Slack
plugin-supabase-supabase
Supabase
plugin-vercel-vercel
Vercel
接続エラー（error）
発見に失敗しており、今は使えません。見えるのは mcp_auth のみです。

plugin-aws-amplify-aws-mcp
plugin-azure-cosmosdb-azure-cosmosdb
plugin-sagemaker-ai-aws-mcp
user-gemini-api-docs-mcp
mcp_auth は認証用の共通ツールで、ほぼ全サーバーにあります。ready サーバーでも未ログインだと実ツールが失敗することがあります。

## Related
- [[Cursor-プロジェクト設定の置き場所]] — .vscode/settings.json・.cursor/rules・AGENTS.md などプロジェクト単位設定の置き場所
- [[North Star]]
