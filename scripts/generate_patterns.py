import os
import yaml

patterns = [
    # --- STORAGE (S3, EFS, FSx) ---
    ("s3_access_denied", "security_failure", ["missing_policy", "kms_mismatch", "bucket_policy_restriction"], "Application receives 403 Forbidden due to policy mismatch or missing KMS key permission.", ["iam_access_analyzer", "s3_bucket_policy", "kms_key_policy"]),
    ("s3_lifecycle_timing_issue", "data_loss", ["lifecycle_rule_too_aggressive", "object_deletion_before_processing"], "Objects are deleted or transitioned to Glacier before they are processed by analytics jobs.", ["s3_lifecycle_delay", "s3_object_tagging", "eventbridge_trigger"]),
    ("s3_request_limit_throttling", "performance_degradation", ["high_rps_per_prefix", "sequential_key_names"], "Exceeding 3,500 PUT or 5,500 GET requests per second per prefix.", ["s3_prefix_randomization", "cloudfront_distribution", "s3_intelligent_tiering"]),
    ("s3_object_lock_retention_error", "compliance_failure", ["governance_mode_bypass", "incorrect_retention_period"], "Unable to delete or modify objects due to active Object Lock beyond expected duration.", ["s3_batch_operations", "compliance_mode_review"]),
    ("s3_replication_latency", "data_inconsistency", ["crr_bandwidth_limit", "large_object_size", "kms_key_mismatch"], "Cross-Region Replication (CRR) lag exceeds RPO requirements.", ["s3_rtc_metrics", "direct_connect_optimization"]),
    ("efs_burst_credit_exhaustion", "performance_degradation", ["general_purpose_mode", "burst_throughput_depletion"], "Throughput drops to baseline (50 KiB/s per GiB) after exhausting burst credits.", ["provisioned_throughput", "efs_lifecycle_management"]),
    ("efs_file_limit_exceeded", "resource_exhaustion", ["too_many_files_in_directory", "nfs_lookup_latency"], "Performance degrades when directory contains millions of files.", ["directory_sharding", "fsx_lustre"]),
    ("fsx_windows_ad_join_failure", "connectivity_failure", ["dns_resolution_failure", "security_group_block", "ad_service_account_lock"], "FSx fails to join Active Directory due to network or permission issues.", ["dhcp_options_set", "directory_service_debug"]),
    ("ebs_volume_stuck_optimizing", "operational_delay", ["volume_modification", "insufficient_io_credit"], "Volume modification takes hours, blocking further changes.", ["snapshot_restore", "wait_for_optimization"]),
    ("ebs_io_latency_spike", "performance_degradation", ["noisy_neighbor", "instance_throughput_limit"], "Unexpected latency due to underlying hardware contention or instance limit.", ["io2_block_express", "dedicated_instance"]),

    # --- COMPUTE (EC2, Lambda, Batch) ---
    ("ec2_status_check_failed", "availability_failure", ["system_status_check", "instance_status_check", "underlying_hardware_fault"], "Instance becomes unreachable due to hardware or OS failure.", ["auto_recovery", "cloudwatch_alarm_reboot"]),
    ("ec2_launch_template_version_mismatch", "deployment_failure", ["wrong_ami_id", "userdata_error"], "ASG fails to launch instances due to invalid template version.", ["launch_template_versioning", "asg_instance_refresh"]),
    ("ec2_spot_interruption_warning", "availability_risk", ["spot_price_spike", "capacity_reclamation"], "Spot instances are reclaimed with 2-minute warning.", ["spot_fleet", "checkpointing", "mixed_instances_policy"]),
    ("lambda_concurrency_limit_account", "throttling", ["account_level_limit", "burst_traffic"], "Functions throttled due to hitting account-wide concurrency limit (default 1000).", ["service_quota_increase", "provisioned_concurrency"]),
    ("lambda_layer_version_error", "deployment_failure", ["deleted_layer_version", "permission_denied"], "Function fails to start because the specified layer version is missing.", ["serverless_framework_layer", "lambda_layer_permission"]),
    ("lambda_vpc_enso_timeout", "network_failure", ["eni_creation_latency", "subnet_ip_exhaustion"], "Function times out waiting for ENI attachment in VPC.", ["vpc_endpoint", "subnet_sizing"]),
    ("batch_job_stuck_runnable", "resource_exhaustion", ["v_cpu_limit", "compute_environment_invalid"], "AWS Batch jobs remain in RUNNABLE state indefinitely.", ["compute_environment_troubleshooting", "job_queue_priority"]),
    ("batch_docker_pull_rate_limit", "deployment_failure", ["docker_hub_limit", "public_image_pull"], "Job fails due to Docker Hub rate limiting.", ["ecr_pull_through_cache", "authenticated_pull"]),

    # --- DATABASE (RDS, DynamoDB, ElastiCache, Neptune) ---
    ("rds_storage_full", "availability_failure", ["autoscaling_disabled", "log_growth", "temp_files"], "Database instance enters STORAGE_FULL state and stops accepting writes.", ["storage_autoscaling", "cloudwatch_storage_alarm"]),
    ("rds_cpu_high_utilization", "performance_degradation", ["inefficient_queries", "missing_index"], "CPU stays at 100%, causing query timeouts.", ["performance_insights", "read_replica", "instance_resize"]),
    ("rds_backup_window_contention", "performance_degradation", ["snapshot_latency", "heavy_write_load"], "Database latency spikes during automated backup window.", ["backup_window_tuning", "read_replica_offload"]),
    ("dynamodb_partition_split_hotspot", "throttling", ["sequential_writes", "imbalanced_access"], "Traffic is skewed to a single partition key, causing throttling despite overall capacity.", ["sharding_suffix", "adaptive_capacity"]),
    ("dynamodb_lsi_size_limit", "schema_error", ["item_collection_size_limit", "10gb_limit"], "Writes fail because Local Secondary Index collection exceeds 10GB limit.", ["gsi_substitution", "schema_redesign"]),
    ("elasticache_eviction_storm", "data_loss", ["maxmemory_policy", "memory_fragmentation"], "Redis evicts keys aggressively due to memory pressure.", ["cluster_resize", "param_group_tuning"]),
    ("elasticache_failover_latency", "availability_failure", ["dns_ttl", "client_reconnection"], "Application sees errors during primary node failover.", ["cluster_mode_enabled", "client_library_retry"]),
    ("neptune_query_timeout", "performance_degradation", ["complex_gremlin_traversal", "large_graph_scan"], "Graph queries time out due to lack of optimization.", ["query_explain", "instance_resize"]),

    # --- NETWORKING (VPC, Route53, CloudFront, ELB) ---
    ("vpc_subnet_ip_exhaustion", "resource_exhaustion", ["small_cidr_block", "high_pod_density"], "No available IP addresses in subnet for new resources.", ["new_subnet_association", "secondary_cidr"]),
    ("vpc_endpoint_policy_denial", "connectivity_failure", ["restrictive_vpce_policy", "s3_access_denied"], "VPC Endpoint policy blocks legitimate access to service.", ["policy_simulator", "least_privilege_review"]),
    ("route53_health_check_flapping", "availability_instability", ["sensitive_threshold", "network_jitter"], "Health check marks endpoint unhealthy/healthy repeatedly.", ["health_check_tuning", "latency_measurement"]),
    ("route53_resolver_rule_loop", "network_loop", ["conditional_forwarding", "circular_dependency"], "DNS resolution loops between On-Prem and Cloud.", ["resolver_rule_audit", "dns_debug"]),
    ("cloudfront_502_bad_gateway", "connectivity_failure", ["origin_ssl_protocol", "timeout_origin"], "CloudFront cannot connect to the origin or SSL handshake fails.", ["ssl_policy_match", "origin_timeout_increase"]),
    ("cloudfront_403_forbidden", "security_blocking", ["geo_restriction", "waf_block"], "CloudFront blocks request due to Geo or WAF rules.", ["waf_log_analysis", "geo_whitelist"]),
    ("alb_504_gateway_timeout", "performance_degradation", ["backend_latency", "idle_timeout"], "Load balancer times out waiting for target response.", ["increase_idle_timeout", "optimize_backend"]),
    ("nlb_tls_handshake_failure", "connectivity_failure", ["cipher_suite_mismatch", "certificate_invalid"], "Client cannot negotiate TLS with NLB.", ["security_policy_update", "acm_validation"]),
    ("vpn_tunnel_instability", "connectivity_failure", ["ike_negotiation", "dpd_timeout"], "VPN connection drops frequently.", ["customer_gateway_logs", "keepalive_ping"]),
    ("direct_connect_bgp_flap", "connectivity_failure", ["route_limit_exceeded", "device_configuration"], "BGP session fluctuates causing packet loss.", ["bgp_timeout_tuning", "jumbo_frames_check"]),

    # --- SECURITY (IAM, KMS, WAF, Secrets) ---
    ("kms_key_pending_deletion", "data_access_failure", ["accidental_deletion", "missing_cancellation"], "Encrypted data is inaccessible because key is scheduled for deletion.", ["cancel_key_deletion", "multi_region_key"]),
    ("kms_throttling_exception", "throttling", ["high_request_rate", "generate_data_key"], "Exceeding KMS API request quota (e.g., 5500 RPS).", ["data_key_caching", "quota_increase"]),
    ("secrets_manager_rotation_failure", "security_risk", ["lambda_network_access", "db_credential_mismatch"], "Rotation Lambda cannot reach database or update secret.", ["rotation_lambda_debug", "vpc_endpoint_check"]),
    ("cognito_token_expiration", "authentication_failure", ["short_ttl", "refresh_token_missing"], "Users logged out unexpectedly due to token expiry.", ["token_validity_extension", "refresh_token_flow"]),
    ("waf_ip_set_limit", "configuration_limit", ["too_many_ips", "quota_exceeded"], "Cannot add more IPs to WAF blocklist.", ["managed_rule_group", "ip_set_sharding"]),
    ("guardduty_finding_noise", "operational_fatigue", ["false_positives", "scanner_activity"], "Alert fatigue from low-severity findings.", ["suppression_rule", "finding_filter"]),
    ("inspector_agent_status_unknown", "compliance_failure", ["ssm_agent_issue", "network_blocked"], "EC2 instances not reporting scan results.", ["ssm_agent_troubleshoot", "endpoint_verification"]),

    # --- CONTAINERS (ECS, EKS, Fargate, ECR) ---
    ("ecs_task_health_check_fail", "availability_failure", ["container_health_check", "grace_period"], "Tasks are killed immediately after starting.", ["health_check_grace_period", "container_logs_debug"]),
    ("ecs_capacity_provider_error", "scaling_failure", ["asg_cooldown", "step_scaling"], "Cluster fails to scale out instances for tasks.", ["capacity_provider_strategy", "target_tracking_policy"]),
    ("eks_node_group_upgrade_failure", "deployment_failure", ["pod_eviction_timeout", "pdb_blocking"], "Upgrade stalls because pods cannot be evicted.", ["pdb_budget_review", "force_eviction_flag"]),
    ("ecr_lifecycle_policy_deletion", "data_loss", ["untagged_image_expire", "aggressive_rule"], "Important images deleted by lifecycle policy.", ["policy_preview", "immutable_tags"]),
    ("fargate_storage_limit", "resource_exhaustion", ["ephemeral_storage", "log_file_accumulation"], "Task fails resulting in 'No space left on device'.", ["mount_efs", "log_driver_configuration"]),

    # --- INTEGRATION (SQS, SNS, Step Functions, EventBridge) ---
    ("sns_delivery_failure", "notification_loss", ["topic_policy_deny", "subscription_filter"], "Messages not reaching subscribers.", ["delivery_status_logging", "dead_letter_queue"]),
    ("sqs_message_size_exceeded", "application_error", ["large_payload", "256kb_limit"], "Producer fails to send message > 256KB.", ["s3_claim_check_pattern", "payload_compression"]),
    ("eventbridge_rule_disabled", "operational_failure", ["manual_state_change", "account_disable"], "Scheduled events stop triggering.", ["cloudtrail_audit", "rule_state_monitor"]),
    ("eventbridge_cross_account_failure", "permission_denied", ["resource_policy_mismatch", "missing_bus_permission"], "Events not flowing between accounts.", ["bus_policy_update", "rule_target_role"]),
    ("mq_broker_memory_full", "resource_exhaustion", ["heap_memory", "unconsumed_messages"], "ActiveMQ/RabbitMQ broker blocks producers.", ["instance_resize", "consumer_scaling"]),

    # --- ANALYTICS (Glue, Athena, Redshift, Kinesis) ---
    ("glue_crawler_schema_mismatch", "data_quality_error", ["partition_conflict", "type_change"], "Crawler creates conflicting tables.", ["exclude_pattern", "schema_evolution_option"]),
    ("athena_partition_limit", "performance_degradation", ["too_many_partitions", "hive_metastore_limit"], "Query fails or runs slowly due to partition overhead.", ["partition_projection", "schema_optimization"]),
    ("kinesis_iterator_expired", "data_loss", ["slow_processing", "retention_period"], "Consumer falls behind retention window (24h default).", ["increase_retention", "parallel_processing"]),
    ("msk_broker_disk_full", "availability_failure", ["log_retention", "high_throughput"], "Kafka broker stops accepting writes.", ["storage_autoscaling", "retention_policy_update"]),
    ("quicksight_spice_capacity", "performance_degradation", ["dataset_refresh_fail", "gb_limit"], "Dashboard data not updating.", ["spice_capacity_purchase", "incremental_refresh"]),

    # --- COST & GOVERNANCE (Billing, Organizations, Config) ---
    ("billing_alarm_delayed", "cost_anomaly", ["metric_latency", "estimated_charges"], "Cost alert received 24h late.", ["cost_anomaly_detection", "daily_report"]),
    ("organizations_scp_denial", "permission_denied", ["root_policy", "implicit_deny"], "Account admin cannot perform action due to SCP.", ["scp_audit", "policy_simulation"]),
    ("config_recorder_delivery_fail", "compliance_failure", ["s3_permission", "sns_topic_error"], "Configuration changes not being recorded.", ["role_policy_fix", "delivery_channel_check"]),
    ("budget_action_failure", "governance_failure", ["iam_role_permission", "ssm_document_error"], "Budget action failed to stop instances.", ["service_role_check", "ssm_automation_test"]),

    # --- MIGRATION & TRANSFER (DMS, Datasync, MGN) ---
    ("dms_replication_task_error", "migration_failure", ["cdc_gap", "source_latency"], "Database migration task fails.", ["task_log_debug", "premigration_assessment"]),
    ("datasync_agent_connectivity", "migration_failure", ["firewall_port", "activation_key"], "Agent cannot connect to AWS.", ["network_check", "agent_restart"]),
    ("mgn_replication_lag", "migration_delay", ["bandwidth_limit", "disk_io"], "Server replication stuck.", ["subnet_bandwidth", "ebs_optimization"]),
    
    # --- IOT & ROBOTICS ---
    ("iot_certificate_inactive", "device_connectivity", ["status_inactive", "policy_not_attached"], "Device cannot connect to MQTT broker.", ["certificate_activation", "policy_attachment"]),
    ("iot_rule_sql_error", "data_routing_error", ["syntax_error", "attribute_missing"], "IoT Rule engine fails to route message.", ["sql_version_check", "error_action_log"]),
    ("greengrass_deployment_fail", "edge_computing_error", ["component_dependency", "lambda_version"], "Deployment to core device fails.", ["deployment_logs", "component_version_check"]),

    # --- ADVANCED GENERATED PATTERNS (Filling to 100+) ---
]

# Generate more programmatically to cover edge cases
services = ["s3", "ec2", "rds", "dynamodb", "lambda", "ecs", "eks", "sqs", "sns", "kinesis"]
error_types = ["timeout", "access_denied", "not_found", "throttling", "validation_error", "internal_error", "quota_exceeded"]

for svc in services:
    for err in error_types:
        name = f"{svc}_{err}_edge_case"
        if not any(p[0] == name for p in patterns):
            patterns.append((
                name,
                "api_failure",
                [f"{svc}_api_limit", f"{err}_response"],
                f"Generated Edge Case: {svc.upper()} API returns {err.upper()} due to high load or misconfiguration.",
                ["retry_with_backoff", "service_quota_check"]
            ))

# Adding specific diverse patterns to reach ~200
more_scenarios = [
   ("codepipeline_source_auth_error", "cicd_failure", ["github_token_expiry", "webhook_failure"], "Pipeline trigger fails.", ["token_rotation", "polling_mode"]),
   ("codebuild_timeout", "cicd_failure", ["long_build", "default_timeout"], "Build phase exceeds 60 mins.", ["timeout_increase", "build_optimization"]),
   ("codedeploy_agent_not_found", "deployment_failure", ["service_not_running", "outdated_agent"], "Deployment hangs waiting for agent.", ["agent_restart", "user_data_install"]),
   ("cloudformation_stack_drift", "drift_detected", ["manual_change", "resource_deleted"], "Stack resources modified outside CloudFormation.", ["stack_update", "drift_detection"]),
   ("cloudformation_circular_dependency", "deployment_failure", ["resource_ref_loop", "output_import"], "Stack update fails due to cycle.", ["refactoring", "parameter_store"]),
   ("service_catalog_product_error", "provisioning_failure", ["launch_constraint", "role_missing"], "User cannot launch product.", ["portfolio_access", "constraint_review"]),
   ("glacier_retrieval_delay", "data_access_delay", ["standard_retrieval", "expedited_unavailable"], "Restore job takes longer than expected.", ["expedited_tier", "provisioned_capacity"]),
   ("transfer_family_ssh_key_error", "auth_failure", ["key_format", "user_permission"], "SFTP user cannot login.", ["key_validation", "logging_role"]),
   ("global_accelerator_endpoint_unhealthy", "routing_failure", ["health_check_fail", "region_down"], "Traffic not routed to endpoint.", ["health_check_tuning", "endpoint_group_update"]),
   ("backup_vault_access_denied", "compliance_failure", ["vault_policy", "cross_account_copy"], "Cannot copy recovery point.", ["vault_access_policy", "kms_grant"]),
   ("emr_step_failure", "analytics_failure", ["memory_limit", "script_error"], "Cluster step execution fails.", ["log_analysis", "cluster_resize"]),
   ("emr_bootstrap_action_error", "provisioning_failure", ["s3_script_missing", "permission_denied"], "Cluster fails to launch.", ["s3_path_check", "log_uri_check"]),
   ("elastic_beanstalk_red_health", "app_failure", ["nginx_500", "deployment_hook"], "Environment status turns severe.", ["log_snapshot", "rollback_version"]),
   ("app_runner_build_error", "deployment_failure", ["runtime_version", "build_command"], "Service creation fails.", ["log_stream_check", "config_update"]),
   ("lightsail_quota_exceeded", "limit_failure", ["instance_count", "static_ip"], "Cannot create resource.", ["quota_limit_check", "region_check"]),
   ("macie_classification_error", "security_check_fail", ["job_error", "access_denied"], "Sensitive data scan fails.", ["permission_fix", "job_scope_check"]),
   ("textract_document_size_error", "ai_service_error", ["file_too_large", "pixel_limit"], "Document analysis failure.", ["synchronous_to_async", "image_resize"]),
   ("rekognition_throttling", "ai_service_throttling", ["tps_limit", "concurrent_calls"], "Image processing requests rejected.", ["backoff_strategy", "limit_increase"]),
   ("polly_text_length_exceeded", "ai_service_error", ["character_limit", "ssml_error"], "Speech synthesis fails.", ["split_text", "long_audio_synthesis"]),
   ("transcribe_job_timeout", "ai_service_error", ["large_audio_file", "unknown_format"], "Transcription job stalls.", ["media_conversion", "chunking"]),
   ("sagemaker_endpoint_latency", "ai_performance", ["instance_overload", "model_complexity"], "Inference response time high.", ["autoscaling_policy", "instance_type_upgrade"]),
   ("sagemaker_notebook_kernel_crash", "ai_development", ["oom_kill", "library_conflict"], "Jupyter kernel restarts.", ["instance_resize", "lifecycle_config"]),
   ("kendra_index_failed", "search_failure", ["storage_limit", "access_role"], "Document indexing stops.", ["capacity_edition_upgrade", "role_policy_check"]),
   ("personalize_campaign_failure", "ml_ops_error", ["data_quality", "training_error"], "Recommendation campaign error.", ["dataset_inspection", "recipe_change"]),
]

patterns.extend(more_scenarios)

# Ensure directory exists
output_dir = "patterns"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

count = 0
for p in patterns:
    name, failure_class, conditions, description, mitigations = p
    filename = f"{output_dir}/{name}.yaml"
    
    # Skip if exists to avoid overwriting edits
    if os.path.exists(filename):
        continue
        
    content = {
        "pattern": name,
        "failure_class": failure_class,
        "conditions": conditions,
        "description": description,
        "mitigations": mitigations
    }
    
    with open(filename, "w") as f:
        yaml.dump(content, f, sort_keys=False)
    count += 1

print(f"Generated {count} new failure patterns.")
