import os
import hcl2
from typing import Dict, Any, List, Set
from agents.graph_engine import ArchitectureGraph

# Hard-coded keyword mappings from Terraform resource types to our standardized service types
TF_TYPE_MAPPING = {
    # ========== COMPUTE ==========
    "aws_lambda_function": "lambda",
    "aws_lambda_layer_version": "lambda",
    "aws_lambda_alias": "lambda",
    "aws_instance": "ec2",
    "aws_spot_instance_request": "ec2",
    "aws_ecs_service": "ecs",
    "aws_ecs_task_definition": "ecs",
    "aws_ecs_cluster": "ecs",
    "aws_ecs_capacity_provider": "ecs",
    "aws_eks_cluster": "eks",
    "aws_eks_node_group": "eks",
    "aws_eks_fargate_profile": "eks",
    "aws_autoscaling_group": "asg",
    "aws_launch_template": "ec2",
    "aws_launch_configuration": "ec2",
    "aws_batch_job_definition": "batch",
    "aws_batch_compute_environment": "batch",
    "aws_lightsail_instance": "lightsail",
    "aws_elastic_beanstalk_application": "beanstalk",
    "aws_elastic_beanstalk_environment": "beanstalk",
    
    # ========== STORAGE ==========
    "aws_s3_bucket": "s3",
    "aws_s3_bucket_object": "s3",
    "aws_s3_bucket_notification": "s3",
    "aws_s3_bucket_policy": "s3",
    "aws_s3_access_point": "s3",
    "aws_efs_file_system": "efs",
    "aws_efs_mount_target": "efs",
    "aws_efs_access_point": "efs",
    "aws_ebs_volume": "ebs",
    "aws_ebs_snapshot": "ebs",
    "aws_fsx_lustre_file_system": "fsx",
    "aws_fsx_windows_file_system": "fsx",
    "aws_fsx_ontap_file_system": "fsx",
    "aws_fsx_openzfs_file_system": "fsx",
    "aws_backup_vault": "backup",
    "aws_backup_plan": "backup",
    "aws_glacier_vault": "glacier",
    "aws_storagegateway_gateway": "storage_gateway",
    
    # ========== DATABASE ==========
    "aws_dynamodb_table": "dynamodb",
    "aws_dynamodb_global_table": "dynamodb",
    "aws_db_instance": "rds",
    "aws_rds_cluster": "rds",
    "aws_rds_cluster_instance": "rds",
    "aws_db_proxy": "rds",
    "aws_rds_global_cluster": "rds",
    "aws_elasticache_cluster": "elasticache",
    "aws_elasticache_replication_group": "elasticache",
    "aws_elasticache_parameter_group": "elasticache",
    "aws_neptune_cluster": "neptune",
    "aws_neptune_cluster_instance": "neptune",
    "aws_docdb_cluster": "docdb",
    "aws_docdb_cluster_instance": "docdb",
    "aws_redshift_cluster": "redshift",
    "aws_redshift_subnet_group": "redshift",
    "aws_dax_cluster": "dax",
    "aws_memorydb_cluster": "memorydb",
    "aws_timestream_database": "timestream",
    "aws_qldb_ledger": "qldb",
    
    # ========== INTEGRATION & MESSAGING ==========
    "aws_sqs_queue": "sqs",
    "aws_sns_topic": "sns",
    "aws_sns_topic_subscription": "sns",
    "aws_kinesis_stream": "kinesis",
    "aws_kinesis_firehose_delivery_stream": "firehose",
    "aws_kinesis_analytics_application": "kinesis_analytics",
    "aws_kinesis_video_stream": "kinesis_video",
    "aws_sfn_state_machine": "step_functions",
    "aws_mq_broker": "mq",
    "aws_msk_cluster": "msk",
    "aws_msk_configuration": "msk",
    "aws_eventbridge_rule": "eventbridge",
    "aws_eventbridge_event_bus": "eventbridge",
    "aws_appflow_flow": "appflow",
    "aws_appsync_graphql_api": "appsync",
    
    # ========== NETWORKING & CONTENT DELIVERY ==========
    "aws_api_gateway_rest_api": "api_gateway",
    "aws_api_gateway_stage": "api_gateway",
    "aws_apigatewayv2_api": "api_gateway_v2",
    "aws_apigatewayv2_stage": "api_gateway_v2",
    "aws_cloudfront_distribution": "cloudfront",
    "aws_cloudfront_origin_access_identity": "cloudfront",
    "aws_lb": "alb",
    "aws_alb": "alb",
    "aws_elb": "elb",
    "aws_lb_target_group": "alb",
    "aws_lb_listener": "alb",
    "aws_route53_zone": "route53",
    "aws_route53_record": "route53",
    "aws_route53_health_check": "route53",
    "aws_vpc": "vpc",
    "aws_subnet": "subnet",
    "aws_nat_gateway": "nat",
    "aws_internet_gateway": "igw",
    "aws_vpn_gateway": "vpn",
    "aws_vpn_connection": "vpn",
    "aws_customer_gateway": "vpn",
    "aws_vpc_peering_connection": "vpc_peering",
    "aws_transit_gateway": "transit_gateway",
    "aws_dx_connection": "direct_connect",
    "aws_globalaccelerator_accelerator": "global_accelerator",
    "aws_route_table": "route_table",
    "aws_network_interface": "eni",
    "aws_eip": "eip",
    
    # ========== SECURITY & IDENTITY ==========
    "aws_security_group": "sg",
    "aws_security_group_rule": "sg",
    "aws_network_acl": "nacl",
    "aws_waf_web_acl": "waf",
    "aws_wafv2_web_acl": "waf",
    "aws_wafv2_rule_group": "waf",
    "aws_shield_protection": "shield",
    "aws_guardduty_detector": "guardduty",
    "aws_macie2_classification_job": "macie",
    "aws_inspector_assessment_template": "inspector",
    "aws_securityhub_account": "security_hub",
    "aws_iam_role": "iam_role",
    "aws_iam_policy": "iam_policy",
    "aws_iam_role_policy": "iam_policy",
    "aws_iam_user": "iam_user",
    "aws_iam_group": "iam_group",
    "aws_iam_access_key": "iam_access_key",
    "aws_kms_key": "kms",
    "aws_kms_alias": "kms",
    "aws_secretsmanager_secret": "secrets_manager",
    "aws_secretsmanager_secret_version": "secrets_manager",
    "aws_acm_certificate": "acm",
    "aws_cognito_user_pool": "cognito",
    "aws_cognito_identity_pool": "cognito",
    
    # ========== MONITORING & LOGGING ==========
    "aws_cloudwatch_log_group": "cloudwatch",
    "aws_cloudwatch_log_stream": "cloudwatch",
    "aws_cloudwatch_metric_alarm": "cloudwatch",
    "aws_cloudwatch_dashboard": "cloudwatch",
    "aws_cloudwatch_event_rule": "cloudwatch_events",
    "aws_cloudtrail": "cloudtrail",
    "aws_config_configuration_recorder": "config",
    "aws_config_config_rule": "config",
    "aws_xray_sampling_rule": "xray",
    
    # ========== CONTAINER & ORCHESTRATION ==========
    "aws_ecr_repository": "ecr",
    "aws_ecr_repository_policy": "ecr",
    "aws_ecr_lifecycle_policy": "ecr",
    
    # ========== ANALYTICS & BIG DATA ==========
    "aws_athena_database": "athena",
    "aws_athena_workgroup": "athena",
    "aws_glue_catalog_database": "glue",
    "aws_glue_crawler": "glue",
    "aws_glue_job": "glue",
    "aws_emr_cluster": "emr",
    "aws_emr_instance_group": "emr",
    "aws_elasticsearch_domain": "elasticsearch",
    "aws_opensearch_domain": "opensearch",
    "aws_quicksight_data_source": "quicksight",
    "aws_lake_formation_resource": "lake_formation",
    "aws_mwaa_environment": "mwaa",
    
    # ========== MACHINE LEARNING & AI ==========
    "aws_sagemaker_notebook_instance": "sagemaker",
    "aws_sagemaker_model": "sagemaker",
    "aws_sagemaker_endpoint": "sagemaker",
    "aws_sagemaker_endpoint_configuration": "sagemaker",
    "aws_rekognition_collection": "rekognition",
    "aws_comprehend_document_classifier": "comprehend",
    "aws_lex_bot": "lex",
    "aws_transcribe_vocabulary": "transcribe",
    
    # ========== DEVELOPER TOOLS ==========
    "aws_codecommit_repository": "codecommit",
    "aws_codebuild_project": "codebuild",
    "aws_codedeploy_app": "codedeploy",
    "aws_codedeploy_deployment_group": "codedeploy",
    "aws_codepipeline": "codepipeline",
    "aws_codeartifact_repository": "codeartifact",
    
    # ========== MANAGEMENT & GOVERNANCE ==========
    "aws_organizations_organization": "organizations",
    "aws_organizations_account": "organizations",
    "aws_cloudformation_stack": "cloudformation",
    "aws_cloudformation_stack_set": "cloudformation",
    "aws_ssm_parameter": "ssm",
    "aws_ssm_document": "ssm",
    "aws_ssm_maintenance_window": "ssm",
    "aws_service_catalog_portfolio": "service_catalog",
    "aws_opsworks_stack": "opsworks",
    
    # ========== APPLICATION INTEGRATION ==========
    "aws_ses_domain_identity": "ses",
    "aws_ses_email_identity": "ses",
    "aws_pinpoint_app": "pinpoint",
    "aws_workspaces_workspace": "workspaces",
    "aws_appstream_fleet": "appstream",
    
    # ========== IOT ==========
    "aws_iot_thing": "iot",
    "aws_iot_policy": "iot",
    "aws_iot_certificate": "iot",
    "aws_iot_topic_rule": "iot",
    "aws_iotanalytics_channel": "iot_analytics",
    "aws_greengrass_group": "greengrass",
    
    # ========== BLOCKCHAIN ==========
    "aws_managedblockchain_network": "blockchain",
    "aws_managedblockchain_node": "blockchain",
    
    # ========== MEDIA SERVICES ==========
    "aws_media_store_container": "media_store",
    "aws_media_convert_queue": "media_convert",
    "aws_media_live_channel": "media_live",
    
    # ========== MIGRATION & TRANSFER ==========
    "aws_dms_replication_instance": "dms",
    "aws_dms_endpoint": "dms",
    "aws_datasync_location_s3": "datasync",
    "aws_transfer_server": "transfer",
    
    # ========== EVENT SOURCES ==========
    "aws_lambda_event_source_mapping": "event_source_mapping",
}








class TerraformParser:
    def __init__(self, streaming_mode=False, max_workers=32):
        self.graph = ArchitectureGraph()
        self.variables = {}  # Symbol table for var.x
        self.locals = {}  # Symbol table for local.x
        self.all_resources = {}  # Global resource registry
        self.modules = {}  # Module definitions
        self.parsed_modules = set()  # Track parsed module paths to avoid cycles
        self.plan_mode = False  # Track if parsing a plan file
        self.resource_changes = {}  # Track resource changes from plan
        self.remote_module_cache = {}  # Cache for remote modules
        self.module_registry_cache_dir = os.path.expanduser("~/.terraform-parser-cache")
        
        # Performance optimizations
        self._value_resolution_cache = {}  # Cache for resolved values
        self._property_resolution_cache = {}  # Cache for resolved properties
        self._redundancy_cache = {}  # Cache for redundancy calculations
        
        # Massive codebase optimizations
        self.streaming_mode = streaming_mode  # Process resources incrementally
        self.max_workers = max_workers  # Max parallel workers
        self._batch_size = 100  # Process resources in batches
        self._enable_gc = True  # Enable aggressive garbage collection
        self._lazy_edge_building = True  # Build edges lazily
        self._resource_count = 0  # Track total resources
        
        # Memory management
        self._memory_efficient_mode = False  # Auto-enabled for >2000 resources
        self._edge_cache = {}  # Cache for edge relationships
        
        # Create cache directory
        os.makedirs(self.module_registry_cache_dir, exist_ok=True)
        


    def _fetch_remote_module(self, source: str, version: str = None) -> str:
        """Fetch remote module and return local path."""
        import hashlib
        import subprocess
        
        # Create cache key
        cache_key = hashlib.md5(f"{source}:{version}".encode()).hexdigest()
        cache_path = os.path.join(self.module_registry_cache_dir, cache_key)
        
        # Check cache
        if os.path.exists(cache_path):
            return cache_path
        
        try:
            # Terraform Registry modules (e.g., "terraform-aws-modules/vpc/aws")
            if "/" in source and not source.startswith(("./", "../", "git::", "http")):
                print(f"[INFO] Fetching Terraform Registry module: {source}")
                # Use terraform init to download
                temp_dir = os.path.join(self.module_registry_cache_dir, f"temp_{cache_key}")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Create minimal terraform config
                with open(os.path.join(temp_dir, "main.tf"), "w") as f:
                    version_str = f'version = "{version}"' if version else ""
                    f.write(f'''
module "temp" {{
  source  = "{source}"
  {version_str}
}}
''')
                
                # Run terraform init
                result = subprocess.run(
                    ["terraform", "init", "-backend=false"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # Find downloaded module
                    modules_dir = os.path.join(temp_dir, ".terraform", "modules")
                    if os.path.exists(modules_dir):
                        # Copy to cache
                        import shutil
                        for item in os.listdir(modules_dir):
                            src = os.path.join(modules_dir, item)
                            if os.path.isdir(src):
                                shutil.copytree(src, cache_path, dirs_exist_ok=True)
                                return cache_path
                
                print(f"[WARNING] Failed to fetch module {source}: {result.stderr}")
                return None
            
            # Git modules (e.g., "git::https://github.com/...")
            elif source.startswith("git::"):
                print(f"[INFO] Fetching Git module: {source}")
                git_url = source.replace("git::", "")
                
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", git_url, cache_path],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    return cache_path
                
                print(f"[WARNING] Failed to clone Git module: {result.stderr}")
                return None
            
            # HTTP modules
            elif source.startswith(("http://", "https://")):
                print(f"[INFO] Fetching HTTP module: {source}")
                import urllib.request
                import tarfile
                import zipfile
                
                # Download to temp file
                temp_file = os.path.join(self.module_registry_cache_dir, f"download_{cache_key}")
                urllib.request.urlretrieve(source, temp_file)
                
                # Extract based on extension
                if source.endswith(".tar.gz") or source.endswith(".tgz"):
                    with tarfile.open(temp_file, "r:gz") as tar:
                        tar.extractall(cache_path)
                elif source.endswith(".zip"):
                    with zipfile.ZipFile(temp_file, "r") as zip_ref:
                        zip_ref.extractall(cache_path)
                
                os.remove(temp_file)
                return cache_path
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch remote module {source}: {e}")
            return None
        
        return None
    
    def parse_plan_file(self, plan_path: str) -> ArchitectureGraph:

        """Parse a Terraform plan JSON file.
        
        Terraform plan files are generated with:
        terraform plan -out=tfplan
        terraform show -json tfplan > tfplan.json
        """
        import json
        
        try:
            with open(plan_path, 'r') as f:
                plan_data = json.load(f)
            
            self.plan_mode = True
            
            # Extract planned values (what will exist after apply)
            if "planned_values" in plan_data and "root_module" in plan_data["planned_values"]:
                root = plan_data["planned_values"]["root_module"]
                self._extract_plan_resources(root)
            
            # Extract resource changes (create/update/delete)
            if "resource_changes" in plan_data:
                for change in plan_data["resource_changes"]:
                    address = change.get("address", "")
                    actions = change.get("change", {}).get("actions", [])
                    after = change.get("change", {}).get("after", {})
                    
                    # Store change metadata
                    self.resource_changes[address] = {
                        "actions": actions,
                        "config": after
                    }
                    
                    # Only analyze resources that will exist after apply
                    if "delete" not in actions and after:
                        # Parse resource type and name from address
                        # Format: aws_lambda_function.my_function
                        parts = address.split(".")
                        if len(parts) >= 2:
                            tf_type = parts[0]
                            tf_name = ".".join(parts[1:])
                            
                            if tf_type not in self.all_resources:
                                self.all_resources[tf_type] = {}
                            self.all_resources[tf_type][tf_name] = after
            
            # Build graph from collected resources
            self._build_graph()
            return self.graph
            
        except Exception as e:
            print(f"Error parsing plan file {plan_path}: {e}")
            return self.graph
    
    def _extract_plan_resources(self, module_data: Dict):
        """Recursively extract resources from plan module data."""
        # Extract resources from this module
        if "resources" in module_data:
            for resource in module_data["resources"]:
                tf_type = resource.get("type", "")
                name = resource.get("name", "")
                values = resource.get("values", {})
                
                if tf_type not in self.all_resources:
                    self.all_resources[tf_type] = {}
                self.all_resources[tf_type][name] = values
        
        # Recursively process child modules
        if "child_modules" in module_data:
            for child in module_data["child_modules"]:
                self._extract_plan_resources(child)

    def parse_state_file(self, state_path: str) -> ArchitectureGraph:
        """Parse a Terraform state file to detect drift and orphaned resources.
        
        State files contain the actual deployed infrastructure.
        """
        import json
        
        try:
            with open(state_path, 'r') as f:
                state_data = json.load(f)
            
            # Extract resources from state
            state_resources = {}
            if "resources" in state_data:
                for resource in state_data["resources"]:
                    tf_type = resource.get("type", "")
                    name = resource.get("name", "")
                    instances = resource.get("instances", [])
                    
                    if instances:
                        # Use first instance's attributes
                        attrs = instances[0].get("attributes", {})
                        
                        if tf_type not in state_resources:
                            state_resources[tf_type] = {}
                        state_resources[tf_type][name] = attrs
            
            # Store state resources
            self.all_resources = state_resources
            
            # Build graph
            self._build_graph()
            return self.graph
            
        except Exception as e:
            print(f"Error parsing state file {state_path}: {e}")
            return self.graph
    
    def compare_state_to_code(self, state_path: str, code_dir: str) -> Dict[str, List[str]]:
        """Compare state file to code to detect drift.
        
        Returns:
            {
                "orphaned": ["resource.name"],  # In state but not in code
                "missing": ["resource.name"],   # In code but not in state
                "drift_detected": True/False
            }
        """
        import json
        
        drift_report = {
            "orphaned": [],
            "missing": [],
            "drift_detected": False
        }
        
        try:
            # Parse state
            with open(state_path, 'r') as f:
                state_data = json.load(f)
            
            state_resources = set()
            if "resources" in state_data:
                for resource in state_data["resources"]:
                    tf_type = resource.get("type", "")
                    name = resource.get("name", "")
                    state_resources.add(f"{tf_type}.{name}")
            
            # Parse code
            code_parser = TerraformParser()
            code_parser.parse_directory(code_dir)
            
            code_resources = set()
            for tf_type, resources in code_parser.all_resources.items():
                for name in resources.keys():
                    code_resources.add(f"{tf_type}.{name}")
            
            # Find drift
            drift_report["orphaned"] = list(state_resources - code_resources)
            drift_report["missing"] = list(code_resources - state_resources)
            drift_report["drift_detected"] = len(drift_report["orphaned"]) > 0 or len(drift_report["missing"]) > 0
            
        except Exception as e:
            print(f"Error comparing state to code: {e}")
        
        return drift_report

        
    def parse_directory(self, dir_path: str) -> ArchitectureGraph:
        """Parses all .tf files in a directory."""
        if not os.path.isdir(dir_path):
            return self.graph
        
        # Collect all .tf files first
        tf_files = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".tf"):
                    tf_files.append(os.path.join(root, file))
        
        # Parallel file loading for large codebases
        if len(tf_files) > 10:
            print(f"[PERFORMANCE] Parsing {len(tf_files)} files in parallel...")
            self._load_files_parallel(tf_files, dir_path)
        else:
            # Sequential for small codebases (less overhead)
            for file_path in tf_files:
                self._load_file(file_path, base_dir=dir_path)

        # Second Pass: Process modules
        self._process_modules(dir_path)

        # Third Pass: Build Graph from collected resources
        self._build_graph()
        return self.graph
    
    def _load_files_parallel(self, file_paths: List[str], base_dir: str):
        """Load multiple files in parallel using multiprocessing."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        # Thread-safe lock for shared data structures
        lock = threading.Lock()
        
        def load_file_safe(file_path):
            """Thread-safe file loading."""
            try:
                with open(file_path, 'r') as f:
                    parsed = hcl2.load(f)
                
                # Collect data locally first
                local_vars = {}
                local_locals = {}
                local_modules = {}
                local_resources = {}
                
                # Extract variables
                if "variable" in parsed:
                    for var_block in parsed["variable"]:
                        for var_name, var_config in var_block.items():
                            if "default" in var_config:
                                local_vars[f"var.{var_name}"] = var_config["default"]
                
                # Extract locals
                if "locals" in parsed:
                    for locals_block in parsed["locals"]:
                        for local_name, local_value in locals_block.items():
                            local_locals[f"local.{local_name}"] = local_value
                
                # Extract modules
                if "module" in parsed:
                    for module_block in parsed["module"]:
                        for module_name, module_config in module_block.items():
                            local_modules[module_name] = {
                                "source": module_config.get("source", ""),
                                "config": module_config,
                                "base_dir": base_dir or os.path.dirname(file_path)
                            }
                
                # Collect resources
                if "resource" in parsed:
                    for resource_block in parsed["resource"]:
                        for tf_type, resources_of_type in resource_block.items():
                            if tf_type not in local_resources:
                                local_resources[tf_type] = {}
                            for tf_name, props in resources_of_type.items():
                                local_resources[tf_type][tf_name] = props
                
                # Merge into shared data structures (thread-safe)
                with lock:
                    self.variables.update(local_vars)
                    self.locals.update(local_locals)
                    self.modules.update(local_modules)
                    
                    for tf_type, resources in local_resources.items():
                        if tf_type not in self.all_resources:
                            self.all_resources[tf_type] = {}
                        self.all_resources[tf_type].update(resources)
                
                return True
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
                return False
        
        # Use ThreadPoolExecutor for I/O-bound operations
        max_workers = min(32, len(file_paths))  # Limit to 32 threads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(load_file_safe, fp): fp for fp in file_paths}
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 50 == 0:
                    print(f"[PROGRESS] Parsed {completed}/{len(file_paths)} files...")


    def _load_file(self, file_path: str, base_dir: str = None):
        """Load variables, locals, modules, and resources from a single file."""
        try:
            with open(file_path, 'r') as f:
                parsed = hcl2.load(f)
            
            # Extract variables
            if "variable" in parsed:
                for var_block in parsed["variable"]:
                    for var_name, var_config in var_block.items():
                        if "default" in var_config:
                            self.variables[f"var.{var_name}"] = var_config["default"]
            
            # Extract locals
            if "locals" in parsed:
                for locals_block in parsed["locals"]:
                    for local_name, local_value in locals_block.items():
                        self.locals[f"local.{local_name}"] = local_value
            
            # Extract modules
            if "module" in parsed:
                for module_block in parsed["module"]:
                    for module_name, module_config in module_block.items():
                        self.modules[module_name] = {
                            "source": module_config.get("source", ""),
                            "config": module_config,
                            "base_dir": base_dir or os.path.dirname(file_path)
                        }
            
            # Collect all resources
            if "resource" in parsed:
                for resource_block in parsed["resource"]:
                    for tf_type, resources_of_type in resource_block.items():
                        if tf_type not in self.all_resources:
                            self.all_resources[tf_type] = {}
                        for tf_name, props in resources_of_type.items():
                            self.all_resources[tf_type][tf_name] = props
                            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _process_modules(self, base_dir: str):
        """Recursively process all module definitions."""
        for module_name, module_info in self.modules.items():
            source = module_info["source"]
            module_base = module_info["base_dir"]
            module_config = module_info.get("config", {})
            version = module_config.get("version")
            
            module_path = None
            
            # Handle local modules
            if source.startswith("./") or source.startswith("../"):
                module_path = os.path.normpath(os.path.join(module_base, source))
            
            # Handle remote modules (Registry, Git, HTTP)
            else:
                print(f"[INFO] Processing remote module: {module_name} from {source}")
                module_path = self._fetch_remote_module(source, version)
                
                if not module_path:
                    print(f"[WARNING] Skipping module {module_name}: failed to fetch from {source}")
                    continue
            
            # Avoid infinite recursion
            if module_path in self.parsed_modules:
                continue
            
            self.parsed_modules.add(module_path)
            
            # Parse module directory
            if os.path.isdir(module_path):
                # Create a temporary parser for the module
                # Inherit parent variables but keep resources separate
                for root, _, files in os.walk(module_path):
                    for file in files:
                        if file.endswith(".tf"):
                            self._load_file(os.path.join(root, file), base_dir=module_path)


    def parse_file(self, file_path: str) -> ArchitectureGraph:
        """Parses a single .tf file."""
        self._load_file(file_path)
        self._build_graph()
        return self.graph

    def _build_graph(self):
        """Build the graph from collected resources."""
        # Map: { "aws_sqs_queue.orders": "sqs_orders" }
        tf_id_map = {}
        
        # Count total resources for progress reporting
        total_resources = sum(len(resources) for resources in self.all_resources.values())
        self._resource_count = total_resources
        
        # Enable memory-efficient mode for massive codebases
        if total_resources > 2000:
            self._memory_efficient_mode = True
            print(f"[MASSIVE CODEBASE] {total_resources} resources detected - enabling optimizations...")
            print(f"[OPTIMIZATION] Memory-efficient mode: ON")
            print(f"[OPTIMIZATION] Batch processing: {self._batch_size} resources/batch")
            print(f"[OPTIMIZATION] Garbage collection: ON")
        elif total_resources > 100:
            print(f"[PERFORMANCE] Building graph from {total_resources} resources...")
        
        processed = 0
        batch_count = 0
        
        # 1. Create all nodes (with batch processing for massive codebases)
        for tf_type, resources_of_type in self.all_resources.items():
            svc_type = TF_TYPE_MAPPING.get(tf_type)
            
            # Skip non-graphable types (but track event_source_mapping for edges)
            if not svc_type or svc_type == "event_source_mapping":
                continue
            
            for tf_name, props in resources_of_type.items():
                node_id = f"{svc_type}_{tf_name.lower()}"
                
                # Resolve variables in properties (with caching)
                if self._memory_efficient_mode:
                    # Minimal property resolution for massive codebases
                    clean_props = self._resolve_properties_minimal(props)
                else:
                    clean_props = self._resolve_properties(props)
                
                # Calculate redundancy level based on configuration (with caching)
                cache_key = f"{tf_type}:{tf_name}"
                if cache_key in self._redundancy_cache:
                    redundancy_level = self._redundancy_cache[cache_key]
                else:
                    redundancy_level = self._calculate_redundancy_level(tf_type, clean_props)
                    self._redundancy_cache[cache_key] = redundancy_level
                
                # Update node properties with redundancy
                clean_props['_redundancy_level'] = redundancy_level
                
                self.graph.add_node(node_id, svc_type, props=clean_props)
                
                # Set redundancy level on the node
                if node_id in self.graph.nodes:
                    self.graph.nodes[node_id].redundancy_level = redundancy_level
                
                # Store mapping for edge resolution
                full_tf_name = f"{tf_type}.{tf_name}"

                tf_id_map[full_tf_name] = node_id
                tf_id_map[f"{full_tf_name}.id"] = node_id
                tf_id_map[f"{full_tf_name}.arn"] = node_id
                tf_id_map[f"{full_tf_name}.name"] = node_id
                tf_id_map[f"{full_tf_name}.address"] = node_id
                
                processed += 1
                if total_resources > 100 and processed % 100 == 0:
                    print(f"[PROGRESS] Created {processed}/{total_resources} nodes...")
                
                # GC for massive codebases
                if self._memory_efficient_mode and processed % self._batch_size == 0:
                    import gc
                    gc.collect()



        # 2. Build edges
        self._build_graph_edges(tf_id_map)

    def _calculate_redundancy_level(self, tf_type: str, props: Dict) -> int:
        """Calculate redundancy level based on resource configuration.
        
        Returns:
            1 = Single instance/AZ (SPOF risk)
            2 = Multi-AZ or multiple instances
            3 = Auto-scaling or highly distributed
        """
        # RDS/Database checks
        if tf_type in ["aws_db_instance", "aws_rds_cluster"]:
            if props.get("multi_az", False):
                return 2
            return 1
        
        # Check for count/for_each (multiple instances)
        if "count" in props:
            count_val = props["count"]
            if isinstance(count_val, int) and count_val > 1:
                return 2
            elif isinstance(count_val, str) and count_val != "0" and count_val != "1":
                return 2  # Assume variable resolves to > 1
        
        if "for_each" in props:
            return 2  # for_each implies multiple instances
        
        # Auto Scaling Group
        if tf_type == "aws_autoscaling_group":
            min_size = props.get("min_size", 1)
            if isinstance(min_size, int) and min_size >= 2:
                return 3
            return 2
        
        # Lambda with reserved concurrency
        if tf_type == "aws_lambda_function":
            reserved_concurrency = props.get("reserved_concurrent_executions")
            if reserved_concurrency and isinstance(reserved_concurrency, int) and reserved_concurrency > 100:
                return 2
        
        # ECS Service with multiple tasks
        if tf_type == "aws_ecs_service":
            desired_count = props.get("desired_count", 1)
            if isinstance(desired_count, int) and desired_count >= 2:
                return 2
        
        # ALB/ELB (inherently multi-AZ)
        if tf_type in ["aws_lb", "aws_alb", "aws_elb"]:
            return 2
        
        
        # Default: single instance
        return 1

    def _build_graph_edges(self, tf_id_map: Dict):
        """Create edges after all nodes are created."""
        # 1. Create edges from event source mappings
        if "aws_lambda_event_source_mapping" in self.all_resources:
            for mapping_name, mapping_props in self.all_resources["aws_lambda_event_source_mapping"].items():
                source_arn = self._extract_reference(mapping_props.get("event_source_arn", ""))
                target_arn = self._extract_reference(mapping_props.get("function_name", ""))
                
                source_id = tf_id_map.get(source_arn)
                target_id = tf_id_map.get(target_arn)
                
                if source_id and target_id:
                    self.graph.add_edge(source_id, target_id, "trigger")

        # 2. Collect all resources for edge scanning
        scan_targets = []
        for tf_type, resources_of_type in self.all_resources.items():
            svc_type = TF_TYPE_MAPPING.get(tf_type)
            if not svc_type or svc_type == "event_source_mapping":
                continue
            for tf_name, props in resources_of_type.items():
                source_id = f"{svc_type}_{tf_name.lower()}"
                scan_targets.append((source_id, props))

        # 3. Parallelize edge scanning for large node counts
        if len(scan_targets) > 500:
            print(f"[PERFORMANCE] Scanning for edges between {len(scan_targets)} resources in parallel...")
            from concurrent.futures import ThreadPoolExecutor
            
            def scan_task(target):
                source_id, props = target
                # Use minimal resolution for edge scanning in memory-efficient mode
                if self._memory_efficient_mode:
                    resolved_props = self._resolve_properties_minimal(props)
                else:
                    resolved_props = self._resolve_properties(props)
                self._scan_for_edges(source_id, resolved_props, tf_id_map)

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                list(executor.map(scan_task, scan_targets))
        else:
            # Sequential scanning
            for source_id, props in scan_targets:
                if self._memory_efficient_mode:
                    resolved_props = self._resolve_properties_minimal(props)
                else:
                    resolved_props = self._resolve_properties(props)
                self._scan_for_edges(source_id, resolved_props, tf_id_map)



    def _extract_reference(self, value: Any) -> str:
        """Extract terraform reference from HCL2 parsed value."""
        if isinstance(value, str):
            # HCL2 returns interpolations as "${aws_sqs_queue.OrdersQueue.arn}"
            # Strip the ${} wrapper
            if value.startswith("${") and value.endswith("}"):
                value = value[2:-1]
            
            # Extract the resource part: aws_sqs_queue.OrdersQueue
            parts = value.split(".")
            if len(parts) >= 2:
                return f"{parts[0]}.{parts[1]}"
        return ""

    def _resolve_properties(self, props: Dict) -> Dict:
        """Resolve variables, locals, and expressions recursively."""
        resolved = {}
        for k, v in props.items():
            if isinstance(v, str):
                resolved[k] = self._resolve_value(v)
            elif isinstance(v, dict):
                resolved[k] = self._resolve_properties(v)
            elif isinstance(v, list):
                resolved[k] = [self._resolve_properties(item) if isinstance(item, dict) else self._resolve_value(item) if isinstance(item, str) else item for item in v]
            else:
                resolved[k] = v
        return resolved

    def _resolve_properties_minimal(self, props: Dict) -> Dict:
        """Memory-efficient property resolution focusing only on critical keys."""
        critical_keys = {
            "source", "target", "arn", "id", "name", "bucket", "table_name", 
            "function_name", "vpc_id", "subnet_id", "security_group_id",
            "count", "for_each", "multi_az", "replication_factor",
            "event_source_arn", "queue_url", "topic_arn", "kms_key_id"
        }
        
        resolved = {}
        for k, v in props.items():
            # Only resolve critical keys or nested structures
            if k in critical_keys or isinstance(v, (dict, list)):
                if isinstance(v, str):
                    resolved[k] = self._resolve_value(v)
                elif isinstance(v, dict):
                    resolved[k] = self._resolve_properties_minimal(v)
                elif isinstance(v, list):
                    resolved[k] = [self._resolve_properties_minimal(item) if isinstance(item, dict) else self._resolve_value(item) if isinstance(item, str) else item for item in v]
                else:
                    resolved[k] = v
            else:
                # Keep un-resolved to save memory/time
                resolved[k] = v
        return resolved

    
    def _resolve_value(self, value: str) -> Any:
        """Resolve a single value (variable, local, or expression)."""
        if not isinstance(value, str):
            return value
        
        # Check cache first (performance optimization)
        if value in self._value_resolution_cache:
            return self._value_resolution_cache[value]
        
        # Strip interpolation wrapper
        clean_value = value
        if value.startswith("${") and value.endswith("}"):
            clean_value = value[2:-1]
        
        # Check for variable reference
        if clean_value.startswith("var."):
            result = self.variables.get(clean_value, value)
            self._value_resolution_cache[value] = result
            return result
        
        # Check for local reference
        if clean_value.startswith("local."):
            result = self.locals.get(clean_value, value)
            self._value_resolution_cache[value] = result
            return result

        
        # Handle lookup() function
        if clean_value.startswith("lookup("):
            # lookup(map, key, default)
            try:
                import re
                match = re.match(r'lookup\((.*?),\s*"(.*?)"(?:,\s*"(.*?)")?\)', clean_value)
                if match:
                    map_ref, key, default = match.groups()
                    # Try to resolve the map
                    map_value = self._resolve_value(map_ref)
                    if isinstance(map_value, dict) and key in map_value:
                        return map_value[key]
                    return default if default else value
            except:
                pass
            return value
        
        # Handle merge() function
        if clean_value.startswith("merge("):
            # merge(map1, map2, ...) - merge multiple maps
            try:
                import re
                # Extract arguments
                args_str = clean_value[6:-1]  # Remove "merge(" and ")"
                # Simple split by comma (doesn't handle nested commas)
                args = [arg.strip() for arg in args_str.split(",")]
                
                merged = {}
                for arg in args:
                    resolved = self._resolve_value(arg)
                    if isinstance(resolved, dict):
                        merged.update(resolved)
                
                return merged if merged else value
            except:
                pass
            return {}
        
        # Handle flatten() function
        if clean_value.startswith("flatten("):
            # flatten(list) - flatten nested lists
            try:
                arg = clean_value[8:-1]  # Remove "flatten(" and ")"
                resolved = self._resolve_value(arg)
                
                def flatten_list(lst):
                    result = []
                    for item in lst:
                        if isinstance(item, list):
                            result.extend(flatten_list(item))
                        else:
                            result.append(item)
                    return result
                
                if isinstance(resolved, list):
                    return flatten_list(resolved)
            except:
                pass
            return []
        
        # Handle zipmap() function
        if clean_value.startswith("zipmap("):
            # zipmap(keys, values) - create map from two lists
            try:
                import re
                match = re.match(r'zipmap\((.*?),\s*(.*?)\)', clean_value)
                if match:
                    keys_ref, values_ref = match.groups()
                    keys = self._resolve_value(keys_ref)
                    values = self._resolve_value(values_ref)
                    
                    if isinstance(keys, list) and isinstance(values, list):
                        return dict(zip(keys, values))
            except:
                pass
            return {}
        
        # Handle concat() function
        if clean_value.startswith("concat("):
            # concat(list1, list2, ...) - concatenate lists
            try:
                args_str = clean_value[7:-1]  # Remove "concat(" and ")"
                args = [arg.strip() for arg in args_str.split(",")]
                
                result = []
                for arg in args:
                    resolved = self._resolve_value(arg)
                    if isinstance(resolved, list):
                        result.extend(resolved)
                
                return result if result else []
            except:
                pass
            return []
        
        # Handle join() function  
        if clean_value.startswith("join("):
            # join(separator, list)
            try:
                import re
                match = re.match(r'join\("(.*?)",\s*(.*?)\)', clean_value)
                if match:
                    separator, list_ref = match.groups()
                    resolved_list = self._resolve_value(list_ref)
                    if isinstance(resolved_list, list):
                        return separator.join(str(x) for x in resolved_list)
            except:
                pass
            return "joined_value"
        
        # Handle split() function
        if clean_value.startswith("split("):
            # split(separator, string)
            try:
                import re
                match = re.match(r'split\("(.*?)",\s*"(.*?)"\)', clean_value)
                if match:
                    separator, string = match.groups()
                    return string.split(separator)
            except:
                pass
            return []
        
        # Handle tolist(), toset(), tomap()
        if clean_value.startswith("tolist("):
            arg = clean_value[7:-1]
            resolved = self._resolve_value(arg)
            return list(resolved) if not isinstance(resolved, list) else resolved
        
        if clean_value.startswith("toset("):
            arg = clean_value[6:-1]
            resolved = self._resolve_value(arg)
            return list(set(resolved)) if isinstance(resolved, list) else [resolved]
        
        if clean_value.startswith("tomap("):
            arg = clean_value[6:-1]
            resolved = self._resolve_value(arg)
            return dict(resolved) if not isinstance(resolved, dict) else resolved
        
        # Handle templatefile() function
        if clean_value.startswith("templatefile("):
            # templatefile(path, vars) - for now, return placeholder
            return "template_rendered"
        
        # Handle conditional: condition ? true_val : false_val
        if "?" in clean_value and ":" in clean_value:
            # Very naive parsing - just return the first option
            parts = clean_value.split("?")
            if len(parts) == 2:
                true_false = parts[1].split(":")
                if len(true_false) == 2:
                    # Return the "true" value (simplified)
                    return true_false[0].strip().strip('"')
        
        return value



    def _scan_for_edges(self, source_id: str, props: Dict, tf_id_map: Dict):
        """Recursively scan for references to known nodes."""
        for key, value in props.items():
            if isinstance(value, str):
                # Strip interpolation syntax
                clean_value = value
                if value.startswith("${") and value.endswith("}"):
                    clean_value = value[2:-1]
                
                # Check for terraform references
                for known_tf_ref, target_node_id in tf_id_map.items():
                    if source_id == target_node_id:
                        continue
                    
                    if known_tf_ref in clean_value:
                        interaction = "connects"
                        if "trigger" in key or "source" in key:
                            interaction = "trigger"
                        if "policy" in key:
                            interaction = "permissions"
                        
                        self.graph.add_edge(source_id, target_node_id, interaction)
                        
            elif isinstance(value, dict):
                self._scan_for_edges(source_id, value, tf_id_map)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._scan_for_edges(source_id, item, tf_id_map)

    def analyze_graph(self, graph: ArchitectureGraph):
        """Standard analysis."""
        findings = []
        
        # Structural Analysis
        cycles = graph.detect_cycles()
        if cycles:
            for cycle in cycles:
                findings.append(f"Cycle Detected: {' -> '.join(cycle)}")
        
        spofs = graph.detect_spof()
        if spofs:
            for node in spofs:
                findings.append(f"Potential SPOF: {node} has high fan-in.")
                
        bottlenecks = graph.detect_bottlenecks()
        if bottlenecks:
            for node in bottlenecks:
                findings.append(f"Bottleneck Detected: {node}")
        
        # Configuration Analysis
        config_issues = self._analyze_configurations(graph)
        findings.extend(config_issues)
                
        return findings
    
    def _analyze_configurations(self, graph: ArchitectureGraph) -> List[str]:
        """Analyze resource configurations for common issues."""
        issues = []
        
        for node_id, node in graph.nodes.items():
            props = node.properties
            
            # ========== LAMBDA CHECKS ==========
            if node.type == "lambda":
                # Performance
                timeout = props.get("timeout", 3)
                if isinstance(timeout, int) and timeout < 30:
                    issues.append(f"Config Issue: {node_id} has low timeout ({timeout}s), may cause premature failures")
                
                memory = props.get("memory_size", 128)
                if isinstance(memory, int) and memory < 512:
                    issues.append(f"Config Issue: {node_id} has low memory ({memory}MB), may cause OOM errors")
                
                # Security
                if "environment" in props:
                    env_vars = props.get("environment", {})
                    if isinstance(env_vars, list) and len(env_vars) > 0:
                        vars_dict = env_vars[0].get("variables", {}) if isinstance(env_vars[0], dict) else {}
                    elif isinstance(env_vars, dict):
                        vars_dict = env_vars.get("variables", {})
                    else:
                        vars_dict = {}
                    
                    # Check for hardcoded secrets
                    for key in vars_dict.keys():
                        if any(secret in key.lower() for secret in ["password", "secret", "api_key", "token"]):
                            issues.append(f"Security Issue: {node_id} may have hardcoded secrets in environment variable '{key}'")
                
                # Check for VPC configuration (security best practice)
                if "vpc_config" not in props or not props.get("vpc_config"):
                    issues.append(f"Security Issue: {node_id} is not deployed in a VPC")
                
                # Check for dead letter queue
                if "dead_letter_config" not in props:
                    issues.append(f"Reliability Issue: {node_id} does not have a dead letter queue configured")
            
            # ========== RDS CHECKS ==========
            elif node.type == "rds":
                # Security
                encrypted = props.get("storage_encrypted", False)
                if not encrypted:
                    issues.append(f"Security Issue: {node_id} does not have storage encryption enabled")
                
                # Check for public accessibility
                publicly_accessible = props.get("publicly_accessible", False)
                if publicly_accessible:
                    issues.append(f"Security Issue: {node_id} is publicly accessible")
                
                # Reliability
                backup_retention = props.get("backup_retention_period", 0)
                if isinstance(backup_retention, int) and backup_retention < 7:
                    issues.append(f"Reliability Issue: {node_id} has insufficient backup retention ({backup_retention} days)")
                
                # Availability
                multi_az = props.get("multi_az", False)
                if not multi_az:
                    issues.append(f"Availability Issue: {node_id} is not configured for Multi-AZ deployment")
                
                # Check for deletion protection
                deletion_protection = props.get("deletion_protection", False)
                if not deletion_protection:
                    issues.append(f"Data Protection Issue: {node_id} does not have deletion protection enabled")
                
                # Performance monitoring
                if "enabled_cloudwatch_logs_exports" not in props:
                    issues.append(f"Monitoring Issue: {node_id} does not export logs to CloudWatch")
            
            # ========== S3 CHECKS ==========
            elif node.type == "s3":
                # Data Protection
                versioning = props.get("versioning", {})
                if isinstance(versioning, dict):
                    enabled = versioning.get("enabled", False)
                    if not enabled:
                        issues.append(f"Data Protection Issue: {node_id} does not have versioning enabled")
                
                # Security
                server_side_encryption = props.get("server_side_encryption_configuration")
                if not server_side_encryption:
                    issues.append(f"Security Issue: {node_id} does not have server-side encryption configured")
                
                # Check for public access block
                if "public_access_block_configuration" not in props:
                    issues.append(f"Security Issue: {node_id} does not have public access block configured")
                
                # Check for logging
                if "logging" not in props:
                    issues.append(f"Compliance Issue: {node_id} does not have access logging enabled")
                
                # Check for lifecycle policies (cost optimization)
                if "lifecycle_rule" not in props:
                    issues.append(f"Cost Optimization: {node_id} does not have lifecycle policies configured")
            
            # ========== DYNAMODB CHECKS ==========
            elif node.type == "dynamodb":
                # Data Protection
                point_in_time_recovery = props.get("point_in_time_recovery", {})
                if isinstance(point_in_time_recovery, dict):
                    enabled = point_in_time_recovery.get("enabled", False)
                    if not enabled:
                        issues.append(f"Data Protection Issue: {node_id} does not have point-in-time recovery enabled")
                
                # Security
                server_side_encryption = props.get("server_side_encryption")
                if not server_side_encryption:
                    issues.append(f"Security Issue: {node_id} does not have encryption at rest enabled")
                
                # Performance
                billing_mode = props.get("billing_mode", "PROVISIONED")
                if billing_mode == "PROVISIONED":
                    if "autoscaling" not in props:
                        issues.append(f"Performance Issue: {node_id} uses provisioned capacity without autoscaling")
            
            # ========== EC2 CHECKS ==========
            elif node.type == "ec2":
                # Security
                if "vpc_security_group_ids" not in props:
                    issues.append(f"Security Issue: {node_id} does not have security groups configured")
                
                # Check for IMDSv2
                metadata_options = props.get("metadata_options", {})
                if isinstance(metadata_options, dict):
                    http_tokens = metadata_options.get("http_tokens", "optional")
                    if http_tokens != "required":
                        issues.append(f"Security Issue: {node_id} does not enforce IMDSv2")
                
                # Monitoring
                monitoring = props.get("monitoring", False)
                if not monitoring:
                    issues.append(f"Monitoring Issue: {node_id} does not have detailed monitoring enabled")
                
                # Check for EBS encryption
                if "ebs_block_device" in props:
                    ebs_devices = props["ebs_block_device"]
                    if isinstance(ebs_devices, list):
                        for device in ebs_devices:
                            if not device.get("encrypted", False):
                                issues.append(f"Security Issue: {node_id} has unencrypted EBS volume")
            
            # ========== SECURITY GROUP CHECKS ==========
            elif node.type == "sg":
                # Check for overly permissive ingress
                ingress_rules = props.get("ingress", [])
                if isinstance(ingress_rules, list):
                    for rule in ingress_rules:
                        cidr_blocks = rule.get("cidr_blocks", [])
                        if "0.0.0.0/0" in cidr_blocks:
                            from_port = rule.get("from_port", 0)
                            to_port = rule.get("to_port", 0)
                            if from_port != 80 and from_port != 443:
                                issues.append(f"Security Issue: {node_id} allows ingress from 0.0.0.0/0 on port {from_port}-{to_port}")
            
            # ========== ECS CHECKS ==========
            elif node.type == "ecs":
                # Check for task definition
                if "task_definition" not in props:
                    issues.append(f"Config Issue: {node_id} does not have a task definition")
                
                # Check for load balancer
                if "load_balancer" not in props:
                    issues.append(f"Availability Issue: {node_id} is not behind a load balancer")
                
                # Check desired count
                desired_count = props.get("desired_count", 1)
                if isinstance(desired_count, int) and desired_count < 2:
                    issues.append(f"Availability Issue: {node_id} has only {desired_count} task(s), consider increasing for HA")
            
            # ========== ALB/ELB CHECKS ==========
            elif node.type in ["alb", "elb"]:
                # Security
                if "access_logs" not in props:
                    issues.append(f"Compliance Issue: {node_id} does not have access logs enabled")
                
                # Check for HTTPS listeners
                listeners = props.get("listener", [])
                has_https = False
                if isinstance(listeners, list):
                    for listener in listeners:
                        if listener.get("protocol") == "HTTPS":
                            has_https = True
                
                if not has_https:
                    issues.append(f"Security Issue: {node_id} does not have HTTPS listeners configured")
            
            # ========== CLOUDFRONT CHECKS ==========
            elif node.type == "cloudfront":
                # Security
                default_cache_behavior = props.get("default_cache_behavior", {})
                if isinstance(default_cache_behavior, dict):
                    viewer_protocol_policy = default_cache_behavior.get("viewer_protocol_policy", "allow-all")
                    if viewer_protocol_policy == "allow-all":
                        issues.append(f"Security Issue: {node_id} allows HTTP traffic, should enforce HTTPS")
                
                # Check for WAF
                if "web_acl_id" not in props:
                    issues.append(f"Security Issue: {node_id} does not have WAF enabled")
                
                # Check for logging
                if "logging_config" not in props:
                    issues.append(f"Compliance Issue: {node_id} does not have logging enabled")
            
            # ========== ELASTICACHE CHECKS ==========
            elif node.type == "elasticache":
                # Security
                at_rest_encryption = props.get("at_rest_encryption_enabled", False)
                if not at_rest_encryption:
                    issues.append(f"Security Issue: {node_id} does not have encryption at rest enabled")
                
                transit_encryption = props.get("transit_encryption_enabled", False)
                if not transit_encryption:
                    issues.append(f"Security Issue: {node_id} does not have encryption in transit enabled")
                
                # Availability
                num_cache_nodes = props.get("num_cache_nodes", 1)
                if isinstance(num_cache_nodes, int) and num_cache_nodes < 2:
                    issues.append(f"Availability Issue: {node_id} has only {num_cache_nodes} node(s)")
            
            # ========== SQS CHECKS ==========
            elif node.type == "sqs":
                # Security
                if "kms_master_key_id" not in props:
                    issues.append(f"Security Issue: {node_id} does not use KMS encryption")
                
                # Check for dead letter queue
                if "redrive_policy" not in props:
                    issues.append(f"Reliability Issue: {node_id} does not have a dead letter queue configured")
            
            # ========== SNS CHECKS ==========
            elif node.type == "sns":
                # Security
                if "kms_master_key_id" not in props:
                    issues.append(f"Security Issue: {node_id} does not use KMS encryption")
            
            # ========== KINESIS CHECKS ==========
            elif node.type == "kinesis":
                # Security
                encryption_type = props.get("encryption_type", "NONE")
                if encryption_type == "NONE":
                    issues.append(f"Security Issue: {node_id} does not have encryption enabled")
                
                # Performance
                shard_count = props.get("shard_count", 1)
                if isinstance(shard_count, int) and shard_count < 2:
                    issues.append(f"Performance Issue: {node_id} has only {shard_count} shard(s), may cause throttling")
        
        return issues

